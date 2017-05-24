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
import usaddress

class wrfc(scrapy.Spider):
	name = 'wrfc'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.centerracoop.com/wp-admin/admin-ajax.php'
		formdata = {
			'action':'vc_get_vc_grid_data',
			'vc_action':'vc_get_vc_grid_data',
			'tag':'vc_basic_grid',
			'data[visible_pages]':'5',
			'data[page_id]':'1384',
			'data[style]':'all',
			'data[action]':'vc_get_vc_grid_data',
			'data[shortcode_id]':'1490362157540-0f62bca1-8761-5',
			'data[tag]':'vc_basic_grid',
			'vc_post_id':'1384',
			'_vcnonce':'eafca32a9c'
		}
		header = {
			'Accept':'text/html, */*; q=0.01',
			'Accept-Encoding':'gzip, deflate',
			'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
			'X-Requested-With':'XMLHttpRequest'
		}
		yield scrapy.FormRequest(url=init_url, formdata=formdata, method='POST', headers=header,callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")

		store_list = response.xpath('//a[contains(@class, "vc_gitem-link vc_single_image-wrapper")]/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			detail = self.eliminate_space(response.xpath('//div[contains(@class, "location-details")]//text()').extract())
			item = ChainItem()
			item['address'] = ''
			item['city'] = ''
			addr = usaddress.parse(detail[0])
			for temp in addr:
				if temp[1] == 'PlaceName':
					item['city'] += temp[0].replace(',','')	+ ' '
				elif temp[1] == 'StateName':
					item['state'] = temp[0].replace(',','')
				elif temp[1] == 'ZipCode':
					item['zip_code'] = temp[0]
				else:
					item['address'] += temp[0].replace(',', '') + ' '
			item['country'] = 'United States'
			item['phone_number'] = detail[1]
			h_temp = ''
			for de in detail:
				if ':' in de and 'Seasonal' not in de:
					h_temp += de + ', '					
			item['store_hours'] = h_temp[:-2]
			yield item			
		except:
			pass

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''