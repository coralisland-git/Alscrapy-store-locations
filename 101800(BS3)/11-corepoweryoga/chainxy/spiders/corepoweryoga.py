import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from selenium import webdriver
from lxml import html
import pdb

class BS3Corepoweryoga(scrapy.Spider):
	name = 'corepoweryoga'
	domain = 'https://www.corepoweryoga.com'
	history = []

	def start_requests(self):

		init_url  = 'https://d7mth1zoj92fj.cloudfront.net/data/all-locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = json.loads(response.body)
		for cnt in range(0, len(store_list)-1):
			store = store_list[str(cnt)]
			detail_link = 'https://d7mth1zoj92fj.cloudfront.net/data/content' + store['path']
			yield scrapy.Request(url=detail_link, callback=self.parse_detail)

	def parse_detail(self, response):
		detail = json.loads(response.body)
		item = ChainItem()
		item['store_name'] = detail['metatags']['title'].split('|')[0].strip()
		item['store_number'] = ''
		item['address'] = detail['field_address_1']['und'][0]['value']
		try:
			item['address2'] = detail['field_address_2']['und'][0]['value']
		except:
			pass
		item['city'] = detail['field_city']['und'][0]['value']
		item['state'] = detail['field_studio_state']['und'][0]['value']
		item['zip_code'] = detail['field_zip_code']['und'][0]['value']
		item['country'] = detail['field_country']['und'][0]['value']
		item['phone_number'] = detail['field_phone']['und'][0]['value']
		geolocation = detail['field_location']['und'][0]['geom'].split('(')[1].strip()[:-1].split(' ')
		item['latitude'] = geolocation[0]
		item['longitude'] = geolocation[1]
		item['store_hours'] = ''
		item['store_type'] = ''
		item['other_fields'] = ''
		item['coming_soon'] = ''
		yield item	

	def validate(self, item):
		try:
			return item.strip().replace('\n', '').replace('&#8211', '-').replace(';','')
		except:
			return ''