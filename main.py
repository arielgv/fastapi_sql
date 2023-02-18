from fastapi import FastAPI
import requests
import pymysql
import json

app = FastAPI()
@app.get('/')
def mainhome():
    main={'Main Home' : 'For procedure go to /docs'}
    return main
@app.get("/suitecrm")
async def get_leads():
    """
    This Get request obtain access to SuiteCrm and obtain the Session ID, and achieve to fetch the fields obtained and filtered by Phone Work, First name and Last name
    """

# OBTAINING THE SESSION ID 

    session = requests.Session()

# Send a login request to the SuiteCRM API to obtain a session ID
    url = 'https://suitecrmdemo.dtbc.eu/service/v4/rest.php'
    payload = {'method': 'login', 'input_type': 'JSON', 'response_type': 'JSON', 'rest_data': json.dumps({'user_auth': {'user_name': 'Demo', 'password': 'f0258b6685684c113bad94d91b8fa02a'}, 'application_name': 'RestTest'})}
    response = session.post(url, data=payload)

# Check if the login was successful
    response_json = response.json()
    if 'id' not in response_json:
        print('Failed to log in to SuiteCRM API')
    session_id = response_json['id']

    # Using id session to fetch the fields.

    url = 'https://suitecrmdemo.dtbc.eu/service/v4/rest.php'
    payload = {
        'method': 'get_entry_list',
        'input_type': 'JSON',
        'response_type': 'JSON',
        'rest_data': json.dumps({
            'session': session_id,
            'module_name': 'Leads',
            'query': '',
            'order_by': '',
            'offset': '',
            'select_fields': ['phone_work', 'first_name', 'last_name'],
            'link_name_to_fields_array': [],
            'max_results': '',
            'deleted': ''
        })
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=payload, headers=headers)
    theleads = response.json()['entry_list']
    return theleads 

#SETTING UP THE DATABASE AND TABLE

@app.post("/createdb")
def create_database():
    """
    This endpoint creates a database called 'leads_db' in Sql.
    """
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='yourdbpassword'
    )
    cur = conn.cursor()
    cur.execute('CREATE DATABASE IF NOT EXISTS leads_db')
    conn.commit()
    cur.close()
    conn.close()

@app.post('/createtable')
def create_table():
    """
    This endpoint creates a table needed to initiate the insertion of data. it's configured to access as a root user.
    """
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='yourdbpassword',
        db='leads_db'
    )
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INT NOT NULL AUTO_INCREMENT,
            phone_work VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            PRIMARY KEY (id)
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

#STORING LEADS DATA ON MYSQL. it uses the data returned in the function "get_leads".
@app.post('/storeleads')
def store_leads():
    """
    This endpoint will store the leads into the leads table in the Database
    """
    session = requests.Session()

# Send a login request to the SuiteCRM API to obtain a session ID
    url = 'https://suitecrmdemo.dtbc.eu/service/v4/rest.php'
    payload = {'method': 'login', 'input_type': 'JSON', 'response_type': 'JSON', 'rest_data': json.dumps({'user_auth': {'user_name': 'Demo', 'password': 'f0258b6685684c113bad94d91b8fa02a'}, 'application_name': 'RestTest'})}
    response = session.post(url, data=payload)

# Check if the login was successful
    response_json = response.json()
    if 'id' not in response_json:
        print('Failed to log in to SuiteCRM API')
    session_id = response_json['id']

    # Using id session to fetch the fields.

    url = 'https://suitecrmdemo.dtbc.eu/service/v4/rest.php'
    payload = {
        'method': 'get_entry_list',
        'input_type': 'JSON',
        'response_type': 'JSON',
        'rest_data': json.dumps({
            'session': session_id,
            'module_name': 'Leads',
            'query': '',
            'order_by': '',
            'offset': '',
            'select_fields': ['phone_work', 'first_name', 'last_name'],
            'link_name_to_fields_array': [],
            'max_results': '',
            'deleted': ''
        })
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=payload, headers=headers)
    theleads = response.json()['entry_list']

    #From here , leads go to the database

    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='yourdbpassword',
        db='leads_db'
    )
    cur = conn.cursor()
    for lead in theleads:
        phone_work = lead['name_value_list']['phone_work']['value']
        first_name = lead['name_value_list']['first_name']['value']
        last_name = lead['name_value_list']['last_name']['value']
        cur.execute(f"INSERT INTO leads (phone_work, first_name, last_name) VALUES ('{phone_work}', '{first_name}', '{last_name}')")
    conn.commit()
    cur.close()
    conn.close()


#Integrate Bitcoin-USD prices API into FastAPI   
# With this new endpoint in FastAPI , it returns the current bitcoin-usd price
@app.get('/btc-usd-price')
def get_btc_usd_price():
    """
    This endpoint is working with a remote api , it retrieves the actual value of a Bitcoin
    """
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
    response = requests.get(url)
    btc_usd_price = response.json()['bitcoin']['usd']
    return {'btc_usd_price': btc_usd_price}
