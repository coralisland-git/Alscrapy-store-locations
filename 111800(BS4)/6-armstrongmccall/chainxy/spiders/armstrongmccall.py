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

class armstrongmccall(scrapy.Spider):
	name = 'armstrongmccall'
	domain = 'https://www.armstrongmccall.com/'
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")

	def start_requests(self):
		yield scrapy.Request(url=self.domain, callback=self.body) 

	def body(self, response):	
		print("=========  Checking.......")
		self.driver.get("https://www.armstrongmccall.com/StoreLocator/Map.aspx?&cname=BizSearchResult&zip=90025&tag=All&m=20000")
		time.sleep(2)
		next_bt = ''
		for i in range(0, 100):
			source = self.driver.page_source.encode("utf8")
			tree = etree.HTML(source)
			try:
				next_bt = tree.xpath('//input[@name="dnn$ctr713$ControlLoader$BizSearchResult$cmdNext"]/@disabled')[0].strip()
			except:
				next_bt = ''

			if next_bt == 'disabled':
				break
			else :
				for cnt in range(0,5):
					address = tree.xpath('//tr[@id="dnn_ctr713_ControlLoader_BizSearchResult_rptSearchResults_trFullAddress_'+str(cnt)+'"]//td/text()')
					item = ChainItem()
					item['store_name'] = 'Armstrong McCall'
					try:
						item['address'] = self.validate(address[0].strip().split('\n')[0])
						item['address2'] = self.validate(address[0].strip().split('\n')[1])
					except:
						item['address'] = self.validate(address[0].strip())
 					c_temp = ''
					address = address[1].strip().replace('  ', '').split('\n')
					for cnt in range(0, len(address)-2):
						c_temp += self.validate(address[cnt]) + ' '
					item['city'] = self.validate(c_temp.strip())
					item['state'] = self.validate(address[len(address)-2])
					item['zip_code'] = self.validate(address[len(address)-1])
					item['country'] = 'United States'
					item['phone_number'] = self.validate(tree.xpath('//tr[@id="dnn_ctr713_ControlLoader_BizSearchResult_rptSearchResults_trPhone_'+str(cnt)+'"]//td/text()')[0])
					yield item		
				self.driver.find_element_by_name('dnn$ctr713$ControlLoader$BizSearchResult$cmdNext').click()

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''