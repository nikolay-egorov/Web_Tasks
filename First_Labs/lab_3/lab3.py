import sqlite3
import requests
import urllib
import re
from bs4 import BeautifulSoup


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)


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
    # head = rows[0].findAll('th')
    # head = [item.text.strip() for item in head]
    # head = [re.sub(r'(\[.*\])', '', item) for item in head]
    # ans.append(head)
    for row in rows:
        cols = row.findAll('td')
        cols = [item.text.strip() for item in cols]
        cols = [re.sub(r'(\[.*\])', '', item) for item in cols]
        ans.append([item for item in cols if item])

    return ans


def create_result(conn, result):
    sql = ''' INSERT INTO acm(year,location,placing,squad,coach)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    if len(result) != 5:
        result.append('')
    cur.execute(sql, result)
    return cur.lastrowid


def get_results(conn):
    sql = ''' SELECT * FROM acm ;'''
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()


url = 'https://ru.wikipedia.org/wiki/Университет_ИТМО'
database = r"C:\sqlite\db\lab3.db"

sql_create_acm_comp_table = """ CREATE TABLE IF NOT EXISTS acm (
                                        year integer PRIMARY KEY,
                                        location text NOT NULL,
                                        placing text NOT NULL,
                                        squad text NOT NULL,
                                        coach text  
                                    ); """

res = scrap_data(url)


conn = create_connection(database)

# create table
# if conn is not None:
#     create_table(conn, sql_create_acm_comp_table)
# else:
#     print("Error! cannot create the database connection ")

# insert values
with conn:
    # for row in res:
    #     if row:
    #         create_result(conn,row)

    ans = get_results(conn)
    a =1
    conn.commit()
if conn:
    conn.close()
