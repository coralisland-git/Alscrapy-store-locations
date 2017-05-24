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

class citizensbank(scrapy.Spider):
    name = 'citizensbank'
    domain = 'https://www.citizensbank.com'
    location_list = []
    history = []

    def __init__(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/cities.json'
        with open(file_path) as data_file:    
            self.location_list = json.load(data_file)

    def start_requests(self):
        init_url = 'https://www.citizensbank.com/apps/ApiProxy/BranchlocatorApi/api/BranchLocator'

        header = {
        	"Accept":"application/json, text/javascript, */*; q=0.01",
			"Accept-Encoding":"gzip, deflate, br",
			"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
			"X-Requested-With":"XMLHttpRequest"
        }

        frmdata = {
            	'RequestHeader[RqStartTime]': '2017-05-16T00:09:25.354Z',
                'coordinates[Latitude]': "41.2033216",
                'coordinates[Longitude]': "-77.1945247",
                'searchFilter[IncludeAtms]': 'false',
                'searchFilter[IncludeBranches]': 'false',
                'searchFilter[IncludeVoiceAssistedAtms]': 'false',
                'searchFilter[IncludeSuperMarketBranches]': 'false',
                'searchFilter[IncludeOpenNow]': 'false'
                }
        yield FormRequest(url=init_url, callback=self.body, headers=header, method='post', formdata=frmdata) 

    def body(self, response):
        with open('response.html', 'wb') as f:
			f.write(response.body)
       