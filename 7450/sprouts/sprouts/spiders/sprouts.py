import scrapy

class sprouts(scrapy.Spider):
    name = "sprouts"
    item = {}
    history = ['']
    def start_requests(self):
        init_url  = 'https://www.sprouts.com/stores/search/'
        yield scrapy.Request(url=init_url, callback=self.body)  

    def body(self, response):
        state_list = response.xpath('.//div[@class="sprouts-select-container"]//select//option')
        for state in state_list:
            url  = 'https://www.sprouts.com/stores/search/-/store-search/view?_storesearch_WAR_storelocatorportlet_latitude=&_storesearch_WAR_storelocatorportlet_longitude=&zip=&city=&state='+state.xpath('./@value').extract_first().strip()
            yield scrapy.Request(url=url, callback=self.parse)  
         
    def parse(self, response):
        store_list = response.xpath('.//div[@class="store-finder-summary-container store-resultitem"]')
        for store in store_list:
            self.item['store_name'] = (store.xpath('.//div[@class="store-finder-store-summary-name"]//h3//a/text()').extract_first()).split('(')[0].strip()
            self.item['store_number'] = (store.xpath('.//div[@class="store-finder-store-summary-name"]//h3//a/text()').extract_first()).split('(')[1].strip().split('#')[1][:-1].strip()
            addr = store.xpath('.//div[@class="store-finder-summary-address"]/text()').extract()
            self.item['address'] = addr[0].strip()
            self.item['address2'] = ''
            self.item['city'] = addr[1].split(',')[0].strip()
            self.item['state'] = addr[1].split(',')[1].strip().split(' ')[0].strip()
            self.item['zip_code'] = addr[1].split(',')[1].strip().split(' ')[1].strip()
            self.item['country'] = 'United States'
            self.item['phone_number'] = addr[2].strip()
            self.item['latitude'] = ''
            self.item['longitude'] = ''
            self.item['store_hours'] = ''
            try:
                self.item['store_hours'] = (store.xpath('.//div[@class="store-finder-store-summary-name"]//p/text()').extract_first()).strip()               
                self.item['store_hours'] = (store.xpath('.//div[@class="store-finder-summary-hours"]//strong/text()').extract_first()).strip()
            except:
                pass
            self.item['store_type'] = ''
            self.item['other_fields'] = ''
            self.item['distributor_name'] = ''
            if self.item['store_name']+str(self.item['store_number']) not in self.history:
                yield self.item
                self.history.append(self.item['store_name']+str(self.item['store_number']))

    
        
    
        