import sqlite3
import requests
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
    head = rows[0].findAll('th')
    head = [item.text.strip() for item in head]
    head = [re.sub(r'(\[.*\])', '', item) for item in head]
    # ans.append(head)
    for row in rows:
        cols = row.findAll('td')
        cols = [item.text.strip() for item in cols]
        cols = [re.sub(r'(\[.*\])', '', item) for item in cols]
        ans.append([item for item in cols if item])

    return ans, head



def scrap_head():
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
    return head

def create_result(result):
    conn = get_connection()

    sql = ''' INSERT INTO acm(year,location,placing,squad,coach)
              VALUES(?,?,?,?,?) '''
    if len(result) != 5:
        result.append('')
    with conn:
        cur = conn.cursor()
        cur.execute(sql, result)
        a = cur.lastrowid
    cur.close()
    return a


def get_db_results():
    conn = get_connection()

    sql = ''' SELECT * FROM acm ;'''
    ans = None
    with conn:
        cur = conn.cursor()
        cur.execute(sql)
        ans = cur.fetchall()

    cur.close()
    return ans


url = 'https://ru.wikipedia.org/wiki/Университет_ИТМО'
database = r"C:\sqlite\db\lab3.db"

sql_create_acm_comp_table = """ CREATE TABLE IF NOT EXISTS acm (
                                        year integer PRIMARY KEY,
                                        location text NOT NULL,
                                        placing text NOT NULL,
                                        squad text NOT NULL,
                                        coach text  
                                    ); """





def get_connection():
    return create_connection(database)

def get_table_data():
    return scrap_data(url=url)