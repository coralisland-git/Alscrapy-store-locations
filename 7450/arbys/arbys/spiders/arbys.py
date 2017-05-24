import scrapy
import os
import json
import geocoder

class arbys(scrapy.Spider):
    name = "arbys"
    item = {}
    history = ['']

    def start_requests(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/cities.json'
        with open(file_path) as data_file:    
            location_list = json.load(data_file)
        
        for location in location_list:
            g = geocoder.google([location['latitude'], location['longitude']], method='reverse')
            init_url  = 'http://locations.arbys.com/search.html?q='+g.city+'%2C+'+g.state
            yield scrapy.Request(url=init_url, callback=self.parse)  
         
    def parse(self, response):
        store_list = response.xpath('.//div[@class="location"]')
        for store in store_list:
            self.item['store_name'] = (store.xpath('.//h2[@class="location-info-title"]//span[2]/text()').extract_first()).strip()
            self.item['store_number'] = (store.xpath('.//div[@class="location-info-id"]/text()').extract_first()).split('#')[1].strip()
            addr = store.xpath('.//div[@class="store-finder-summary-address"]/text()').extract()
            self.item['address'] = (store.xpath('.//address//span[@class="c-address-street"]//span[@class="c-address-street-1"]/text()').extract_first()).strip()
            self.item['address2'] = ''
            try:
                self.item['address2'] = (store.xpath('.//address//span[@class="c-address-street"]//span[@class="c-address-street-2"]/text()').extract_first()).strip()
            except:
                pass
            self.item['city'] = (store.xpath('.//address//span[@class="c-address-city"]//span[1]/text()').extract_first()).strip()
            self.item['state'] = (store.xpath('.//address//abbr[@class="c-address-state"]/text()').extract_first()).strip()
            self.item['zip_code'] = (store.xpath('.//address//span[@class="c-address-postal-code"]//text()').extract_first()).strip()
            self.item['country'] = (store.xpath('.//address//abbr[@class="c-address-country-name c-address-country-us"]/@title').extract_first()).strip()
            self.item['phone_number'] = (store.xpath('.//div[@class="location-info-phone"]//a/text()').extract_first()).strip()
            self.item['latitude'] = ''
            self.item['longitude'] = ''
            hour_daily = ''
            try:
                hour_daily  = (store.xpath('.//div[@class="location-info-hours"]//span[@class="c-location-hours-today-details-row js-day-of-week-row"][1]//span//span/text()').extract_first()).strip()
            except:
                pass
            if 'Open' in hour_daily:
                self.item['store_hours'] = hour_daily
            else :
                h_temp = ''
                week_list = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
                hour_list  = store.xpath('.//div[@class="location-info-hours"]//span[@class="c-location-hours-today-details-row js-day-of-week-row"]')
                
                for hour in hour_list:
                    week = week_list[int(hour.xpath('./@data-day-of-week-start-index').extract_first())]
                    hour_open = hour.xpath('.//span[@class="c-location-hours-today-day-hours"]//span[@class="c-location-hours-today-day-hours-intervals-instance-open"]/text()').extract_first()
                    hour_close = hour.xpath('.//span[@class="c-location-hours-today-day-hours"]//span[@class="c-location-hours-today-day-hours-intervals-instance-close"]/text()').extract_first()
                    h_temp = h_temp + week + ' : ' + str(hour_open) + '-' + str(hour_close) + ', '
                self.item['store_hours'] = h_temp[:-2]
            self.item['store_type'] = ''
            self.item['other_fields'] = ''
            self.item['distributor_name'] = ''
            if self.item['store_name']+str(self.item['store_number']) not in self.history:
                yield self.item
                self.history.append(self.item['store_name']+str(self.item['store_number']))

    
        
    
        