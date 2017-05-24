import scrapy, time
from selenium import webdriver
from lxml import etree

class Neispider(scrapy.Spider):
    name = "neispider"
    item = {}     
    driver = webdriver.Chrome("./chromedriver")

    def start_requests(self):
        init_url  = 'http://www.neimanmarcus.com'
        header = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, sdch',
            'Accept-Language':'en-US,en;q=0.8',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'Host':'www.neimanmarcus.com',
            'Referer':'http://www.neimanmarcus.com/en-ca/stores/locations',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }
        yield scrapy.Request(url=init_url, method="GET", headers=header, callback=self.parse)    

    def parse(self, response):
        self.driver.get("http://www.neimanmarcus.com/en-ca/stores/locations")  
        time.sleep(20)      
        source = self.driver.page_source.encode("utf8")
        self.driver.close()
        tree = etree.HTML(source)
        store_list = tree.xpath('//div[@class="store-info nmResult-store-info"]')
        for store in store_list:
            self.item['store_name'] = store.xpath('.//div[@class="store-name"]//a/text()')[0].strip()
            self.item['store_number'] = ''
            self.item['address'] = store.xpath('.//div[@class="grid-60 tablet-grid-50 grid-parent directory"]//p[@class="localStoreAddressBar"]//span[1]/text()')[0].strip()
            print(self.item['address'])
            self.item['address2'] = ''
            self.item['country'] = 'United States'
            address = store.xpath('.//div[@class="grid-60 tablet-grid-50 grid-parent directory"]//p')
            if len(address[0].xpath('.//span')) == 4 :  
                self.item['address'] = address[0].xpath('.//span[1]/text()')[0].strip()
                self.item['city'] = (address[0].xpath('.//span[2]/text()')[0].strip())[:-1]
                self.item['state'] = address[0].xpath('.//span[3]/text()')[0].strip()
                self.item['zip_code'] = address[0].xpath('.//span[4]/text()')[0].strip()
            else :
                self.item['address'] = address[0].xpath('.//span[1]/text()')[0].strip() + ", " + address[0].xpath('.//span[2]/text()')[0].strip()
                self.item['city'] = (address[0].xpath('.//span[3]/text()')[0].strip())[:-1]
                self.item['state'] = address[0].xpath('.//span[4]/text()')[0].strip()
                self.item['zip_code'] = address[0].xpath('.//span[5]/text()')[0].strip()
            phone_list = store.xpath('.//div[@class="grid-60 tablet-grid-50 grid-parent directory"]//div[@class="hide-on-mobile"]//span')
            p_temp = ''
            for phone in phone_list:
                p_temp = p_temp + phone.xpath('.//a/text()')[0].strip() + ', '
            self.item['phone_number'] = p_temp[:-2]   
            self.item['latitude'] = ''
            self.item['longitude'] = ''
            hour_list = store.xpath('.//div[@class="grid-40 tablet-grid-50 grid-parent store-hours directory"]//table//tbody//tr')
            h_temp = ''
            for hour in hour_list:
                h_temp = h_temp + hour.xpath('.//td[1]/text()')[0].strip() + hour.xpath('.//td[2]/text()')[0].strip() + ", "
            self.item['store_hours'] = h_temp[:-2]
            self.item['store_type'] = ''
            self.item['other_fields'] = ''
            self.item['distributor_name'] = ''
            yield self.item   