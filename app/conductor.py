from os import path, environ, walk
import subprocess
import requests
from tempfile import NamedTemporaryFile
import pyodbc
import logging

logging.basicConfig(level=logging.INFO)

CONDUCTOR_PWD = path.dirname(path.abspath(__file__))
SQL_SERVER_URL = environ.get('SQL_SERVER_URL', None)
SQL_SERVER_DATABASE = environ.get('SQL_SERVER_DATABASE', 'parking_prediction')
SQL_SERVER_USERNAME = environ.get('SQL_SERVER_USERNAME', 'padmin')
SQL_SERVER_PASSWORD = environ.get('SQL_SERVER_PASSWORD', None)
DISCOVERY_URL = environ.get('DISCOVERY_URL', 'https://data.smartcolumbusos.com/api/v1')
DISCOVERY_DATA_LIMIT = environ.get('DISCOVERY_DATA_LIMIT', False)


def _bcp_shell_command(table, file_path, extra_arguments=[]):
    command_args = [
        'bcp',
        table, 'in', file_path,
        '-S', SQL_SERVER_URL,
        '-c',
        '-U', SQL_SERVER_USERNAME,
        '-d', SQL_SERVER_DATABASE,
        '-P', SQL_SERVER_PASSWORD
        ] + extra_arguments

    logging.debug(f"running bcp command: {' '.join(command_args)}")
    _process = subprocess.run(command_args)


def _bulk_copy_ref_file(table):
    _bcp_shell_command(table, f"{CONDUCTOR_PWD}/../ref_data/{table}.dat")


def _bulk_copy_csv_file(table, file_path):
    _bcp_shell_command(table, file_path, ['-F', '2', '-t', ','])


def _download_file(url):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with NamedTemporaryFile(delete=False) as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)

    return f.name


def _load_dataset(organization, dataset, table):
    limit = f"?limit={DISCOVERY_DATA_LIMIT}" if DISCOVERY_DATA_LIMIT else ''
    file_path = _download_file(f"{DISCOVERY_URL}/organization/{organization}/dataset/{dataset}/query{limit}")
    _bulk_copy_csv_file(table, file_path)


def _conn_string():
    return 'Driver={ODBC Driver 17 for SQL Server};Server=' \
        + SQL_SERVER_URL + ';Database=' + SQL_SERVER_DATABASE \
        + ';UID=' + SQL_SERVER_USERNAME + ';PWD=' + SQL_SERVER_PASSWORD \
        + ';'


def _run_statement(conn, statement):
    logging.debug(f"running statement {statement}")
    with conn.cursor() as cur:
        try:
            return cur.execute(statement)
        except pyodbc.ProgrammingError as e:
            (code, _message) = e.args
            if code != '42S02': # object not found (typically thrown by DROP on a missing table)
                logging.error(e)
                raise e
            else:
                logging.warn(f"a table was not found: {e}")
                return e


def _run_sql_file(file_name):
    logging.debug(f"running sql file {file_name}")
    conn = pyodbc.connect(_conn_string(), autocommit=True)

    with open(file_name, 'r') as script:
        sqlScript = script.read().strip()
        statements = sqlScript.split(';')

        legit_statements = filter(lambda s: s.strip() != '', statements)
        _results = list(map(lambda s: _run_statement(conn, s), legit_statements))

    conn.close()


def load_data():
    _run_sql_file(f"{CONDUCTOR_PWD}/../sql/00_ref_tables.sql")

    _bulk_copy_ref_file('ref_meter')
    _bulk_copy_ref_file('ref_zone')
    _bulk_copy_ref_file('ref_semihourly_timetable')
    _bulk_copy_ref_file('ref_calendar_parking')

    _run_sql_file(f"{CONDUCTOR_PWD}/../sql/01_staging_tables.sql")

    _load_dataset('ips_group', 'parking_meter_inventory_2020', 'stg_ips_group_parking_meter_inventory_2020')
    _load_dataset('ips_group', 'parking_meter_transactions_2018', 'stg_parking_tranxn_2018')
    _load_dataset('ips_group', 'parking_meter_transactions_2020', 'stg_parking_tranxn_2019')
    _load_dataset('ips_group', '7ab08634_3eda_4b05_a754_5eb6cab31326', 'stg_parking_tranxn_2015_2017')
    _load_dataset('parkmobile', 'parking_meter_transactions_2020', 'stg_parkmobile')


def _run_etl_for_ips():
    for root, _dirs, files in walk(f"{CONDUCTOR_PWD}/../sql/ips", topdown=True):
        files.sort()
        for name in files:
            _run_sql_file(path.join(root, name))


def _run_etl_for_park_mobile():
    for root, _dirs, files in walk(f"{CONDUCTOR_PWD}/../sql/park_mobile", topdown=True):
        files.sort()
        for name in files:
            _run_sql_file(path.join(root, name))


def _run_aggregation():
    _run_sql_file(f"{CONDUCTOR_PWD}/../sql/16_aggregate_occupancy.sql")


def run_etl():
    _run_etl_for_ips()
    _run_etl_for_park_mobile()
    _run_aggregation()

load_data()
run_etl()