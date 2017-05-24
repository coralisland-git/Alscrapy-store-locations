import scrapy
import string

class Alspider(scrapy.Spider):
    name = "alspider"
    

    def start_requests(self):
        url = 'https://usa.loccitane.com/boutique-locator,82,1,34279,268123.htm?Country=United+States'
        yield scrapy.Request(url=url, callback=self.parse)    

    def parse(self, response):
        for item in response.xpath('.//div[@class="nano"]//ul'):
            storeDetail = item.xpath('./@href').extract_first()
            request = scrapy.Request(storeDetail , callback=self.parse_detail)      
            yield request
    
    def parse_detail(self, response):
        site_name = response.xpath('.//tr[@class="grey"]//a[@class="red_link"]/text()').extract_first() 
        site_url = response.xpath('.//tr[@class="grey"]//a[@class="red_link"]/@href').extract_first()
        site_url = (site_url.split("u=")[1]).split("&")[0]
        dataset = {
                 "Store Name" : '',
                 "Contact Person" : '',
                 "Phone Number" : '',
                 "Email" :'',
                 "Physical Store Addresses or Suburb" : '',
                 "Outlets" :'',
                 "Store Url" : ''
            }
        dataset["Store Name"] = site_name
        dataset["Store Url"] = site_url
        yield dataset

    