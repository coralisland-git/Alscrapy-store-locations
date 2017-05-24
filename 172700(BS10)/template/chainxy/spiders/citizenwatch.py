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
import csv
import pdb

class citizenwatchSpider(scrapy.Spider):
    name = 'citizenwatch'
    domain = 'http://www.citizenwatch.com'
    history = []

    def __init__(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/US_States.json'
        
        with open(file_path) as data_file:    
            self.location_list = json.load(data_file)

    def start_requests(self): 
        init_url = 'http://citizenwatch.com.gotlocations.com/index.php'

        # for location in self.location_list:
        formdata = {
            'c': 'IE',
            'ip_country': 'US',
            'address': 'CA',
            'bypass': 'y',
            'Submit': 'search',
            'lat2': '',
            'lon2': ''
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        yield scrapy.FormRequest(url=init_url, method="POST", headers=headers, body=json.dumps(formdata), callback=self.body) 

    def body(self, response):
        store_list = response.xpath('//div[contains(@class, "altrow")]')
        for store in store_list:
        	item = ChainItem()
        	detail = store.xpath('.//text()').extract()
        	pdb.set_trace()
			# item['store_name'] = self.validate(store['name'])
			# item['store_number'] = self.validate(store['store_number'])
			# item['address'] = self.validate(store['address'])
			# item['address2'] = self.validate(store['address2'])
			
			# item['address'] = ''
			# item['city'] = ''
			# addr = usaddress.parse(address)
			# for temp in addr:
			# 	if temp[1] == 'PlaceName':
			# 		item['city'] += temp[0].replace(',','')	+ ' '
			# 	elif temp[1] == 'StateName':
			# 		item['state'] = temp[0]
			# 	elif temp[1] == 'ZipCode':
			# 		item['zip_code'] = temp[0]
			# 	else:
			# 		item['address'] += temp[0].replace(',', '') + ' '

			# address = ''
			# addr = address.split(',')
			# item['city'] = self.validate(addr[0].strip())
			# item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			# item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())

			# item['city'] = self.validate(store['city'])
			# item['state'] = self.validate(store['state'])
			# item['zip_code'] = self.validate(store['zip'])
			# item['country'] = self.validate(store['country'])
			# item['phone_number'] = self.validate(store['phone'])
			# item['latitude'] = self.validate(store['latitude'])
			# item['longitude'] = self.validate(store['longitude'])
			# h_temp = ''
			# hour_list = ''
			# for hour in hour_list:
			# 	h_temp += hour + ', '
			# item['store_hours'] = h_temp[:-2]
			# item['store_hours'] = self.validate(store['hours'])
			# item['store_type'] = ''
			# item['other_fields'] = ''
			# item['coming_soon'] = ''
			# if item['store_number'] not in self.history:
			# 	self.history.append(item['store_number'])
			# 	yield item	
            
	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	