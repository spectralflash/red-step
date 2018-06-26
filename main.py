#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fake_useragent import UserAgent
import json
import sys
import time
import requests
from bs4 import BeautifulSoup
import sqlite3
from sqlite3 import Error

'''
база объявлений
[+] в бесконечном цикле писать объявления с циана с последовательными ID в базу sqlite, одна запись - одна строка-json
    - обход капчи через прокси //
    - либо эмуляция клика через Selenium (и тогда парсинг через Selenium с куками)
- выделить ключевые поля, писать их отдельно
- фильтровать объявления, не писать ненужные (продажа, краткосрочная аренда)

анализ схожести объявлений (отдельный поток?)
- все критерии сравнения должны быть вынесены в отдельные поля в БД: адрес, описание, thumbnails
- каждое новое объявление: искать похожие сначала по адресу, потом (если адрес совпадает) по дополнительным критериям
- сравнение адреса (подключить API?)
- сравнение текстового описания
- сравнение картинок
- писать в базу, только если в ней еще нет похожего объявления

нотификация
- если объявление попало в БД, выводим на экран
'''

CIAN_COLD_START_ID = 177362276
CIAN_URL = 'https://www.cian.ru/rent/flat/'


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def add_cian_ad(conn, cian_ad_entry):
    sql = ''' INSERT INTO cian_ads(cian_id,cian_ad)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, cian_ad_entry)
    return cur.lastrowid


def get_last_cian_id(conn):
    cur = conn.cursor()
    cur.execute("SELECT max(id) FROM cian_ads")
    id = cur.fetchone()[0]
    if id is None:
        cian_id = CIAN_COLD_START_ID
    else:
        cur.execute("SELECT * FROM cian_ads WHERE id=?", (id,))
        cian_id = cur.fetchone()[1]
    return cian_id


def get_cian_ad(cian_id):
    url = CIAN_URL + str(cian_id)
    headers = {'User-Agent':str(ua.random)}
    r = requests.get(url, headers=headers)
    print 'Response: ' + str(r.status_code)
    if r.status_code == 404:
        return None
    # print 'Encoding: ' + r.encoding
    soup = BeautifulSoup(r.text, 'html.parser')

    for item in soup.find_all(name='script', type="text/javascript"):
        script_code = item.prettify(encoding='utf-8')
        if 'onloadCaptcha' in script_code:
            print script_code
            sys.exit('Captcha')
        for line in script_code.splitlines():
            if "['offer-card']" in line:
                offer_card = line.split(' = ')[1]
                if offer_card[-1]==';':
                    offer_card = offer_card[:-1]
                return offer_card
            else:
                offer_card = None
    print 'Offer card not found'
    print 'Headers: ' + repr(headers)
    print 'Soup: ' + repr(soup)
    print 'Soup decoded: ' + repr(soup).decode('string-escape')
    return offer_card


if __name__ == '__main__':

    ua = UserAgent()
    db="pythonsqlite.db"

    sql_create_cian_ads_table = """ CREATE TABLE IF NOT EXISTS cian_ads (
                                        id integer PRIMARY KEY,
                                        cian_id integer,
                                        cian_ad text
                                    ); """

    conn = create_connection(db)
    conn.text_factory = str

    if conn is not None:
        create_table(conn, sql_create_cian_ads_table)
    else:
        print("Error! cannot create the database connection.")

    with conn:
        # ad1 = (177362276, 'test string 1')
        # ad_id = add_cian_ad(conn, ad1)

        id = get_last_cian_id(conn)
        id += 1
        print 'Starting from Cian ID: ' + str(id)

        while True:
            print 'Getting: ' + CIAN_URL + str(id)
            ad = get_cian_ad(id)
            if ad:
                ad_id = add_cian_ad(conn, (id, ad))
                conn.commit()
                print 'Cian ad added to DB, internal id: ' + str(ad_id)
            else:
                print 'Unable to parse Cian ad'
            time.sleep(15)
            id += 1



# url = 'https://www.cian.ru/rent/flat/177362276/'
# r = requests.get(url)
# html = r.text
# soup = BeautifulSoup(html, 'html.parser')
#
#
# for item in soup.find_all(name='script', type="text/javascript"):
#     script_code = item.prettify(encoding='utf-8')
#     for line in script_code.splitlines():
#         if "['offer-card']" in line:
#             offer_card = line.split(' = ')[1]
#             if offer_card[-1]==';':
#                 offer_card = offer_card[:-1]
#
# print offer_card
# # print json.dumps(json.loads(offer_card), indent=4, sort_keys=True)
#
