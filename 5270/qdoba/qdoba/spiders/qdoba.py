import scrapy
from lxml import etree
import os
import json

class qdoba(scrapy.Spider):
    name = "qdoba"
    item = {}
    history = ['']

    def start_requests(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			location_list = json.load(data_file)
		for location in location_list:
			init_url = 'https://prod.qdoba.bottlerocketservices.com/api/v1/query/store/locate/lat/'+ str(location['latitude'])+'/lon/'+ str(location['longitude'])+'/radius/30'
			yield scrapy.Request(url=init_url, callback=self.parse)   

    def parse(self, response):
		data = json.loads(response.body)
		for store in data['results']:
			try :
				self.item['store_name'] = store['name'].strip()
				self.item['store_number'] = ''
				self.item['address'] = store['address']['street']
				self.item['address2'] = ''
				if 'street2' in store['address']:
					self.item['address2'] = store['address']['street2']
				self.item['city'] = store['address']['city']
				self.item['state'] = store['address']['state']
				self.item['zip_code'] = store['address']['postal']
				self.item['country'] = store['address']['country']
				self.item['phone_number'] = ''
				if 'cateringPhone' in store['contactInfo']:
					self.item['phone_number'] = store['contactInfo']['cateringPhone'] + ', '
				if 'retailPhone' in store['contactInfo']:
					self.item['phone_number'] = self.item['phone_number'] + store['contactInfo']['retailPhone']
				self.item['latitude'] = store['geoLoc']['lat']
				self.item['longitude'] = store['geoLoc']['lon']
				self.item['store_hours'] = ''
				if 'hoursOfOperation' in store:
					week = ['Monday', 'Thuesday', 'Wednesday','Thursday','Friday','Saturday', 'Sunday']
					h_temp = ''
					for hour in store['hoursOfOperation']:
						h_temp = h_temp + week[hour['dayOfWeek']-1] + ' : ' + hour['timeWindows'][0]['openingTime'][:-7] + ' - ' + hour['timeWindows'][0]['closingTime'][:-7] + ', '
					self.item['store_hours'] = h_temp[:-2]
				self.item['store_type'] = ''
				self.item['other_fields'] = ''
				self.item['distributor_name'] = ''
				if self.item['zip_code'] not in self.history:
					yield self.item
				self.history.append(self.item['zip_code'])
			except : 
				pass
