#!/usr/bin/env python

import cgi
import cgitb
from lab_7.utils import *
cgitb.enable()


print("Content-type: text/html\n")
ans = get_table_data()
print("""<!DOCTYPE HTML>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Таблица результатов чемпионатов ACM ICPC</title>
        </head>
        <body>""")
print("<table><tbody")

a = 1
for row in ans:
    print('<tr>')
    for item in row:
        if a == 1:
            print('<th class="header">{}</th>'.format(item))
            a = 0
        else:
            print('<th >{}</th>'.format(item))
    print('</tr>')

print("</tbody></table>")
print("</body></html>")
