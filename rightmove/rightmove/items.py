# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class RightmoveItem(Item):
    # define the fields for your item here like:
    id = Field()
    date = Field()
    number_bedrooms = Field()
    price = Field()
    address = Field()
    nearest_station = Field()
    distance_to_station = Field()
    area = Field()
    borough = Field()
    zone = Field()
    furnished = Field()
    balcony = Field()
    garden = Field()
    refurbished = Field()


