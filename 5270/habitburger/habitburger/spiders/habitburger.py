import scrapy

class habitburger(scrapy.Spider):
    name = "habitburger"
    item = {}
    def start_requests(self):
        init_url  = 'https://www.habitburger.com/locations/all/'
        yield scrapy.Request(url=init_url, callback=self.parse)   
    
    def parse(self, response):
        data = response.xpath('.//li[@class="loc"]')
        for store in data:
            try:
                self.item['store_name'] = (store.xpath('.//div[@class="locaddress"]/text()').extract_first()).strip()
                self.item['store_number'] = ''
                locaddress = store.xpath('.//div[@class="locaddress"]//a/text()').extract()
                self.item['address'] = locaddress[0].strip()
                self.item['address2'] = ''
                cnt = 1
                if len(locaddress) == 3:
                    cnt = 2
                self.item['city'] = locaddress[cnt].strip().split(',')[0].strip()
                self.item['state'] = locaddress[cnt].strip().split(',')[1].strip().split(' ')[0].strip()
                self.item['zip_code'] = locaddress[cnt].strip().split(',')[1].strip().split(' ')[1].strip()
                self.item['country'] = 'United States'
                self.item['phone_number'] = ''
                self.item['latitude'] = ''
                self.item['longitude'] = ''
                locinfo = store.xpath('.//div[@class="locinfo"]/text()').extract()
                print(locinfo)
                h_temp = ''
                for hour in locinfo:
                    if '(' in hour:
                        self.item['phone_number'] = hour.strip()
                    else : 
                        h_temp = h_temp + hour.strip() + ', '
                self.item['store_hours'] = h_temp[:-2]
                self.item['store_type'] = ''
                self.item['other_fields'] = ''
                self.item['distributor_name'] = ''
                if len(self.item['state']) == 2:
                    yield self.item
            except:
                pass


                