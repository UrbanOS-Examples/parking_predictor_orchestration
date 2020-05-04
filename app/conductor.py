from os import path, environ
import subprocess
import requests
from tempfile import mkstemp
import pyodbc

CONDUCTOR_PWD = path.basename(path.abspath(__file__))
SQL_SERVER_URL = environ.get('SQL_SERVER_URL', None)
SQL_SERVER_DATABASE = environ.get('SQL_SERVER_DATABASE', 'parking_prediction')
SQL_SERVER_USERNAME = environ.get('SQL_SERVER_USERNAME', 'padmin')
SQL_SERVER_PASSWORD = environ.get('SQL_SERVER_PASSWORD', None)
DISCOVERY_URL = environ.get('DISCOVERY_URL', 'https://data.smartcolumbusos.com/api/v1')


def _bcp_shell_command(table, file_path=f"{CONDUCTOR_PWD}/ref_data/{table}.dat", extra_arguments=[]):
    process = subprocess.run([
        'bcp',
        table, 'in', file_path,
        '-S', SQL_SERVER_URL,
        '-c',
        '-U', SQL_SERVER_USERNAME,
        '-d', SQL_SERVER_DATABASE,
        '-P', SQL_SERVER_PASSWORD
        ] + extra_arguments
    )


def _bulk_copy_csv_file(table, file_path):
    _bcp_shell_command(table, file_path, ['-F', '2', '-c', '-t', ','])


def _download_file(url):
    file_path = mkstemp()
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)

    file_path


def _load_dataset(organization, dataset, table):
    file_path = _download_file(f"{DISCOVERY_URL}/organization/{organization}/dataset/{dataset}/query")
    _bulk_copy_csv_file(table, file_path)

def _conn_string():
    'Driver={ODBC Driver 17 for SQL Server};Server=' \
    + SQL_SERVER_DATABASE + ';Database=' + SQL_SERVER_DATABASE \
    + ';UID=' + SQL_SERVER_USERNAME + ';PWD=' + SQL_SERVER_PASSWORD \
    + ';'

def _run_sql_file(file_name):
    conn = pyodbc.connect(_conn_string(), autocommit=True)

    with open(file_name,'r') as script:
        sqlScript = script.readlines()
        for statement in sqlScript.split(';'):
            with conn.cursor() as cur:
                cur.execute(statement)

    conn.close()

def load_data():
    _bcp_shell_command('ref_meter')
    _bcp_shell_command('ref_zone')
    _bcp_shell_command('ref_semihourly_timetable')
    _bcp_shell_command('ref_calendar_parking')

    _load_dataset('ips_group', 'parking_meter_inventory_2020', 'stg_ips_group_parking_meter_inventory_2020')
    _load_dataset('ips_group', 'parking_meter_transactions_2018', 'stg_parking_tranxn_2018')
    _load_dataset('ips_group', 'parking_meter_transactions_2020', 'stg_parking_tranxn_2019')
    _load_dataset('ips_group', '7ab08634_3eda_4b05_a754_5eb6cab31326', 'stg_parking_tranxn_2015_2017')
    _load_dataset('parkmobile', 'parking_meter_transactions_2020', 'stg_parkmobile')
