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
import unicodedata

class coffeeculture(scrapy.Spider):
	name = 'coffeeculture'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.coffeeculturecafe.com/locations/?/front/get/_all_/_all_/1'
		yield scrapy.Request(url=init_url, callback=self.body)

	def body(self, response):
		store_list = json.loads(response.body)
		print("=========  Checking.......", len(store_list))
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.format(self.validate(store['name']))
			item['latitude'] = self.validate(store['lat'])
			item['longitude'] = self.validate(store['lng'])
			detail = etree.HTML(self.validate(store['display']))
			addr = detail.xpath('//li[@class="lpr-location-address"]/text()')
			item['address'] = self.validate(addr[0])	
			if 'Canada' in addr or 'CANADA' in addr :
				if len(addr) == 3:
					addr_detail = self.validate(addr[1]).split(' ')
				else:
					addr_detail = self.validate(addr[2]).split(' ')
				c_temp = ''
				if len(self.validate(addr_detail[len(addr_detail)-2])) == 2:
					for cnt in range(0, len(addr_detail)-2):
						c_temp += addr_detail[cnt] + ' '
					item['city'] = self.validate(c_temp)
					item['state'] = self.validate(addr_detail[len(addr_detail)-2])
					item['zip_code'] = self.validate(addr_detail[len(addr_detail)-1])
				else :
					for cnt in range(0, len(addr_detail)-3):
						c_temp += addr_detail[cnt] + ' '
					item['city'] = self.validate(c_temp)
					item['state'] = self.validate(addr_detail[len(addr_detail)-3])
					item['zip_code'] = self.validate(addr_detail[len(addr_detail)-1]) +' ' + self.validate(addr_detail[len(addr_detail)-2])
				item['country'] = 'Canada'

			else:
				c_temp = ''
				if len(addr) == 4:
					addr_detail = self.validate(addr[2]).split(' ')
				else :
					addr_detail = self.validate(addr[1]).split(' ')
				for cnt in range(0, len(addr_detail)-2):
					c_temp += addr_detail[cnt] + ' '
				item['city'] = self.validate(c_temp)
				item['state'] = self.validate(addr_detail[len(addr_detail)-2])
				item['zip_code'] = self.validate(addr_detail[len(addr_detail)-1])
				try:
					zipcode=int(item['zip_code'])
				except:
					addr_detail = self.validate(addr[2]).split(' ')
					c_temp = ''
					for cnt in range(0, len(addr_detail)-2):
						c_temp += addr_detail[cnt] + ' '
						item['city'] = self.validate(c_temp)
						item['state'] = self.validate(addr_detail[len(addr_detail)-2])
						item['zip_code'] = self.validate(addr_detail[len(addr_detail)-1])
				item['country'] = 'United States'
			try:
				item['phone_number'] = self.validate(detail.xpath('//li[@class="lpr-location-phone"]/text()')[0]).split('Phone:')[1]
			except:
				pass
			h_temp = ''
			hour_list = detail.xpath('//li[contains(@class, "lpr-location-misc")]/text()')
			for hour in hour_list:
				h_temp += self.validate(hour) + ', '
			item['store_hours'] = h_temp[:-2]
			yield item				

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def format(self, item):
		return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()