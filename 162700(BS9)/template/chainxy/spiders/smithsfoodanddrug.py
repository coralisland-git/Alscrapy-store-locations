import scrapy
import json
import csv
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem


class SmithsfoodanddrugSpider(scrapy.Spider):
    name = "smithsfoodanddrug"
    uid_list = []

    def start_requests(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/US_States.json'
        with open(file_path) as data_file:    
            locations = json.load(data_file)

        form_data = {"query":"query storeSearch($searchText: String!, $filters: [String]!) {\n  storeSearch(searchText: $searchText, filters: $filters) {\n    stores {\n      ...storeSearchResult\n    }\n    fuel {\n      ...storeSearchResult\n    }\n    shouldShowFuelMessage\n  }\n}\n\nfragment storeSearchResult on Store {\n  banner\n  vanityName\n  divisionNumber\n  storeNumber\n  phoneNumber\n  showWeeklyAd\n  showShopThisStoreAndPreferredStoreButtons\n  distance\n  latitude\n  longitude\n  address {\n    addressLine1\n    addressLine2\n    city\n    countryCode\n    stateCode\n    zip\n  }\n  pharmacy {\n    phoneNumber\n  }\n}\n","variables":{"searchText":"AI","filters":[]},"operationName":"storeSearch"}

        for row in locations:
            headers = {
                ':authority':'www.smithsfoodanddrug.com',
                ':method':'POST',
                ':path':'/stores/api/graphql',
                ':scheme':'https',
                'Content-Type': 'application/json',
                'accept':'*/*',
                'accept-encoding':'gzip, deflate, br'
            }
            variables = { 'searchText': row['abbreviation'].encode('utf-8'), 'filters' : [] }
            form_data['variables'] = variables

            yield scrapy.Request(
                url='https://www.smithsfoodanddrug.com/stores/api/graphql',
                method="POST",
                callback=self.parse_store,
                body=json.dumps(form_data),
                headers=headers
            )

            return

    def parse_store(self, response):
        stores = json.loads(response.body)
        stores = stores['data']['storeSearch']['stores']

        for store in stores:
            item = ChainItem()
            try:
                item['store_name'] = store['vanityName'].encode("utf-8")
            except:
                item['store_name'] = ''

            try:
                item['store_number'] = str(store['storeNumber'])
            except:
                item['store_number'] = ''

            try:
                item['address'] = store['address']['addressLine1'].encode("utf-8")
            except:
                item['address'] = ''

            item['address2'] = ""
            if store['phoneNumber'] is not None:
                item['phone_number'] = store['phoneNumber'].encode("utf-8")
            else:
                item['phone_number'] = ''

            item['city'] = store['address']['city'].encode("utf-8")
            item['state'] = store['address']['stateCode'].encode("utf-8")
            if item['state'] == "":
                item['state'] = store['address']['stateCode'].encode("utf-8")

            item['zip_code'] = store['address']['zip'].encode("utf-8")
            item['country'] = store['address']['countryCode'].encode("utf-8")
            item['latitude'] = str(store['latitude'])
            item['longitude'] = str(store['longitude'])

            item['store_hours'] = ''
          
            item['other_fields'] = ""
            item['coming_soon'] = 0

            if item["store_number"] in self.uid_list:
                continue
 
            self.uid_list.append(item['store_number'])

            yield item