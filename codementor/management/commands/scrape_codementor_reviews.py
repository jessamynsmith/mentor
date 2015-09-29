import dateutil.parser
from optparse import make_option
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess

from django.core.management.base import NoArgsCommand

from codementor import models as codementor_models


class ReviewSpider(Spider):
    name = "review"
    allowed_domains = ["codementor.io"]
    start_urls = [
        "https://www.codementor.io/jessamynsmith"
    ]

    def parse(self, response):
        reviews = response.xpath('//div[contains(@class, "reviewModule")]')
        for review in reviews:
            review_info_text = review.xpath('./div[contains(@class, "reviewerName")]/span/text()')
            review_info = review_info_text.extract()
            reviewer_name = review_info[0]
            review_date = dateutil.parser.parse(review_info[1]).date()
            review_content_text = review.xpath('./div[contains(@class, "content")]/text()')
            review_content = review_content_text.extract()[0].strip()
            existing_reviews = codementor_models.Review.objects.filter(reviewer__name=reviewer_name,
                                                                       date=review_date,
                                                                       content=review_content)
            if existing_reviews.count() == 0:
                # This will group reviews by people with the same display name
                reviewer, _ = codementor_models.Client.objects.get_or_create(name=reviewer_name)
                reviewer.save()
                review = codementor_models.Review(reviewer=reviewer,
                                                  date=review_date,
                                                  content=review_content)
                review.save()


class Command(NoArgsCommand):
    help = 'Scrape reviews from codementor and store locally'

    option_list = NoArgsCommand.option_list + (
        make_option('--delete', action='store_true', dest='delete', default=False,
                    help='Delete data before scraping.'),
    )

    def handle(self, *args, **options):
        delete = options.get('delete')
        if delete:
            codementor_models.Client.objects.filter(reviews__isnull=False).delete()
            codementor_models.Review.objects.all().delete()

        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
        })

        process.crawl(ReviewSpider)
        process.start()
