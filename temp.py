#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import openpyxl
from io import BytesIO
import urllib2
import re
import json
import requests
from bs4 import BeautifulSoup

url = 'https://www.cian.ru/rent/flat/177362276/'
r = requests.get(url)
html = r.text
soup = BeautifulSoup(html, 'html.parser')

# print soup.prettify(encoding='utf-8')

# for item in soup.find_all(True):   # 'img'
#     print item.prettify(encoding='utf-8')

for item in soup.find_all(name='script', type="text/javascript"):
    script_code = item.prettify(encoding='utf-8')
    for line in script_code.splitlines():
        if "['offer-card']" in line:
            offer_card = line.split(' = ')[1]
            if offer_card[-1]==';':
                offer_card = offer_card[:-1]

print json.dumps(json.loads(offer_card), indent=4, sort_keys=True)

    # if "window._cianConfig['offer-card']" in item.prettify(encoding='utf-8'):
    #     # for line in
    #     print item.prettify(encoding='utf-8')

# ===========================================================
# site = 'https://www.cian.ru/rent/flat/177362276/'
#
# response = requests.get(site)
#
# soup = BeautifulSoup(response.text, 'html.parser')
# img_tags = soup.find_all('img')
# urls = [img['src'] for img in img_tags]
#
# for url in urls:
#     print url
#     filename = re.search(r'/([\w_-]+[.](jpg|gif|png|jpeg))$', url)
#     with open(filename.group(1), 'wb') as f:
#         if 'http' not in url:
#             # sometimes an image source can be relative
#             # if it is provide the base url which also happens
#             # to be the site variable atm.
#             url = '{}{}'.format(site, url)
#         response = requests.get(url)
#         f.write(response.content)


# path = 'https://www.cian.ru/export/xls/offers/?deal_type=rent&engine_version=2&offer_type=flat&region=1&room1=1&room2=1&room3=1&room4=1&room5=1&type=4'
# path = 'https://www.cian.ru/rent/flat/177362276/'
# res = requests.get(path).content
# # wb = openpyxl.load_workbook(filename=BytesIO(res), read_only=True, keep_vba=False, data_only=True)
# # ws = wb.active
# #
# # for row in ws.rows:
# #     print row[0]
#
# soup = BeautifulSoup(res, "html.parser")
#
# print repr(soup)
# # print soup.prettify()
# for child in soup.children:
#     print child
