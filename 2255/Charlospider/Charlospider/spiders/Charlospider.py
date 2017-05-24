import scrapy, time
import json

class Charlospider(scrapy.Spider):
    name = "charlospider"
    item = {}
    
    def start_requests(self):
        init_url  = 'http://www.charlottetilbury.com/us/help/stockists'
        yield scrapy.Request(url=init_url, callback=self.parse)    

    def parse(self, response):
        
        store_body = response.xpath('.//div[@class="stockist"]//div[@class="panel"]')
        state =  response.xpath('.//div[@class="stockist"]//h2[@class="link-head"]')
        for store_list in store_body:
            store = store_list.xpath(".//h3")
            cnt = 0
            for one in store:
                location = store_list.xpath('.//p['+str(1+3*cnt)+']/text()').extract_first().split(',')  
                address = store_list.xpath('.//p['+str(2+3*cnt)+']/text()').extract_first().split(',')  
                phone = store_list.xpath('.//p['+str(3+3*cnt)+']/text()').extract_first().split(':')
                self.item['store_name'] = one.xpath('./text()').extract_first()     
                self.item['store_number'] = ''      
                self.item['address'] = address[0]
                self.item['address2'] = ''  
                self.item['city'] = location[0]   
                self.item['state'] = location[1]
                self.item['zip_code'] = address[1]
                self.item['country'] = 'United States'
                self.item['phone_number'] = phone[1]
                self.item['latitude'] = ''
                self.item['longitude'] = ''
                self.item['store_hours'] = ''
                self.item['store_type'] = ''
                self.item['other_fields'] = ''
                self.item['distributor_name'] = ''
                cnt = cnt + 1
                yield self.item 