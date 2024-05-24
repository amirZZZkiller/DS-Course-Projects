# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SocialbladeItem(scrapy.Item):
    socialblade_url = scrapy.Field()
    channel_name = scrapy.Field()
    channel_id = scrapy.Field()
    channel_link = scrapy.Field()
    uploads = scrapy.Field()
    subscribers = scrapy.Field()
    views = scrapy.Field()
    country = scrapy.Field()
    channel_type = scrapy.Field()
    created_date = scrapy.Field()
    social_blade_rank = scrapy.Field()
    subscriber_rank = scrapy.Field()
    video_view_rank = scrapy.Field()
    country_rank = scrapy.Field()
    people_rank = scrapy.Field()
    estimated_monthly_income = scrapy.Field()
    subscribers_last_30_days = scrapy.Field()
    views_last_30_days = scrapy.Field()
    yearly_income = scrapy.Field()
    daily_subs_average = scrapy.Field()
    daily_views_average = scrapy.Field()
