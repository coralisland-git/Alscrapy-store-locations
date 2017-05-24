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

class associatedbank(scrapy.Spider):
	name = 'associatedbank'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://spatial.virtualearth.net/REST/v1/data/e0ac722002794ad6b6cb3e5b3320e23b/AssociatedProduction/AssociatedBank?$filter=Branch%20Eq%27Yes%27%20Or%20ATM%20Eq%27Yes%27%20Or%20NonBranchLocation%20Eq%27Yes%27&spatialFilter=nearby('+str(location['latitude'])+','+str(location['longitude'])+',%2080%20)&$select=AddressLine,Latitude,Longitude,PostalCode,DriveUpHours,LobbyHours,LocationName,PrimaryCity,State,Phone,ATM,Branch,DAATMs,MortgageOfficer,AISRep,SafeDepositBox,PrivateClient,InstitutionalTrust,InstantIssueCards,NonBranchLocation&$*&$format=json&jsonp=SDSServiceCallback&key=Apc8XDQjnMpfQnJXz8qbV_y8lRaMTqq35W_gbey3U-P3j2EmFs7eCjLO-fofpeMJ'
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			data = response.body.split('SDSServiceCallback(')[1].strip()[:-1]
			store_list = json.loads(data)['d']['results']
			for store in store_list:
				item = ChainItem()
				item['store_name'] = self.validate(store['LocationName'])
				item['address'] = self.validate(store['AddressLine'])
				item['city'] = self.validate(store['PrimaryCity'])
				item['state'] = self.validate(store['State'])
				item['zip_code'] = self.validate(store['PostalCode'])
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store['Phone'])
				item['latitude'] = self.validate(str(store['Latitude']))
				item['longitude'] = self.validate(str(store['Longitude']))
				item['store_hours'] = ''
				if self.validate(store['LobbyHours']) != '':
					item['store_hours'] = 'LobbyHours ' + self.validate(store['LobbyHours'])
				if self.validate(store['DriveUpHours']) != '':
					if item['store_hours'] != '':
						item['store_hours'] += ', '
					item['store_hours'] += 'DriveUpHours ' + self.validate(store['DriveUpHours'])
				item['store_type'] = ''
				item['other_fields'] = ''
				item['coming_soon'] = ''
				if item['store_name']+item['phone_number'] not in self.history:
					self.history.append(item['store_name']+item['phone_number'])
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

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''

	def fixLazyJson (self, in_text):
		tokengen = tokenize.generate_tokens(StringIO(in_text).readline)
		result = []
		for tokid, tokval, _, _, _ in tokengen:
			if (tokid == token.NAME):
				if tokval not in ['true', 'false', 'null', '-Infinity', 'Infinity', 'NaN']:
					tokid = token.STRING
					tokval = u'"%s"' % tokval
			elif (tokid == token.STRING):
				if tokval.startswith ("'"):
					tokval = u'"%s"' % tokval[1:-1].replace ('"', '\\"')
			elif (tokid == token.OP) and ((tokval == '}') or (tokval == ']')):
				if (len(result) > 0) and (result[-1][1] == ','):
					result.pop()			
			elif (tokid == token.STRING):
				if tokval.startswith ("'"):
					tokval = u'"%s"' % tokval[1:-1].replace ('"', '\\"')
			result.append((tokid, tokval))

		return tokenize.untokenize(result)
