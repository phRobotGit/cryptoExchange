import os 
import pathlib
from re import A
from matplotlib import axis, use
from matplotlib.pylab import f
import pandas as pd 

class Report_platfrom():
    query_dict = {
        "user": 
            '''select t1.id, date(t1.ctime), t1.deleted_status, t2.ctime from 
                (select id, ctime, deleted_status from user where date(ctime)>"2023-07-26") t1 
                left join 
                (select from_uid, ctime from transaction where scene="trade") t2 
                on t1.id = t2.from_uid;
            ''', # 平台用户，及现货交易表， 粒度 交易
        "deposit": 
            '''select uid, symbol, amount, fee, real_fee, created_at from transaction_deposit_crypto;''', # 现货充值表, 粒度 交易
        "withdraw": 
            "select uid, symbol, amount, fee, real_fee, created_at from transaction_withdraw_crypto;", # 现货提现表， 粒度 交易
        "otc_trasfer": 
            '''select uid, coin_symbol, transfer_type, create_time,  amount from otc_transfer where status=1;''', # OTC转账表， 粒度 交易
        "co_postiion_fill": 
            '''select uid, sum(deal_money), sum(realized_amount), avg(fee_rate), sum(fee), side, date(ctime) 
               from co_position_fill 
               group by uid, date(ctime), side;''',
    } # 这里添加BD
    df_dict = {}

    
    def __init__(self) -> None:
        pass
    
    def get_data(self, connection) -> None:
        for k,v in self.query_dict.items():
            self.df_dict[k] = pd.read_sql(v, connection)

    
    def summary_report(self) -> None:
        pass
    
    def save_summary_report(self, save_path_root) -> None:
        pass 
