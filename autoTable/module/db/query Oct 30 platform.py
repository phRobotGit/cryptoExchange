query_sql_dict = {
    #"database|pd_name": "query"
    "exchange|user_info": "select id, date(ctime) as cdate, country_code,reg_ip, deleted_status, deleted_time, deleted_reason from user;",
    "exchange|money_deposit":
        '''
        select uid, date(created_at) as date, 4 as transfer_type,
        symbol, sum(amount) as amount, sum(fee) as fee, 
        sum(real_fee) as real_fee
        from transaction_deposit_crypto
        group by uid, date(created_at), symbol;
        '''.replace("\n",""),
    "exchange|money_withdraw":
        '''
        select uid, date(created_at) as date, 3 as transfer_type,
        symbol, sum(amount) as amount, sum(fee) as fee, 
        sum(real_fee) as real_fee
        from transaction_withdraw_crypto
        group by uid, date(created_at), symbol;
        '''.replace("\n",""),
    "exchange|money_otc":
        '''
        select 
        uid, date(create_time) as date, 
        transfer_type, coin_symbol as symbol, 
        sum(amount) as amount, 0 as fee, 0 as real_fee
        from otc_transfer 
        where status=1
        group by uid, date(create_time), transfer_type, coin_symbol;
        '''.replace("\n",""),
    "futures|position_fill":
        '''
        select a.uid, date(a.mtime) as date, 
        sum(a.deal_money) as deal_money, 
        sum(a.fee) as fee, 
        fee/deal_money as fee_rate,
        sum(a.realized_amount * (1-b.status)) as realized_amount
        from co_position_fill a  
        left join co_position b 
        on a.position_id = b.id 
        group by uid, date;
        '''.replace("\n",""),
}

query_dict = {
    "sql": query_sql_dict,
    
}