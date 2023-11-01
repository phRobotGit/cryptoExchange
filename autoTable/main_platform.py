#%%

import pathlib 
import datetime
import argparse
from configparser import ConfigParser
import os 
import pandas as pd 
import numpy as np 
import sys
from module.db.mysql import connect_to_db_mysql
from module.email.communicate import Email
from module.report.report_platfrom import Report_platfrom
from module.tool.dataType import AssetPool
from module.db.query import query_dict

# if __name__ == "__main__":
def main(config, params, env="dev"):
    query_dict = params["query_dict"]
    
    connection = {}
    for database in ["exchange", "partner", "futures"]:
        if database == "futures" and env == "prod":
            print(" use futures!! ")
            connection[database] = connect_to_db_mysql(
                username = config[f"common:mysqlDatabase"]["USER_FUTURE"],
                password = config[f"common:mysqlDatabase"]["PASSWORD_FUTURE"],
                host = config[f"common:mysqlDatabase"]["HOST_FUTURE"],
                port = config[f"common:mysqlDatabase"]["PORT_FUTURE"],
                database = database,
            ) # , "futures"
        connection[database] = connect_to_db_mysql(
            username = config[f"common:mysqlDatabase"]["USER"],
            password = config[f"common:mysqlDatabase"]["PASSWORD"],
            host = config[f"common:mysqlDatabase"]["HOST"],
            port = config[f"common:mysqlDatabase"]["PORT"],
            database = database,
        ) # , "futures"
    

    df_dict = {}
    for k,v in query_dict.items():
        database = k.split("|")[0]
        table = k.split("|")[1]
        query = v 
        df_dict[table] = pd.read_sql(query, connection[database])

    # 制作前置表格
    df = pd.concat([df_dict["money_deposit"], df_dict["money_withdraw"], df_dict["money_otc"]], axis=0)
    def f(df):
        df_in = df[df["transfer_type"].apply(lambda x: int(x) in (4,2))].copy()
        df_out = df[df["transfer_type"].apply(lambda x: int(x) in (3,1))].copy()
        return(pd.Series({
            "amount_in": df_in["amount"].sum(),
            "amount_out": df_out["amount"].sum(),
        }))
    df = df.groupby(["uid", "date", "symbol"]).apply(f).reset_index(drop=False)
    
    def f(df):
        # 把 symbol 和 account_in; account_out 做成一个 str symbol: amount
        # if sum(r["amount_in"])
        amount_in = ", ".join(df.apply(lambda r: f"{r["symbol"]}:{r["amount_in"]}", axis=1).tolist())
        amount_out = ", ".join(df.apply(lambda r: f"{r["symbol"]}:{r["amount_out"]}", axis=1).tolist())
        return(pd.Series({
            "入金": AssetPool(amount_in),
            "出金": AssetPool(amount_out)
        }))
    df_uid_date = df.groupby(["uid", "date"]).apply(f).reset_index(drop=False)

    def f(df):
        pass
    df_uid_date = pd.merge(df_uid_date, 
                           df_dict["position_fill"],
                           on=["uid", "date"], 
                           how="outer")

    
    # 制作表格
    def f(df):
        return(pd.Series({
            "新增注册用户": df.shape[0],
        })) 
    df_date = df_dict["user_info"].groupby("cdate").apply(f).reset_index(drop=False)
    df_date.rename(columns={"cdate":"date"}, inplace=True)
    
    
    def f(df):
        amount_out = np.sum(df["出金"].tolist())
        amount_in = np.sum(df["入金"].tolist())
        return( pd.Series({
            "出金": amount_in,
            "入金": amount_out,
            "净入金": amount_in - amount_out,
            "出金人数":sum(df["出金"].apply(lambda x: False if type(x)!=AssetPool else x.is_zero())),
            "入金人数":sum(df["入金"].apply(lambda x: False if type(x)!=AssetPool else x.is_zero())), 
            "交易量": df["deal_money"].sum(),
            "手续费": df["fee"].sum(),
            "手续费率": df["deal_money"].sum()/ df["fee"].sum(),
            "已实现收益": df["realized_amount"].sum(),
        }))
    df_date = pd.merge(df_date, 
                       df_uid_date.groupby("date").apply(f).reset_index(drop=False), 
                       on="date", 
                       how="outer")
    
    # 自动发送邮件
    today = datetime.date.today().strftime("%Y%m%d")
    email = Email(sender=config["common:email"]["sender"], 
                password=config["common:email"]["password"])

    save_root = pathlib.Path(f"result/平台业务日报_{today}")
    if not os.path.exists(save_root):
        os.makedirs(save_root)
    save_path = save_root / pathlib.Path(f"平台业务日报_{today}.xlsx")
    df_date.to_excel( save_path, index=False)
    l = [ i for i in config["common:email"]["receiver"].split(";") if len(i) > 0]
    email.send_email(receiver_list=  l, 
                    cc_list=  l,
                    subject= f"平台业务日报 {env} {today}".replace("prod",""),
                    text= "您好, 请查收平台业务报表。",
                    attachment_excel_path_list= list(save_root.glob("*.xlsx")),
                    )


if __name__ == "__main__":
    np.seterr(divide = "ignore", invalid="ignore") # Attention! Igonore warnings here!
    
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--environment", type=str, default="dev", help="please select environment in (dev, test, prod)")
        args = parser.parse_args(sys.argv[1:])
        environment = args.environment
    except:
        environment = "dev"
    
    config = ConfigParser(interpolation=None)
    config.read(pathlib.Path(f"config/config_{environment}.config"))
    params = ConfigParser()
    params.read(pathlib.Path(f"config/params.config"))
    
    table_needed_list = [
        "exchange|user_info",
        'exchange|money_deposit',
        'exchange|money_withdraw',
        'exchange|money_otc',
        'futures|position_fill'
        ]
    query_dict = { k:v for k,v in query_dict["sql"].items() if k in table_needed_list}
    params["query_dict"] = query_dict
    print("ready for main")
    main(config=config, params=params, env=environment)
    # python main_t1.py --environment dev