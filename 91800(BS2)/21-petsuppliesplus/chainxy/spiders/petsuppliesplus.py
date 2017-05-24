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

class petsuppliesplus(scrapy.Spider):
	name = 'petsuppliesplus'
	domain = 'https://www.petsuppliesplus.com/'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		header = {
			'Accept':'*/*',
			'Accept-Encoding':'gzip, deflate, br',
			'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
			'X-Requested-With':'XMLHttpRequest',
			'Cookie':'Chute_uID=702ca1b7f11145858ebd893ef8f67be0; .PSPUSER=ECC175C45BCA104EE207AE0F1EBF909A8526193C8DDBB21BEA0C45C839282A9588F0BB7ED9BDC90DB22EEB0CB26B4678D4E21A1C236C407EBA61D15685A29922F9864C7D6EF7FE0C82E1DBF8825AB007B381409D214A3FEF0FB64D72DF88E968FCC8C9ED4060697BA5D0555984907F370688C01E95AF0FA6B17EED3705573FF53FCE08CAEB55855ED711D7928D512617212387C96A6B9195C955A49F32A52DA5A22158DEE60D28A1CC6FB2953778758AF682F5553866FF4F2C2FCE237541472F9F4F568058B13E3ECD6E22E8FFEC4189D77151C451FDD16497DF29B0FD2138A5712972B878FAA0E2009B7B3BA765654C317FF3443083983E1DADF19CED7428811F5E995DBE4BB9D029990DE868B698AA7CBEAE30A6B9A1833E0028997337849FFCEDC830C8338226560EA2E8298720BBA5D8E4C59D4501B3B2179580F6B06901A657073551B84FC4C88AE4FEF6712FF6764CF56622B24A5A79D9C037E905D8FD87C7A32B7DD38007CA294E6C3B6AE24D76006A009A0F9AC7CD3ECDF965656ED425F674936463634BE090511B578F088C4CA6B47CAE479FD0F4E2735AB565755CDF4D35784C1B0C7BF5FB868189BD7D6812EC1BB52B5C8A74B48BBC5940B97580303339020D32D85A2E7B8320BBDA3F397E1E64E0E462B1E3B2AAA5804C4F78C1ECF5D2B0283E59476455B84120234D61A50652559EB0B1F1A037AE5CD01370D0F1E2FB50B124DB53942F0A62F9191C07B07FD8C8; __unam=1c46568-15baf6a6e26-4e0697c1-4; TURNTO_TEASER_SHOWN=1493296683649; ASP.NET_SessionId=ebajaxcla3vuvox2gszfaapy; cd.petsuppliesplus.com#lang=en; BNES_cd.petsuppliesplus.com#lang=4LNEQfo00HtY1YLZvM3JnRCgTBYIonG6dPLadTM7YfSi85EKsrSpu+lB4WqJbd86FUTTW0duGdp36tfeUOV02w==; SignUpPromoCheck=false; _ga=GA1.2.1266557699.1493296379; MyLatitude=37.09024; MyLongitude=-95.712891; SearchedState=NY; InvalidAddress=; NoNearByStore=; BNI_persistence=0000000000000000000000000600010a0000bb01; SearchedLatitude=40.730712; SearchedLongitude=-73.887375; SeachFlag=true; SearchCityLat=36.778261; SearchCityLng=-119.4179324'

		}
		form_data = {
			'searchQuery':'New York',
			'pageSize':'6',
			'fromRowNumber':'0'
		}
		init_url  = 'https://www.petsuppliesplus.com/api/sitecore/Store/Search'

		yield scrapy.FormRequest(url=init_url, formdata=form_data, method='POST', headers=header, callback=self.body)

	def body(self, response):
		print("=========  Checking.......")
		with open('re22.html', 'wb') as f:
			f.write(response.body)
		store_list = json.loads(response.body)
		# for store in store_list:
		# 	item = ChainItem()
		# 	item['store_name'] = store['Name']
		# 	item['store_number'] = store['MyStoreID']
		# 	item['address'] = store['Address1']
		# 	item['address2'] = store['Address2']
		# 	item['city'] = store['City']
		# 	item['state'] = store['StateCode']
		# 	item['zip_code'] = store['Zip']
		# 	item['country'] = 'Canada'
		# 	item['phone_number'] = store['Phone']
		# 	item['latitude'] = store['LatPos']
		# 	item['longitude'] = store['LngPos']
		# 	item['store_hours'] = ''
		# 	item['store_type'] = ''
		# 	item['other_fields'] = ''
		# 	item['coming_soon'] = ''
		# 	if item['store_number'] in self.history:
		# 		continue
		# 	self.history.append(item['store_number'])
		# 	yield item			

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''