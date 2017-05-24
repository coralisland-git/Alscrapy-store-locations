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
import time
import usaddress
import pdb

class gretchenscott(scrapy.Spider):
	name = 'gretchenscott2'
	domain = 'https://www.gretchenscottdesigns.com/'
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Zipcode.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):	
		init_url  = 'https://www.gretchenscottdesigns.com/store-locator'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = []
		self.driver.get("https://www.gretchenscottdesigns.com/store-locator")
		time.sleep(2)
		self.driver.find_element_by_xpath('//a[@class="klaviyo_close_modal klaviyo_header_close"]').click()
		for location in self.location_list:
			self.driver.get("https://www.gretchenscottdesigns.com/store-locator")
			time.sleep(2)
			input_zip = self.driver.find_element_by_name('zip')
			input_zip.clear()
			len_zip = len(str(location['zipcode']))
			search_zip = ''
			if len_zip == 3:
				search_zip = '00' + str(location['zipcode'])
			if len_zip == 4:
				search_zip = '0' + str(location['zipcode'])
			input_zip.send_keys(search_zip)
			self.driver.find_element_by_xpath('//input[@value="Search"]').click()
			i = 0
			flag_end = 0
			while flag_end == 0:
				request_url = 'http://app.xtremelocator.com/visitor/results.php?pos=' + str(i)
				self.driver.get(request_url)
				time.sleep(1)
				source = self.driver.page_source.encode("utf8")
				tree = etree.HTML(source)
				stores = tree.xpath('//li//div[@class="text"]//table//tbody')
				if not stores:
					flag_end = 1
				else:
					for store in stores:
						info_list = store.xpath('.//tr')
						store_name = info_list[0].xpath('.//td')[1].xpath('./a/text()')[0].strip()
						if not store_name in self.history:
							self.history.append(store_name)
							item = ChainItem()
							item['store_name'] = store_name
							temp_list = info_list[1].xpath('.//td')[1].xpath('./text()')
							temp_address = ''
							for temp in temp_list:
								temp_address += temp.strip() + ' '
							addr = usaddress.parse(temp_address)
							item['city'] = ''
							item['address'] = ''
							for temp in addr:
								if temp[1] == 'PlaceName':
									item['city'] += temp[0].replace(',','')	+ ' '
								elif temp[1] == 'StateName':
									item['state'] = temp[0].replace(',','')
								elif temp[1] == 'ZipCode':
									item['zip_code'] = temp[0].replace(',','')
								else:
									item['address'] += temp[0].replace(',','') + ' '
							item['country'] = info_list[2].xpath('.//td')[1].xpath('./text()')[0].strip()
							yield item
				i += 3
			
	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''