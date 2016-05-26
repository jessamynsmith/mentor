import datetime
import dateutil.parser
from decimal import Decimal
import json
from optparse import make_option
import os
import pytz
from scrapy import FormRequest, Request
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess

from django.core.management.base import NoArgsCommand
from django.db import IntegrityError
from django.db.models import Q

from codementor import models as codementor_models


# TODO get client timezone, username, other fields?


class PayoutSpider(Spider):
    name = "payout"
    allowed_domains = ["codementor.io"]
    start_urls = [
        "https://www.codementor.io/users/sign_in"
    ]
    known_timezones = {
        'Pacific Time': 'US/Pacific',
        'Mountain Time': 'US/Mountain',
        'Central Time': 'US/Central',
        'Eastern Time': 'US/Eastern',
    }

    def __init__(self, **kwargs):
        super(PayoutSpider, self).__init__()
        self.username = os.environ['CODEMENTOR_USERNAME']
        self.password = os.environ['CODEMENTOR_PASSWORD']

    def parse(self, response):
        login_form = {
            'login': self.username,
            'password': self.password,
        }
        return FormRequest.from_response(
            response,
            formdata=login_form,
            callback=self.after_login
        )

    def after_login(self, response):
        # If login failed, error out
        profile_link = "<a href='/%s'>" % self.username
        if profile_link not in response.body:
            self.logger.error("Login failed")
            return

        return Request(
            "https://www.codementor.io/%s" % self.username,
            callback=self.parse_timezone_and_reviews
        )

    def parse_timezone_and_reviews(self, response):
        timezone_div = response.xpath('//div[contains(@class, "timezone")]')
        timezone_text = timezone_div.xpath('./text()').extract()[1]
        timezone_name = timezone_text.split('(')[0].strip()
        self.timezone = pytz.timezone(self.known_timezones[timezone_name])

        reviews = response.xpath('//div[contains(@class, "reviewModule")]')
        for review in reviews:
            review_info_text = review.xpath('./div[contains(@class, "reviewerName")]/span/text()')
            review_info = review_info_text.extract()
            reviewer_name = review_info[0].strip()
            review_date = self.parse_date(review_info[1])
            review_content_text = review.xpath('./div[contains(@class, "content")]/div/text()')
            review_content = review_content_text.extract()[0].strip()

            client = self.get_or_create_client(reviewer_name, review_date)
            self.get_or_create_review(client, review_date, review_content)

        return Request(
            # HACK! Set the page number very high so as to retrieve all history
            "https://www.codementor.io/templates/finished-sessions.html?page=100",
            callback=self.parse_sessions
        )

    def clean_client_name(self, client_name):
        return client_name.replace('Session with', '').replace('(refunded)', '').strip()

    def parse_sessions(self, response):
        sessions = response.xpath('//li[contains(@class, "question-header")]')
        for session in sessions:
            session_info = session.xpath('./div/div[contains(@class, "content")]')
            client_name_text = session_info.xpath('./h4/text()').extract()[0]
            client_name = self.clean_client_name(client_name_text)

            time_text = session_info.xpath('./p[contains(@class, "muted")]/text()').extract()[1]
            time_pieces = time_text.split('\n')
            finished_at = self.parse_date(time_pieces[2])
            session_length = self.parse_length(time_pieces[4].replace('Length:', ''))
            started_at = finished_at - datetime.timedelta(minutes=session_length)

            confirm_links = session.xpath('./div[contains(@class, "confirm")]/div/div/a')
            chat_click = confirm_links[2].xpath('./@ng-click').extract()[0]
            chat_data = chat_click[chat_click.find('(')+1:chat_click.find(')')]
            chat_data = json.loads(chat_data.replace("'", '"'))
            username = chat_data['contact']['username']

            client = self.get_or_create_client(client_name, started_at, username)

            review = None

            review_div = session.xpath('./div[contains(@class, "confirm")]/div/div/'
                                       'div[contains(@class, "ng-non-bindable")]')
            if review_div:
                review_content = review_div.xpath('./text()').extract()[0].strip()
                review = self.get_or_create_review(client, finished_at, review_content)

            self.get_or_create_session(client, started_at, session_length, review)

        return Request(
            "https://www.codementor.io/users/payout_history",
            callback=self.parse_payouts
        )

    def parse_length(self, length_text):
        length_text = length_text.strip()
        if length_text == "0 secs":
            return 0
        length = dateutil.parser.parse(length_text)
        length_seconds = length.hour * 60 * 60 + length.minute * 60 + length.second
        return int(round(length_seconds / 60.0))

    def parse_date(self, date_text):
        payment_date = None
        try:
            naive_date = dateutil.parser.parse(date_text.strip())
            local_date = self.timezone.localize(naive_date)
            payment_date = local_date.astimezone(pytz.UTC)
        except ValueError:
            self.logger.warning("Cannot parse date: '%s'" % date_text.strip())
        return payment_date

    def parse_amount(self, amount_text):
        return Decimal(amount_text.strip().replace('$', '').replace(',', ''))

    def parse_payment_type(self, length_or_type_text):
        length_or_type_text = length_or_type_text.strip()
        payment_type = codementor_models.PaymentType.SESSION
        if length_or_type_text == "Offline Help":
            payment_type = codementor_models.PaymentType.OFFLINE_HELP
        elif length_or_type_text.find("Monthly") > 0:
            payment_type = codementor_models.PaymentType.MONTHLY

        return payment_type

    def has_free_preview(self, payment_div):
        free_preview = False
        free_text = payment_div.xpath('./div/text()').extract()
        if len(free_text) > 0:
            free_preview = True
        return free_preview

    def get_or_create_client(self, client_name, started_at, username=None):
        clients = codementor_models.Client.objects.filter(name=client_name)
        if username:
            clients = clients.filter(Q(username=username) | Q(username__isnull=True))
        if clients.count() > 0:
            # TODO how to figure out which client is correct if there is more than one?
            client = clients[0]
        else:
            client = codementor_models.Client(name=client_name, username=username)

        if not client.username:
            client.username = username
        if not client.started_at or started_at < client.started_at:
            client.started_at = started_at
        client.save()
        return client

    def get_or_create_review(self, client, review_date, content):
        # Can't use get_or_create here because dates show up slightly differently between the
        # sessions page and the reviews page.
        reviews = codementor_models.Review.objects.filter(reviewer=client, content=content)
        if reviews.count() > 0:
            review = reviews[0]
        else:
            review = codementor_models.Review(reviewer=client, date=review_date, content=content)
            review.save()
        return review

    def get_or_create_session(self, client, started_at, length, review):
        session, created = codementor_models.Session.objects.get_or_create(
            client=client, started_at=started_at, length=length)
        if created:
            session.review = review
            try:
                session.save()
            except IntegrityError as e:
                # Occurs if there are two reviews with the same text -- if so, just make a new one
                if str(e).find('Key (review_id)') > 0:
                    review = codementor_models.Review(reviewer=client, date=session.started_at,
                                                      content=review.content)
                    review.save()
                    session.review = review
                    session.save()
        return session

    def get_or_create_payment(self, payment_div, payment_date, client_name, earnings_amount,
                              length_or_type_text, payout=None):
        client = self.get_or_create_client(client_name, payment_date)
        payment, created = codementor_models.Payment.objects.get_or_create(
            date=payment_date, client=client, earnings=earnings_amount)
        if created:
            payment.free_preview = self.has_free_preview(payment_div)
            payment.type = self.parse_payment_type(length_or_type_text)
            payment.payout = payout
            payment.save()
        return payment

    def parse_payments(self, payout, payout_data):
        payments = payout_data.xpath('./div[contains(@class, "panel-collapse")]/div'
                                     '/div[@class="row-fluid"]')
        total_earnings = Decimal('0')
        for payment in payments:
            payment_div = payment.xpath('./div/div[@class="info_padding"]')
            payment_info = payment_div.xpath('./text()').extract()
            payment_date = self.parse_date(payment_info[0])
            client_name = self.clean_client_name(payment_info[1])
            length_or_type_text = payment_info[2]

            # Sessions with 15min free have an extra div inserted, so earnings are offset by 1
            earnings_amount = payment_info[3].strip()
            if not earnings_amount:
                earnings_amount = payment_info[4].strip()
            earnings_amount = self.parse_amount(earnings_amount)

            payment = self.get_or_create_payment(payment_div, payment_date, client_name,
                                                 earnings_amount, length_or_type_text, payout)
            total_earnings += payment.earnings

        payout.total_earnings = total_earnings
        payout.save()

    def parse_pending_payments(self, response):
        pending_payments = response.xpath('//div[contains(@class, "pending_list")]')

        for payment_data in pending_payments:
            payment_div = payment_data.xpath('./div/div/div/div[contains(@class, "lesson_info")]')
            payment_info = payment_div.xpath('./text()').extract()
            payment_date = self.parse_date(payment_info[0])
            if not payment_date:
                continue
            client_name = self.clean_client_name(payment_info[1])

            if len(payment_info) < 4:
                # For offline help payments, there is no length and amount is at index 2
                length_or_type_text = "Offline Help"
                earnings_amount = payment_info[2]
            else:
                # For sessions, length is at index 2 and amount is after
                length_or_type_text = payment_info[2]
                earnings_amount = payment_info[3].strip()
                # Sessions with 15min free have an extra div inserted, so earnings are offset by 1
                if not earnings_amount:
                    earnings_amount = payment_info[4].strip()
            earnings_amount = self.parse_amount(earnings_amount)
            tips_div = payment_div.xpath('./*[@id="tips"]')
            if tips_div:
                tips = tips_div.xpath('./text()').extract()
                if not tips[0].find(u'review'):
                    tip_text = tips[0].split(' ')[1]
                    tip_amount = self.parse_amount(tip_text.split(')')[0])
                    earnings_amount += tip_amount

            self.get_or_create_payment(payment_div, payment_date, client_name, earnings_amount,
                                       length_or_type_text)

    def parse_payouts(self, response):
        self.parse_pending_payments(response)

        payouts = response.xpath('//div[@id="paid_panel"]/div[contains(@class, "customize_panel")]')
        for payout_data in payouts:
            payout_info_text = payout_data.xpath('./div/a/div[contains(@class, "fluid")]/'
                                                 'div/div[contains(@class, "info")]/text()')
            payout_info = payout_info_text.extract()
            payout_date = self.parse_date(payout_info[2])
            payout_method = getattr(codementor_models.PayoutMethod, payout_info[3].strip().upper())
            payout_amount = self.parse_amount(payout_info[5])

            existing_payouts = codementor_models.Payout.objects.filter(date=payout_date)
            if existing_payouts.count() == 0:
                payout = codementor_models.Payout(
                    date=payout_date, method=payout_method, amount=payout_amount)
                payout.save()
            else:
                payout = existing_payouts[0]
            self.parse_payments(payout, payout_data)


class Command(NoArgsCommand):
    help = 'Scrape payout information from codementor and store locally'

    option_list = NoArgsCommand.option_list + (
        make_option('--delete', action='store_true', dest='delete', default=False,
                    help='Delete data before scraping.'),
    )

    def handle(self, *args, **options):
        delete = options.get('delete')
        if delete:
            codementor_models.Review.objects.all().delete()
            codementor_models.Session.objects.all().delete()
            codementor_models.Payout.objects.all().delete()
            codementor_models.Payment.objects.all().delete()

        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
        })

        process.crawl(PayoutSpider)
        process.start()
