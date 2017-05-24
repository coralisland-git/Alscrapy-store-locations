import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from lxml import html
import tokenize
import token
from StringIO import StringIO

class tacomayo(scrapy.Spider):
    name = 'tacomayo'
    domain = 'http://www.tacomayo.com'
    request_url = 'http://www.tacomayo.com/locations.aspx'

    def start_requests(self):
        url = self.request_url
        yield scrapy.Request(url=url, callback=self.body)

    def body(self, response):
        if response.body:
            data = ''
            scripts = response.xpath('//script/text()').extract()
            for script in scripts:
                if script.find('var locations = ') != -1:
                    data = script
            data = data.split('var locations = {')[1].split('};')[0].strip()
            data = '{' + data + '}'
            data = data.replace('new google.maps.LatLng(', '[').replace(')', ']')
            data_list = data.split('"point":')
            store_list = json.loads(self.fixLazyJson(data))
            item = ChainItem()
            for store in store_list:
                item['store_number'] = store
                item['address'] = store_list[store]['address']
                item['city'] = store_list[store]['city']
                item['state'] = store_list[store]['state']
                item['zip_code'] = store_list[store]['zip']
                item['phone_number'] = store_list[store]['phone']
                item['coming_soon'] = '0'
                item['country'] = 'United States'
                item['latitude'] = store_list[store]['point'][0]
                item['longitude'] = store_list[store]['point'][1]
                yield item
        else:
            pass
 
    def fixLazyJson (self, in_text):
        tokengen = tokenize.generate_tokens(StringIO(in_text).readline)

        result = []
        for tokid, tokval, _, _, _ in tokengen:
            # fix unquoted strings
            if (tokid == token.NAME):
                if tokval not in ['true', 'false', 'null', '-Infinity', 'Infinity', 'NaN']:
                    tokid = token.STRING
                    tokval = u'"%s"' % tokval

            # fix single-quoted strings
            elif (tokid == token.STRING):
                if tokval.startswith ("'"):
                    tokval = u'"%s"' % tokval[1:-1].replace ('"', '\\"')

            # remove invalid commas
            elif (tokid == token.OP) and ((tokval == '}') or (tokval == ']')):
                if (len(result) > 0) and (result[-1][1] == ','):
                    result.pop()

            # fix single-quoted strings
            elif (tokid == token.STRING):
                if tokval.startswith ("'"):
                    tokval = u'"%s"' % tokval[1:-1].replace ('"', '\\"')

            result.append((tokid, tokval))

        return tokenize.untokenize(result)

    

    