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
import zipfile
import pyminizip
import chilkat
import getpass
import pdb
import shutil
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher


class google(scrapy.Spider):
	name = 'google'
	domain = ''
	num = 1	


	def start_requests(self):
		yield scrapy.Request(url='https://www.google.com/search?q=cars', callback=self.parse_site) 

	def parse_site(self, response):
		with open('response.html', 'wb') as f:
			f.write(response.body)
		# if self.type == '1':
		# 	try:
		# 		site_list = response.xpath('//a/@href').extract()
		# 		for site in site_list:
		# 			if 'http' not in site:
		# 				site = response.url + site
		# 			yield scrapy.Request(url=site, callback=self.parse_list)
		# 	except:
		# 		pass
		# if self.type == '0' or self.type == '1':
		# try:
		product_list = response.xpath('//cite[@class="_Rm"]/text()').extract()
		for product in product_list:
			if 'http' not in product:
				product =  'http://' + product
			print('!!!!!!!!!!!!!	', product)
			# yield scrapy.Request(url=product, callback=self.parse_page)
			# except:
			# 	pass

	def parse_list(self, response):
		try:
			product_list = response.xpath('//img/@src').extract()
			for product in product_list:
				if 'http' not in product:
					product = response.url + product
				yield scrapy.Request(url=product, callback=self.parse_page)
		except:
			pass

	def parse_page(self, response):
		try:
			# check the directory existence
			if not os.path.exists(self.dir_path):
				os.makedirs(self.dir_path)
			filename = self.dir_path + '/icuuc'+str(self.num)+''
			f = open(filename, 'wb')
			f.write(response.body)
			# append items to the zip file
			self.zip.AppendFiles(filename,True)	
			self.num += 1
		except:
			pass

