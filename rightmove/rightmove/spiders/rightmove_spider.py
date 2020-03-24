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
        item['id'] = response.url
        item['date'] = dt.today()
        item['number_bedrooms'] = home.css('h1.fs-22::text').extract()[0]
        item['price'] = home.css('p.property-header-price strong::text').extract()[0]
        item['address'] = home.css('address.grid-25::text').extract()[2]
        item['nearest_station'] = home.xpath('//ul[@class="stations-list"]/li/span/text()').extract_first()
        item['distance_to_station'] = home.xpath('//ul[@class="stations-list"]/li/small/text()').extract_first()
        item['area'] = home.xpath('//ul[@class="list-bdr-b"]/li/a/text()').extract()
        item['borough'] = home.xpath('//ul[@class="list-bdr-b"]/li/a/text()').extract()
        item['zone'] = home.xpath('//ul[@class="list-bdr-b"]/li/a/text()').extract()
        item['coordinates'] = ''
        item['time_to_center'] = 0
        item['furnished'] = home.xpath('//table[@class="table-reset width-100"]/tbody/tr/td[@id="furnishedType"]/text()'
                                       ).extract_first()
        item['balcony'] = home.xpath('//ul[@class="list-two-col list-style-square"]/li/text()').extract()  # key_features
        item['garden'] = home.xpath('//div[@class="sect "]/p/text()').extract()[0]  # long_description
        item['refurbished'] = 0

        yield item
