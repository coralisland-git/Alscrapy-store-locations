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
# import chilkat
import getpass
import pdb
import shutil
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher


class product(scrapy.Spider):
	name = 'product'
	domain = ''
	num = 1	

	def __init__(self):
		dispatcher.connect(self.spider_closed, signals.spider_closed)

	def spider_closed(self, spider):
		# save zipfile
		try:
			# self.zip.WriteZip()
		# delete the directory
			# if os.path.exists(self.dir_path):
			# 	shutil.rmtree(self.dir_path)
			print('************************ Success ***********************')
			# print('************* '+ self.name +'.zip file is created. ***************')
		except:
			pass

	def start_requests(self):
		self.name = raw_input('File Name : ')
		if self.name != '':
			self.url = raw_input('Site Url : ')
			# self.password = getpass.getpass('Password : ')
			# self.confirm = getpass.getpass('Password Confirm : ')
			self.password = 'password'
			self.confirm = 'password'
			if self.password == self.confirm:
				self.type = raw_input('Type : ')
				self.dir_path = './'+self.name
				# create encrypt zip file
				# self.zip = chilkat.CkZip()
				# self.zip.UnlockComponent("anything for 30-day trial")
				# self.zip.NewZip(self.name+'.zip')
				# # Set the Encryption property = 4, which indicates WinZip compatible AES encryption.
				# self.zip.put_Encryption(4)
				# # The key length can be 128, 192, or 256.
				# self.zip.put_EncryptKeyLength(128)
				# self.zip.SetPassword(self.password)
				yield scrapy.Request(url=self.url, callback=self.parse_site) 
			else:
				print("******** Sorry, Password confirmation is failed. Please Try again ********")
		else:
			print("******** Sorry, File name can't be empty. Please Try again ********")

	def parse_site(self, response):
		if self.type == '1':
			try:
				site_list = response.xpath('//a/@href').extract()
				for site in site_list:
					if 'http' not in site:
						site = response.url + site
					yield scrapy.Request(url=site, callback=self.parse_list)
			except:
				pass
		if self.type == '0' or self.type == '1':
			try:
				product_list = response.xpath('//img/@src').extract()
				for product in product_list:
					if 'http' not in product:
						product = response.url + product
					yield scrapy.Request(url=product, callback=self.parse_page)
			except:
				pass

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
			if 'jpg' in response.url or 'png' in response.url:
				# check the directory existence
				if not os.path.exists(self.dir_path):
					os.makedirs(self.dir_path)
				filename = self.dir_path + '/icuuc'+str(self.num)+''
				f = open(filename, 'wb')
				f.write(response.body)
				# append items to the zip file
				# self.zip.AppendFiles(filename,True)	
				self.num += 1
		except:
			pass

