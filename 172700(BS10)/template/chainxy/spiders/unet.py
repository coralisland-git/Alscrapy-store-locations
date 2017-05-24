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
import pdb

class unet(scrapy.Spider):
	name = 'unet'
	domain = ''
	history = []

	def start_requests(self):
		for cnt in range(1, 18):
			init_url = 'https://www.brunet.ca/fr/trouver-pharmacie/localisateur.html?page=%s' %str(cnt)
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//ul[@class="locatorList"]//li[@class="locatorList-item"]//div[@class="contactInfo"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//a[@ga-data-id="liste-recherche-nom-pharmacie"]/text()').extract_first())
				item['address'] = self.validate(store.xpath('.//p[@class="addressMobile"][1]//a/text()').extract_first())
				address = self.validate(store.xpath('.//p[@class="addressMobile"][2]//a/text()').extract_first())
				addr = address.split(',')
				item['city'] = self.validate(addr[0].strip())
				item['state'] = self.validate(addr[1].strip()[:-7])
				item['zip_code'] = self.validate(addr[1].strip()[-7:])
				item['country'] = 'Canada'
				item['phone_number'] = self.validate(store.xpath('.//a[@ga-data-id="liste-recherche-numero-telephone"]/text()').extract_first())
				item['store_hours'] = self.validate(store.xpath('.//ul[@class="contactList"]//li[3]//span/text()').extract_first()).replace('Horaire : ','')
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