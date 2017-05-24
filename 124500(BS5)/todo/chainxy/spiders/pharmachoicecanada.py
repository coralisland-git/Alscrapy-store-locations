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
import unicodedata

class pharmachoicecanada(scrapy.Spider):
	name = 'pharmachoicecanada'
	domain = ''
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")

	def start_requests(self):
		init_url = 'http://www.pharmachoice.com'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		self.driver.get("http://www.pharmachoice.com")
		time.sleep(1)
		# el = self.driver.find_element_by_id('pc_locate_lst_prov')
		# el.find_elements_by_tag_name('option')[1].click()
		# for option in el.find_elements_by_tag_name('option'):
		# 	option.click()
		# 	time.sleep(2)
			# self.driver.find_element_by_id('pc_locate_lnk_back').click()
		# source = self.driver.page_source.encode("utf8")
		# tree = etree.HTML(source)
		# self.driver.find_element_by_xpath('//a[@class="map-arrow"]').click()
		# store_list = tree.xpath('//div[@id="tabStores"]//div')
		# for cnt in range(1, len(store_list)):
		# 	self.driver.find_element_by_xpath('//div[@id="tabStores"]//div['+str(cnt)+']//a').click()
		# 	source = self.driver.page_source.encode("utf8")
		# 	tree = etree.HTML(source)
		# 	item = ChainItem()
		# 	detail = self.eliminatespace(tree.xpath('//div[@class="info_content"]//p//text()'))
		# 	item['store_name'] = detail[0].replace(':','')
		# 	item['address'] = detail[1]
		# 	addr = detail[2].split(',')
		# 	item['city'] = self.validate(addr[0].strip())
		# 	item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
		# 	item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
		# 	item['country'] = 'United States'
		# 	item['phone_number'] = detail[4]
		# 	if 'Hours:' in detail:
		# 		item['store_hours'] = detail[len(detail)-1]
		# 	yield item		
		# self.driver.close()

	def eliminatespace(self, items):
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