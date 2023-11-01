#%%

import sqlalchemy
import dataclasses 
import pandas as pd 

# @dataclasses.dataclass
# class connection(sqlalchemy.Connection):    
#     connector: sqlalchemy.Connection
    
#     def retrive_data()

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

# host = "rds-test.ciolygcdjvw2.ap-east-1.rds.amazonaws.com"
# port = 3306
# username = "exchange"
# password = "exo2It9EqIi7"
# database = "partner"

# s = sqlalchemy.URL.create(
#         "mysql+pymysql",
#         username=username,
#         password=password,  
#         host=host,
#         port=port,
#         database=database,
#     )
# engine = sqlalchemy.create_engine(s)
# connection = engine.connect()

# pd.read_sql(
#             "select uid, sum(amount), biz_type, day_time from user_usdt_record group by uid, day_time, biz_type;",
#             connection
# ) 

# def 

# web-sokit 
# 监听web页面，存活探测  port: 8080 
# 打日志 
# 定时触发，