import dateutil.parser
from decimal import Decimal
from optparse import make_option
import os
from scrapy import FormRequest, Request
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess

from django.core.management.base import NoArgsCommand

from codementor import models as codementor_models


class PayoutSpider(Spider):
    name = "payout"
    allowed_domains = ["codementor.io"]
    start_urls = [
        "https://www.codementor.io/users/sign_in"
    ]

    def parse(self, response):
        login_form = {
            'login': os.environ.get('CODEMENTOR_USERNAME'),
            'password': os.environ.get('CODEMENTOR_PASSWORD'),
        }
        return FormRequest.from_response(
            response,
            formdata=login_form,
            callback=self.after_login
        )

    def after_login(self, response):
        # If login failed, error out
        if "Jessamyn Smith" not in response.body:
            self.logger.error("Login failed")
            return

        return Request(
            "https://www.codementor.io/users/payout_history",
            callback=self.parse_payouts
        )

    def parse_date(self, date_text):
        payment_date = None
        try:
            payment_date = dateutil.parser.parse(date_text.strip()).date()
        except ValueError:
            print("Cannot parse date: '%s'" % date_text.strip())
        return payment_date

    def parse_amount(self, amount_text):
        return Decimal(amount_text.strip().replace('$', '').replace(',', ''))

    def parse_length_and_type(self, length_or_type_text):
        length_or_type_text = length_or_type_text.strip()
        payment_type = codementor_models.PaymentType.SESSION
        payment_length = None
        if length_or_type_text == "Offline Help":
            payment_type = codementor_models.PaymentType.OFFLINE_HELP
        elif length_or_type_text.find("Monthly") > 0:
            payment_type = codementor_models.PaymentType.MONTHLY
        else:
            length = dateutil.parser.parse(length_or_type_text)
            length_seconds = length.hour * 60 * 60 + length.minute * 60 + length.second
            payment_length = int(round(length_seconds/60.0))
        return payment_length, payment_type

    def has_free_preview(self, payment_div):
        # TODO verify that free preview detection works for pending payments
        free_preview = False
        free_text = payment_div.xpath('./div/text()').extract()
        if len(free_text) > 0:
            free_preview = True
        return free_preview

    def get_or_create_payment(self, payment_div, payment_date, client_name, earnings_amount,
                              length_or_type_text):
        earnings = self.parse_amount(earnings_amount)
        try:
            payment = codementor_models.Payment.objects.get(date=payment_date,
                                                            client__name=client_name,
                                                            earnings=earnings)
        except codementor_models.Payment.DoesNotExist:
            # This will group payments by people with the same display name
            client, created = codementor_models.Client.objects.get_or_create(name=client_name)
            if created:
                client.save()
            payment = codementor_models.Payment(date=payment_date,
                                                client=client,
                                                earnings=earnings)

        payment.free_preview = self.has_free_preview(payment_div)
        payment.length, payment.type = self.parse_length_and_type(length_or_type_text)
        return payment

    def parse_payments(self, payout, payout_data):
        payments = payout_data.xpath('./div[contains(@class, "panel-collapse")]/div'
                                     '/div[@class="row-fluid"]')
        total_earnings = Decimal('0')
        for payment in payments:
            payment_div = payment.xpath('./div/div[@class="info_padding"]')
            payment_info = payment_div.xpath('./text()').extract()
            payment_date = self.parse_date(payment_info[0])
            client_name = payment_info[1].strip()
            length_or_type_text = payment_info[2]

            # For offline payments earnings are at index 3, for sessions they are at index 4
            earnings_amount = payment_info[3].strip()
            if not earnings_amount:
                earnings_amount = payment_info[4].strip()

            payment = self.get_or_create_payment(payment_div, payment_date, client_name,
                                                 earnings_amount, length_or_type_text)
            payment.payout = payout
            payment.save()
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
            client_name = payment_info[1].strip()

            if len(payment_info) == 4:
                # For sessions, length is at index 2 and amount is at index 3
                length_or_type_text = payment_info[2]
                earnings_amount = payment_info[3]
            else:
                # For offline help payments, there is no length and amount is at index 2
                length_or_type_text = "Offline Help"
                earnings_amount = payment_info[2]

            payment = self.get_or_create_payment(payment_div, payment_date, client_name,
                                                 earnings_amount, length_or_type_text)
            payment.save()

    def parse_payouts(self, response):
        self.parse_pending_payments(response)

        payouts = response.xpath('//div[@id="paid_panel"]/div[contains(@class, "customize_panel")]')
        for payout_data in payouts:
            payout_info_text = payout_data.xpath('./div/a/div[contains(@class, "fluid")]/'
                                                 'div/div[contains(@class, "info")]/text()')
            payout_info = payout_info_text.extract()
            payout_date = self.parse_date(payout_info[2])
            payout_method = codementor_models.PayoutMethod.get(payout_info[3].strip().upper()).value
            payout_amount = self.parse_amount(payout_info[5])

            existing_payouts = codementor_models.Payout.objects.filter(date=payout_date)
            if existing_payouts.count() == 0:
                payout = codementor_models.Payout(date=payout_date,
                                                  method=payout_method,
                                                  amount=payout_amount)
                payout.save()
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
            codementor_models.Client.objects.filter(payments__isnull=False).delete()
            codementor_models.Payment.objects.all().delete()
            codementor_models.Payout.objects.all().delete()

        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
        })

        process.crawl(PayoutSpider)
        process.start()
