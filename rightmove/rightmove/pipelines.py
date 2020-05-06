# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import json
import logging

import pymongo
import requests
from scrapy.exceptions import DropItem


class RightmovePipeline(object):

    collection_name = 'rightmove'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.ids_seen = set()

    @classmethod
    def from_crawler(cls, crawler):
        # pull in information from settings.py
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        # initializing spider
        # opening db connection
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        # clean up when spider is closed
        self.client.close()

    def process_item(self, item, spider):
        # how to handle each post
        # ---------- ID ----------
        item['id'] = ''.join(i for i in item['id'] if i.isdigit())

        if item['id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            # ---------- ID ----------
            self.ids_seen.add(item['id'])
            # ---------- NUMBER BEDROOMS ----------
            title = item['number_bedrooms']
            first_word_title = title.split()[0].lower()
            if first_word_title == '1' or first_word_title == 'one':
                number_bedrooms = 1
            elif first_word_title == '2' or first_word_title == 'two':
                number_bedrooms = 2
            elif first_word_title == 'studio':
                number_bedrooms = 0
            else:
                number_bedrooms = 3
            item['number_bedrooms'] = number_bedrooms
            # ---------- PRICE ----------
            item['price'] = item['price'].strip()
            splitted_string = item['price'].split(' ')
            if item['price'][-2:] == 'pw':
                value = ''.join(i for i in item['price'] if i.isdigit())
                item['price'] = round((float(value) * 52) / 12, 2)
            elif item['price'][-3:] == 'pcm':
                value = ''.join(i for i in item['price'] if i.isdigit())
                item['price'] = float(value)
            else:
                if 'pcm' in splitted_string:
                    index_pcm = splitted_string.index('pcm')
                    value = ''.join(i for i in splitted_string[index_pcm-1] if i.isdigit())
                    item['price'] = float(value)
                elif 'pw' in splitted_string:
                    index_pw = splitted_string.index('pw')
                    value = ''.join(i for i in splitted_string[index_pw - 1] if i.isdigit())
                    item['price'] = round((float(value) * 52) / 12, 2)
                else:
                    item['price'] = 1500
            # ---------- ADDRESS ----------
            item['address'] = " ".join(item['address'].split())
            item['address'] = item['address'].lower()
            item['address'] = item['address'] + ' london' if 'london' not in item['address'] else item['address']
            # ---------- DISTANCE STATION ----------
            item['distance_to_station'] = item['distance_to_station'].replace("(", "")
            item['distance_to_station'] = float(item['distance_to_station'].split(" ")[0])
            # ---------- AREA ----------
            item['area'] = item['area'][0]
            # ---------- BOROUGH ----------
            item['borough'] = item['borough'][1]
            # ---------- ZONE ----------
            item['zone'] = item['zone'][3] if len(item['zone']) == 4 else item['zone'][2]
            # ---------- FURNISHED ----------
            furnished_message = item['furnished']
            if furnished_message == 'Furnished':
                furnished = 1
            elif furnished_message == 'Unfurnished':
                furnished = 0
            elif furnished_message == 'Part-furnished':
                furnished = 2
            else:
                furnished = 4
            item['furnished'] = furnished
            # ---------- BALCONY/GARDEN/REFURBISHED ----------
            key_features = item['balcony']
            long_desc = item['garden'].strip().lower()
            balcony = 0
            garden = 0
            refurbished = 0
            for feature in key_features:
                feature_lower = feature.lower()
                balcony = 1 if 'balcony' in feature_lower \
                               or 'terrace' in feature_lower \
                               or 'deck' in feature_lower else 0
                garden = 1 if 'garden' in feature_lower else 0
                refurbished = 1 if 'refurbished' in feature_lower \
                                   or 'modern' in feature_lower \
                                   or 'renovated' in feature_lower else 0
            if balcony == 0:
                balcony = 1 if 'balcony' in long_desc \
                               or 'terrace' in long_desc \
                               or 'deck' in long_desc else 0
            if garden == 0:
                garden = 1 if 'garden' in long_desc else 0
            if refurbished == 0:
                refurbished = 1 if 'refurbished' in long_desc \
                                   or 'modern' in long_desc \
                                   or 'renovated' in long_desc else 0
            item['balcony'] = balcony
            item['garden'] = garden
            item['refurbished'] = refurbished
            self.db[self.collection_name].insert(dict(item))
            logging.debug("Post added to MongoDB")
            return item