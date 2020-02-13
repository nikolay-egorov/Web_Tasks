import pymysql
import requests
import re
from bs4 import BeautifulSoup

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
    for row in rows:
        cols = row.findAll('td')
        cols = [item.text.strip() for item in cols]
        cols = [re.sub(r'(\[.*\])', '', item) for item in cols]
        ans.append([item for item in cols if item])

    return ans


def connect():
    """ Connect to the MySQL database server """
    conn = None
    try:
        # read connection parameters
        params = config(section='mysql')

        # connect to the PostgreSQL server
        print('Connecting to the MYSQL database...')
        conn = pymysql.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('MYSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the communication with the PostgreSQL
        cur.close()
        return conn
    except (Exception, pymysql.DatabaseError) as error:
        print(error)


def create_table(conn, create_table_sql):
    try:

        cur = conn.cursor()
        cur.execute(create_table_sql)
        cur.close()
        conn.commit()
    except (Exception, pymysql.DatabaseError) as error:
        print(error)


def create_result_row(conn, result):
    sql = ''' INSERT INTO acm(year, location, place, squad, coach)
              VALUES (%s,%s,%s,%s,%s) '''
    conn = None

    try:
        # read database configuration
        params = config()
        conn = pymysql.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        if len(result) != 5:
            result.append('')
        cur.execute(sql, result)
        conn.commit()
    except (Exception, pymysql.DatabaseError) as error:
        print(error)
    return cur.lastrowid


sql_create_acm_comp_table = """ CREATE TABLE IF NOT EXISTS acm (
year integer PRIMARY KEY,
location text NOT NULL,
place text NOT NULL,
squad text NOT NULL,
coach text); """

url = 'https://ru.wikipedia.org/wiki/Университет_ИТМО'

res = scrap_data(url)

conn = connect()
if conn is not None:
    create_table(conn, sql_create_acm_comp_table)
else:
    print("Error! cannot create the database connection ")

with conn:
    for row in res:
        if row:
            create_result_row(conn, row)

if conn:
    conn.close()
