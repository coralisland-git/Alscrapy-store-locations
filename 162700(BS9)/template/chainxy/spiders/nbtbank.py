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

class nbtbank(scrapy.Spider):
	name = 'nbtbank'
	domain = ''
	history = []

	def start_requests(self):
		header = {
			"Accept":"*/*",
			"Accept-Encoding":"gzip, deflate, br",
			"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
			"X-Requested-With":"XMLHttpRequest"
		}
		for cnt in range(1, 40):
			init_url = 'https://www.nbtbank.com/mvc/BranchOffice/PageBranchLocator'
			formdata = {
				"IP":"45.56.150.42",
				"InputBranchType":"",
				"InputAddress":"",
				"InputRadius":"",
				"InputState":"",
				"InputCounty":"",
				"page":str(cnt),
			}
			yield scrapy.FormRequest(url=init_url, headers=header, method='post', formdata=formdata, callback=self.body) 

	def body(self, response):	
		print("=========  Checking.......")

		data = response.body.split('var locations =')[1].strip().split('var mapOptions =')[0].strip()[:-1]
		store_list = json.loads(data)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['BranchName'])
			item['address'] = self.validate(store['Address1'])
			item['address2'] = self.validate(store['Address2'])
			item['city'] = self.validate(store['City'])
			item['state'] = self.validate(store['State'])
			item['zip_code'] = self.validate(store['Zip'])
			item['country'] = self.validate(store['Country'])
			item['phone_number'] = self.validate(store['Phone'])
			item['latitude'] = self.validate(store['BranchLatitude'])
			item['longitude'] = self.validate(store['BranchLongitude'])
			week_list= ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
			h_temp = 'LobbyHours : '
			for week in week_list:
				if self.validate(store['Lobby'+week+'Hour']) != '':
					h_temp += week + ' ' + self.validate(store['Lobby'+week+'Hour']) + ', '

			h_temp += 'Drive-up Hours : '
			for week in week_list:
				if self.validate(store['Drive'+week+'Hour']) != '':
					h_temp += week + ' ' + self.validate(store['Lobby'+week+'Hour']) + ', '
			item['store_hours'] = h_temp[:-2]
			yield item			

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