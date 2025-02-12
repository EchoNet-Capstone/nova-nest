import os
import psycopg

user = os.environ["BDB_USER"]
host = os.environ["BDB_HOST"]
dbname = os.environ["BDB_DB"]

def test_connect():
    # Connect to an existing database
    with psycopg.connect(f'host={host} user={user} dbname={dbname}') as conn:
        print("connected successfully!")