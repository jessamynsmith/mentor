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

    # TODO parse payments not yet attached to a payout

    def parse_payments(self, payout, payout_data):
        payments = payout_data.xpath('./div[contains(@class, "panel-collapse")]/div'
                                     '/div[@class="row-fluid"]')
        total_earnings = Decimal('0')
        for payment in payments:
            payment_info_div = payment.xpath('./div/div[@class="info_padding"]')
            payment_info = payment_info_div.xpath('./text()').extract()
            payment_date = dateutil.parser.parse(payment_info[0].strip()).date()
            client_name = payment_info[1].strip()

            # For some reason, sometimes earnings are at index 3, sometimes at index 4
            earnings_amount = payment_info[3].strip()
            if not earnings_amount:
                earnings_amount = payment_info[4].strip()
            earnings = Decimal(earnings_amount.replace('$', '').replace(',', ''))
            total_earnings += earnings

            existing_payments = codementor_models.Payment.objects.filter(date=payment_date,
                                                                         client__name=client_name,
                                                                         earnings=earnings)
            if existing_payments.count() == 0:
                # This will group payments by people with the same display name
                client, created = codementor_models.Client.objects.get_or_create(name=client_name)
                if created:
                    client.save()
                payment = codementor_models.Payment(payout=payout,
                                                    date=payment_date,
                                                    client=client,
                                                    earnings=earnings)

                free_text = payment_info_div.xpath('./div/text()').extract()
                if len(free_text) > 0:
                    payment.free_preview = True

                length_or_type = payment_info[2].strip()
                if length_or_type == "Offline Help":
                    payment.type = codementor_models.PaymentType.OFFLINE_HELP
                elif length_or_type.find("Monthly") > 0:
                    payment.type = codementor_models.PaymentType.MONTHLY
                else:
                    length = dateutil.parser.parse(length_or_type)
                    payment.length = length.hour * 60 * 60 + length.minute * 60 + length.second

                payment.save()

            payout.total_earnings = total_earnings
            payout.save()

    def parse_payouts(self, response):
        payouts = response.xpath('//div[@id="paid_panel"]/div[contains(@class, "customize_panel")]')
        for payout_data in payouts:
            payout_info_text = payout_data.xpath('./div/a/div[contains(@class, "fluid")]/'
                                            'div/div[contains(@class, "info")]/text()')
            payout_info = payout_info_text.extract()
            payout_date = dateutil.parser.parse(payout_info[2].strip()).date()
            payout_method = codementor_models.PayoutMethod.get(payout_info[3].strip().upper()).value
            payout_amount = Decimal(payout_info[5].strip().replace('$', '').replace(',', ''))

            existing_payouts = codementor_models.Payout.objects.filter(date=payout_date)
            if existing_payouts.count() == 0:
                payout = codementor_models.Payout(date=payout_date,
                                                  method=payout_method,
                                                  amount=payout_amount)
                payout.save()
                self.parse_payments(payout, payout_data)


class Command(NoArgsCommand):
    help = 'Scrape payouts from codementor and store locally'

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
