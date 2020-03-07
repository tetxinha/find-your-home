from rightmove.items import RightmoveItem

import scrapy
from rightmove.webscraper import WebLinks
from datetime import datetime as dt

list_links = WebLinks().get_list()


class HomesSpider(scrapy.Spider):
    name = "homes"
    start_urls = list_links

    def parse(self, response):
        home = response.css('div.property-header-bedroom-and-price')
        item = RightmoveItem()

        item['date'] = dt.today()
        item['title'] = home.css('h1.fs-22::text').extract()[0]
        item['address'] = home.css('address.grid-25::text').extract()[2]
        item['price'] = home.css('p.property-header-price strong::text').extract()[0]
        item['nearest_stations'] = home.xpath('//ul[@class="stations-list"]/li/span/text()').extract()
        item['key_features'] = home.xpath('//ul[@class="list-two-col list-style-square"]/li/text()').extract()
        item['long_description'] = home.xpath('//div[@class="sect "]/p/text()').extract()[0]

        yield item
