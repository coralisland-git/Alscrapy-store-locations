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

class citymarket2(scrapy.Spider):
	name = 'citymarket2'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.citymarket.com/stores/api/graphql'
		header = {
			'accept':'*/*',
			'accept-encoding':'gzip, deflate, br',
			'content-type':'application/json'
		}
		# payload = {
		# 	"operationName":"storeSearch",
		# 	"query":"query storeSearch($searchText: String!, $filters: [String]!) {\
		# 				  storeSearch(searchText: $searchText, filters: $filters) {\
		# 				    stores {...storeSearchResult  }\
		# 				    fuel { ...storeSearchResult   }\
		# 				    shouldShowFuelMessage		  }\
		# 				}\
		# 				fragment storeSearchResult on Store { banner vanityName divisionNumber storeNumber\
		# 				  phoneNumber showWeeklyAd showShopThisStoreAndPreferredStoreButtons distance\
		# 				  latitude longitude \
		# 				  address { addressLine1  addressLine2  city  countryCode  stateCode  zip }\
		# 				  pharmacy { phoneNumber  }\
		# 				}\
		# 				",
		# 	"variables":{"searchText": "new york", "filters": []}
		# }

		payload = {"query":"query storeSearch($searchText: String!, $filters: [String]!) {\n  storeSearch(searchText: $searchText, filters: $filters) {\n    stores {\n      ...storeSearchResult\n    }\n    fuel {\n      ...storeSearchResult\n    }\n    shouldShowFuelMessage\n  }\n}\n\nfragment storeSearchResult on Store {\n  banner\n  vanityName\n  divisionNumber\n  storeNumber\n  phoneNumber\n  showWeeklyAd\n  showShopThisStoreAndPreferredStoreButtons\n  distance\n  latitude\n  longitude\n  address {\n    addressLine1\n    addressLine2\n    city\n    countryCode\n    stateCode\n    zip\n  }\n  pharmacy {\n    phoneNumber\n  }\n}\n","variables":{"searchText":"los angeles","filters":[]},"operationName":"storeSearch"}
		yield scrapy.Request(url=init_url, method='POST', body=json.dumps(payload), headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		pdb.set_trace()
		store_list = json.loads(response.body)['data']['storeSearch']['stores']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['vanityName'])
			item['store_number'] = self.validate(store['storeNumber'])
			item['address'] = self.validate(store['address']['addressLine1'])
			item['address2'] = self.validate(store['address']['addressLine2'])
			item['city'] = self.validate(store['address']['city'])
			item['state'] = self.validate(store['address']['stateCode'])
			item['zip_code'] = self.validate(store['address']['zip'])
			item['country'] = self.validate(store['address']['countryCode'])
			item['phone_number'] = self.validate(store['phoneNumber'])
			item['latitude'] = self.validate(store['latitude'])
			item['longitude'] = self.validate(store['longitude'])
			yield item			

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''