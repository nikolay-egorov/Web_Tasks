import requests
import urllib
import re
from bs4 import BeautifulSoup

response = requests.get('https://ru.wikipedia.org/wiki/Университет_ИТМО')

source = BeautifulSoup(response.content, "html.parser")

tables = source.findAll('table', attrs={"class": "standard"})

res = None
for table in tables:
    table_body = table.find('tbody')
    if re.match(r'^Место проведения финала' ,table_body.text, re.I) != 0:
        res = table_body


ans = []
rows = res.findAll('tr')
for row in rows:
    cols = row.findAll('td')
    cols = [item.text.strip() for item in cols]
    cols = [re.sub(r'(\[.*\])', '', item) for item in cols]
    ans.append([item for item in cols if item])

with open('2-res.txt', 'w', encoding="utf-8") as f:
    head = rows[0].findAll('th')
    head = [item.text.strip() for item in head]
    head = [re.sub(r'(\[.*\])', '', item) for item in head]
    f.write(str(head) + '\n')
    for line in ans:
        if line:
            f.write(str(line) + '\n')


