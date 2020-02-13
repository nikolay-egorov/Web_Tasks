import json

import requests
import re
from bs4 import BeautifulSoup
from pymongo import MongoClient
from lab_4.config import config


def scrap_data(url):
    response = requests.get(url)

    source = BeautifulSoup(response.content, "html.parser")
    tables = source.findAll('table', attrs={"class": "standard"})

    res = None
    for table in tables:
        table_body = table.find('tbody')
        if re.match(r'^Место проведения финала', table_body.text, re.I) != 0:
            res = table_body

    ans = []
    rows = res.findAll('tr')
    head = rows[0].findAll('th')
    head = [item.text.strip() for item in head]
    head = [re.sub(r'(\[.*\])', '', item) for item in head]
    for row in rows:
        cols = row.findAll('td')
        cols = [item.text.strip() for item in cols]
        cols = [re.sub(r'(\[.*\])', '', item) for item in cols]
        ans.append([item for item in cols if item])

    return ans,head


def initMongoDBConn(component=None):

    conf = config(section='mongodb')
    try:
        client = MongoClient('{host}:{port}'.format(host=conf['host'], port=conf['port']))
        mongodb_conn = client[component]
    except ValueError as e:
        print('MongoDB connection to {host} is refused'.format(host=conf['host']))


    return mongodb_conn



def to_json(ans, header):
    val = filter(None, [x for x in ans] )
    out = [dict(zip(header, v)) for v in val] if header else [*val]
    return json.loads(json.dumps(out, ensure_ascii=False))


url = 'https://ru.wikipedia.org/wiki/Университет_ИТМО'

res, header = scrap_data(url)
ans = []

conn = initMongoDBConn('acm')
acm = conn.acm

for row in res:
    if len(row) != 5:
        row.append('')

res_json = to_json(res[1:], header)



for x in res_json:
    if x:
        a = 2
        test = acm.insert_one(x)

