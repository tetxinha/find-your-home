# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class RightmoveItem(Item):
    # define the fields for your item here like:
    date = Field()
    title = Field()
    address = Field()
    price = Field()
    nearest_stations = Field()
    key_features = Field()
    long_description = Field()

