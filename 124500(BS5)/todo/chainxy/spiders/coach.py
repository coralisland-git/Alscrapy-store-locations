from __future__ import unicode_literals
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

class coach(scrapy.Spider):
	name = 'coach'
	domain = ''
	history = []

	def start_requests(self):
		urls = [{ 'url':'http://www.coach.com/stores-edit-search?country=CA', 'type':'1'},
				{ 'url':'http://www.coach.com/stores-edit-state?dwfrm_storelocator_address_states_stateUSSO=CA&dwfrm_storelocator_findbystate=Search+state', 'type':'0'}]
		for url in urls:
			yield scrapy.Request(url=url['url'], callback=self.body, meta={'type':url['type']}) 

	def body(self, response):
		if response.meta['type'] == '1':
			temp_list = response.xpath('//select[@id="dwfrm_storelocator_address_countryTally"]//option')
		else:
			temp_list = response.xpath('//select[@id="dwfrm_storelocator_address_states_stateTallyUSCA"]//option')
		for temp in temp_list:
			label = temp.xpath('./@label').extract_first()
			value = temp.xpath('./@value').extract_first()
			if response.meta['type'] == '1':
				url = 'http://www.coach.com/stores-edit-search?country=%s&countryName=%s' %(value, label)
			else:
				url = 'http://www.coach.com/stores-edit-state?dwfrm_storelocator_address_states_stateUSSO=%s&dwfrm_storelocator_findbystate=Search+state' %value
			yield scrapy.Request(url=url, callback=self.parse_store, meta={'value':value, 'label':label, 'type':response.meta['type']})

	def parse_store(self, response):
		total_cnt = response.xpath('//div[contains(@class, "equal-align count pull-left")]/text()').extract_first().strip().replace(',','')
		total_cnt = int(total_cnt) / 10 + 1
		for cnt in range(0, total_cnt):
			cnt *=10
			if response.meta['type'] == '1':
				url = 'http://www.coach.com/stores-edit-search?country=%s&sz=10&start=%s&format=ajax&storeSequenceNo=%s' %(response.meta['value'], str(cnt), str(cnt))
				yield scrapy.Request(url=url, callback=self.parse_page, meta={'country':response.meta['label'], 'type': response.meta['type']})
			else:
				url = 'http://www.coach.com/on/demandware.store/Sites-Coach_US-Site/en_US/Stores-FilterResult?firstQuery=%s_state&showRFStoreDivider=false&showRStoreDivider=true&showFStoreDivider=false&showDStoreDivider=false&start=%s&sz=10&format=ajax' %(response.meta['value'], str(cnt))
				yield scrapy.Request(url=url, callback=self.parse_page, meta={'country':'United States', 'type': response.meta['type']})

	def parse_page(self, response):
		try:
			if response.meta['type'] == '1':
				store_list = response.xpath('//li[contains(@class, "stores")]')
			else:
				store_list = response.xpath('//div[contains(@class, "stores")]')
			for store in store_list:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//div[contains(@class,"store-name")]//meta[@itemprop="name"]//@content').extract_first())
				address = self.eliminatespace(store.xpath('.//span[@itemprop="streetAddress"]/text()').extract())
				try:
					item['address'] = address[0]
					if len(address) > 1:
						item['address2'] = address[1]
				except:
					pass
				item['city'] = self.validate(store.xpath('.//span[@itemprop="addressLocality"]/text()').extract_first())
				item['state'] = self.validate(store.xpath('.//span[@itemprop="addressRegion"]/text()').extract_first())
				item['zip_code'] = self.validate(store.xpath('.//span[@itemprop="postalCode"]/text()').extract_first())
				item['country'] = response.meta['country']
				item['phone_number'] = self.validate(store.xpath('.//span[@itemprop="telephone"]/text()').extract_first())
				h_temp = ''
				hour_list = self.eliminatespace(store.xpath('.//span[@itemprop="openingHours"]/text()').extract())
				for hour in hour_list:
					h_temp += self.validate(hour) + ', '
				item['store_hours'] = h_temp[:-2]
				yield item		
		except:
			pass

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def eliminatespace(self, items):
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