
#%%

from configparser import ConfigParser
import os 
import argparse
from tracemalloc import start
import pandas as pd 
import pathlib
import datetime
import numpy as np
from module.report.report_BD import report_BD
from module.db.mysql import connect_to_db_mysql
from module.email.communicate import Email
from module.web.server_socket import Server
import sys
import matplotlib.pyplot as plt
import loguru 
from apscheduler.schedulers.blocking import BlockingScheduler

def main(argv):
    # read config and params
    # try:
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", type=str, default="dev", help="please select environment in (dev, test, prod)")
    args = parser.parse_args(argv[1:])
    environment = args.environment

    config = ConfigParser(interpolation=None)
    config.read(pathlib.Path(f"config/config_{environment}.config"))
    params = ConfigParser()
    params.read(pathlib.Path("config/params.config"))

    # connect to the mysql database
    connection = connect_to_db_mysql(
        username = config["common:mysqlDatabase"]["USER"],
        password = config["common:mysqlDatabase"]["PASSWORD"],
        host = config["common:mysqlDatabase"]["host"],
        port = config["common:mysqlDatabase"]["PORT"],
        database = "partner",
    )


    # Part1: 生成日报
    # 获取当日日期
    if config["common:environment"]["environment"] =="dev":
        today = datetime.datetime(2023,5,17).strftime("%Y%m%d")
        start_date = "20230501"
        end_date = today
    elif config["common:environment"]["environment"] in ("test", "prod"):
        today = datetime.date.today().strftime("%Y%m%d")
        start_date = "20230901"
        end_date = today
        
    if today:
        r = report_BD(start_date=start_date, end_date=end_date)
        r.get_data(connection=connection)
        r.summary_report()
        r.save_summary_report(save_path_root=pathlib.Path(f"result/商务BD报表/{start_date}_{end_date}"))
        # 11:09 11：17 13：05

        
    # 自动发送邮件
    email = Email(sender=config["common:email"]["sender"], 
                password=config["common:email"]["password"])

    pathlib.Path(f"result/商务BD报表")
    l = [ i for i in config["common:email"]["receiver"].split(";") if len(i) > 0]
    email.send_email(receiver_list=  l, 
                    cc_list=  l,
                    subject= f"商务BD日报 {environment} {today}".replace("prod",""),
                    text= "您好, 请查收商务BD报表。",
                    attachment_excel_path_list= list(pathlib.Path(f"result/商务BD报表/{start_date}_{end_date}").glob("*.xlsx"))
                    )
    # 13:20
    # %%
    
    
if __name__ == "__main__":
    main(sys.argv)
    # 日志
    # loguru.logger.add(pathlib.Path("log/main_bd.log"), rotation="500 MB")
    # loguru.logger.info("info")
    # loguru.logger.warning("warning")
    # loguru.logger.error("error")
    # loguru.logger.debug("debug")
    # loguru.logger.critical("critical error")
    
    # 启动web服务，监听8080端口
    # server = Server(host="", port=8080)
    # server.listening() # 开始监听
    
    # 定时生成报表
    # scheduler = BlockingScheduler()
    # scheduler.add_job(lambda x: main(sys.argv), 'cron', 
                    #   hour=9, minute=15, second=0,
                      # end_date = datetime.datetime(2023,2,28))
    # )
    # scheduler.start()
    # main(sys.argv)
    
