import sys 
import os
from query import query_dict
from configparser import ConfigParser
import sqlalchemy
import pandas as pd 
import pathlib

def connect_to_db_mysql(username, password, host, port, database) -> sqlalchemy.Connection:
    # Connect to the database    
    engine = sqlalchemy.create_engine(sqlalchemy.URL.create(
        "mysql+pymysql",
        username=username,
        password=password,  
        host=host,
        port=port,
        database=database,
    ))
    return engine.connect()

environment = "dev"

config = ConfigParser(interpolation=None)
config.read(pathlib.Path(f"config/config_{environment}.config"))
params = ConfigParser()
params.read(pathlib.Path(f"config/params.config"))

connection = {}
for database in ("exchange", "futures", "partner"):
    connection[database] = connect_to_db_mysql(
        username = config[f"common:mysqlDatabase"]["USER"],
        password = config[f"common:mysqlDatabase"]["PASSWORD"],
        host = config[f"common:mysqlDatabase"]["HOST"],
        port = config[f"common:mysqlDatabase"]["PORT"],
        database = database,
    )

df_dict = {}
for k,v in query_dict.items():
    database = k.split("|")[0]
    table = k.split("|")[1]
    query = v 
    df_dict[table] = pd.read_sql(query, connection[database])