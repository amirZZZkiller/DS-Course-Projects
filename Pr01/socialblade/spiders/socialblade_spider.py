# socialblade_spider.py
import scrapy
from scrapy.http import Request
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError
from socialblade.items import SocialbladeItem
import time
import random

class SocialbladeSpiderSpider(scrapy.Spider):
    name = "socialblade_spider"
    allowed_domains = ["socialblade.com"]
    headers = {
        "authority": "socialblade.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "referer": "https://socialblade.com/",
        "sec-ch-ua": "\"Chromium\";v=\"118\", \"Microsoft Edge\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46"
    }

    cookies = {
        "PHPSESSXX": "a8bmd0nc46abkel74urrlbonpj"
    }

    country_codes = ['us', 'au', 'gb', 'ca', 'de', 'fr', 'af', 'be', 'fi', 'in', 'ru', 'ng', 'ne', 'qa', 'ir', 'kr', 'cn', 'it', 'lu', 'jp', 'pl', 'sa', 'il', 'br', 'ar', 'at']

    def start_requests(self):
        for code in self.country_codes:
            url = f'https://socialblade.com/youtube/top/country/{code}'
            self.logger.info(f"Scraping the Country of {code}")
            yield scrapy.Request(
                url=url,
                headers=self.headers,
                cookies=self.cookies,
                callback=self.parse_country,
                errback=self.errback_httpbin
            )

    def parse_country(self, response):
        links = response.xpath('//a[contains(@href , "/youtube/c")]/@href').getall()
        for link in links:
            yield scrapy.Request(
                url='https://socialblade.com' + link,
                headers=self.headers,
                cookies=self.cookies,
                callback=self.parse_details,
                errback=self.errback_httpbin
            )
            time.sleep(random.uniform(1, 3))  # Add a random delay between 1 and 3 seconds

    def parse_details(self, response):
        item = SocialbladeItem()
        item['socialblade_url'] = response.url

        item['channel_name'] = response.xpath('//div[@id="YouTubeUserTopInfoBlockTop"]//h1[1]/text()').get(default='N/A')
        item['channel_id'] = response.xpath('//div[@id="YouTubeUserTopInfoBlockTop"]//h4[1]//text()').get(default='N/A')

        if item['channel_id'] != 'N/A':
            item['channel_link'] = 'https://youtube.com/' + item['channel_id']
        else:
            self.logger.error(f"Channel ID is missing for {response.url}")
            item['channel_link'] = None

        item['uploads'] = response.xpath('//span[@id="youtube-stats-header-uploads"]/text()').get(default='N/A')
        item['subscribers'] = response.xpath('//span[@id="youtube-stats-header-subs"]/text()').get(default='N/A')
        item['views'] = response.xpath('//span[@id="youtube-stats-header-views"]/text()').get(default='N/A')
        item['country'] = response.xpath('//span[@id="youtube-stats-header-country"]/text()').get(default='N/A')
        item['channel_type'] = response.xpath('//span[@id="youtube-stats-header-channeltype"]/text()').get(default='N/A')
        item['created_date'] = response.xpath('//span[contains(text(), "User Created")]/following-sibling::span[1]/text()').get(default='N/A')

        table_data = response.xpath('//p/span[@class="hint--top"]/text()').getall()
        item['social_blade_rank'] = table_data[0].strip() if len(table_data) > 0 else 'N/A'
        item['subscriber_rank'] = table_data[1].strip() if len(table_data) > 1 else 'N/A'
        item['video_view_rank'] = table_data[2].strip() if len(table_data) > 2 else 'N/A'
        item['country_rank'] = table_data[3].strip() if len(table_data) > 3 else 'N/A'
        item['people_rank'] = table_data[4].strip() if len(table_data) > 4 else 'N/A'

        item['estimated_monthly_income'] = response.xpath('//p[contains(text(), "Estimated Monthly Earnings ")]/preceding-sibling::p/text()').get(default='N/A').replace('\xa0', '').strip()
        item['subscribers_last_30_days'] = response.xpath('//p[contains(text(), "Subscribers for the last 30 days")]/preceding-sibling::p/text()').get(default='N/A').strip()
        item['views_last_30_days'] = response.xpath('//p[contains(text(), "Video Views for the last 30 days")]/preceding-sibling::p/text()').get(default='N/A').strip()
        item['yearly_income'] = response.xpath('//p[contains(text(), "Estimated Yearly Earnings")]/preceding-sibling::p/text()').get(default='N/A').strip().replace('\xa0', '')

        item['daily_subs_average'] = response.xpath('//div[@id="averagedailysubs"]/span/text()').get(default='N/A')
        item['daily_views_average'] = response.xpath('//div[@id="averagedailyviews"]/span/text()').get(default='N/A')

        yield item

    def errback_httpbin(self, failure):
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
