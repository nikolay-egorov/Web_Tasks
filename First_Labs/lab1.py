import requests
import urllib
import re

response = requests.get('https://ru.wikipedia.org/wiki/Университет_ИТМО')

# matchObj = re.findall(r'<tbody>(.+)\n<th>Год\n</th>(.*?)</tr>(.*?)</tbody>', response.text , re.M | re.I | re.S)
# matchObj = re.findall(r'<table class="standard">(.+)\n<th>Год\n</th>(.*?)</tr>(.*?)</table>', response.text , re.M | re.I | re.S)
matchObj = re.findall(r'^<table class="standard">(.*)(?=<tr>\n<th>Год\n</th>\n)(.*)</table>(?=\n<h3>)',response.text, re.M | re.I | re.S  )

data = (str(matchObj[0][1]))


headers = str(re.findall(r'^<table class="standard">(.*)(?=<tr>\n<th>Год\n</th>\n)(.*?)</tr>(.*?)(?=\n<h3>)', response.text,
                     re.M | re.I | re.S)[0][1]).replace('\n', '')

spans_value = re.findall(r'<span(.*?)(?="data-sort-value=")(.*)\n</span>' , data, re.IGNORECASE | re.DOTALL)

spans_cities = re.findall(r'<span [^>]*data-sort-value=.*(?=(.*))', data, re.IGNORECASE) #only cities, not working
test_reg = re.findall(r'<span .* (?=[^>]*data-sort-value=).*title=(?=(.*))(.*)</span>', data, re.IGNORECASE)


countries = re.findall(r'<span class=.*data-sort-value ?=(.*?)><span .*', data, re.IGNORECASE) #OK



table_header = [x.strip().lower() for x in re.findall("<th(?!ead)[^>]*>(.*?)<\/th>", headers)]
patt = re.compile("<td[^>]*>(.*?)<\/td>")
row = re.findall("<tr[^>]*>(.*?)<\/tr>", data, re.S)

for i in range(0, len(countries)):
    row[i+1] = re.sub(r'<span .*</span>', countries[i],row[i+1])
    row[i+1] = re.sub(r'<sup .*</sup>', '', row[i+1])
    row[i] = re.sub('<.*?>', '', row[i])

row[-1] = re.sub('<.*?>', '', row[-1])

row = [re.sub('\n', '\t',x) for x in row]



with open('1-res.txt', 'w',encoding="utf-8") as f:
    for line in row:
        f.write(str(line)+ '\n')

exit(0)





# splited_data = re.split(r'</tr>', data, flags=re.I)
# for i in range(0, len(countries)):
#     splited_data[i+1] = re.sub(r'<span .*</span>', countries[i], splited_data[i + 1])
#
#
# s = ""
# for x in splited_data:
#     s+=str(x)






# val = filter(None, [patt.findall(x) for x in row])
# out = [dict(zip(table_header, v)) for v in val] if table_header else [*val]
# print(out)
