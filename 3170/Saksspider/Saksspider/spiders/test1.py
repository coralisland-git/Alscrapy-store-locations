import scrapy
import os
import json

class test(scrapy.Spider):
    name = "test"
    item = {}

    def start_requests(self):        
        init_url  = 'http://www.saksfifthavenue.com/stores/stores.jsp'
        header = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'en-US,en;q=0.8',
            'Connection':'keep-alive',
            'Content-Type':'application/x-www-form-urlencoded',
            'Host':'www.saksfifthavenue.com',
            'Origin':'http://www.saksfifthavenue.com',
            'Referer':'http://www.saksfifthavenue.com/stores/stores.jsp',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }
        
        form_data = {
            'mForm':'stores_search',
            'bmFormID':'lKjwNUA',
            'mUID':'lKjwNUB',
            'mIsForm':'true',
            'mPrevTemplate':'/stores/stores.jsp',
            'mHidden':'storeNumber',
            'toreNumber':'',
            'mHidden':'eventId',
            'ventId':'',
            'mHidden':'AUTO_SUBMIT_INPUT',
            'UTO_SUBMIT_INPUT':'false',
            'mHidden':'storesSearch',
            'toresSearch':'true',
            'mText':'CITY_NAME_INPUT',
            'ITY_NAME_INPUT':'Los Angeles',
            'mSingle':'STATE_CODE_INPUT',
            'TATE_CODE_INPUT':'CA',
            'mText':'POSTAL_CODE_INPUT',
            'OSTAL_CODE_INPUT':'Zip Code',
            'mSingle':'DISTANCE_INPUT',
            'ISTANCE_INPUT':'200',
            'mSubmit':'stores',
            'tores':'Find Stores'
        }

        yield scrapy.FormRequest(url=init_url, formdata=form_data, headers=header, callback=self.parse)

    def parse(self, response):
        print("======================")
        with open('response1.html', 'wb') as f:
            f.write(response.body)
        # store_list = response.xpath('.//div[@class="location"]')
        # for store in store_list:
        #     self.item['store_name'] = (store.xpath('.//h2[@class="location-info-title"]//span[2]/text()').extract_first()).strip()
        #     self.item['store_number'] = (store.xpath('.//div[@class="location-info-id"]/text()').extract_first()).split('#')[1].strip()
        #     addr = store.xpath('.//div[@class="store-finder-summary-address"]/text()').extract()
        #     self.item['address'] = (store.xpath('.//address//span[@class="c-address-street"]//span[@class="c-address-street-1"]/text()').extract_first()).strip()
        #     self.item['address2'] = ''
        #     try:
        #         self.item['address2'] = (store.xpath('.//address//span[@class="c-address-street"]//span[@class="c-address-street-2"]/text()').extract_first()).strip()
        #     except:
        #         pass
        #     self.item['city'] = (store.xpath('.//address//span[@class="c-address-city"]//span[1]/text()').extract_first()).strip()
        #     self.item['state'] = (store.xpath('.//address//abbr[@class="c-address-state"]/text()').extract_first()).strip()
        #     self.item['zip_code'] = (store.xpath('.//address//span[@class="c-address-postal-code"]//text()').extract_first()).strip()
        #     self.item['country'] = (store.xpath('.//address//abbr[@class="c-address-country-name c-address-country-us"]/@title').extract_first()).strip()
        #     self.item['phone_number'] = (store.xpath('.//div[@class="location-info-phone"]//a/text()').extract_first()).strip()
        #     self.item['latitude'] = ''
        #     self.item['longitude'] = ''
        #     hour_daily = ''
        #     try:
        #         hour_daily  = (store.xpath('.//div[@class="location-info-hours"]//span[@class="c-location-hours-today-details-row js-day-of-week-row"][1]//span//span/text()').extract_first()).strip()
        #     except:
        #         pass
        #     if 'Open' in hour_daily:
        #         self.item['store_hours'] = hour_daily
        #     else :
        #         h_temp = ''
        #         week_list = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        #         hour_list  = store.xpath('.//div[@class="location-info-hours"]//span[@class="c-location-hours-today-details-row js-day-of-week-row"]')
                
        #         for hour in hour_list:
        #             week = week_list[int(hour.xpath('./@data-day-of-week-start-index').extract_first())]
        #             hour_open = hour.xpath('.//span[@class="c-location-hours-today-day-hours"]//span[@class="c-location-hours-today-day-hours-intervals-instance-open"]/text()').extract_first()
        #             hour_close = hour.xpath('.//span[@class="c-location-hours-today-day-hours"]//span[@class="c-location-hours-today-day-hours-intervals-instance-close"]/text()').extract_first()
        #             h_temp = h_temp + week + ' : ' + str(hour_open) + '-' + str(hour_close) + ', '
        #         self.item['store_hours'] = h_temp[:-2]
        #     self.item['store_type'] = ''
        #     self.item['other_fields'] = ''
        #     self.item['distributor_name'] = ''
        #     yield self.item

    
        
    
        # 