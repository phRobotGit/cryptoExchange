# from dataclasses import dataclass
import os 
import pathlib
from re import A
from matplotlib import axis, use
from matplotlib.pylab import f
import pandas as pd 


class report_BD():
    data_df = None
    summary_df = None
    start_date = None
    end_date = None
    query_dict = {
        "partner": '''select uid, mark, business, create_time, rebate_rate from partner where level = 1 ;''',
        "partner_rebate": "select uid, sum(estimate_rebate), sum(actual_rebate), sum(forbid_nums) from partner_rebate_daily where day_time between $START_DATE$ and $END_DATE$ group by uid;",
        "partner_team_data_daily": "select uid, account_in_nums, total_member, nums, trade_valume, fee, account_in, account_out from partner_team_data_daily where (day_time between $START_DATE$ and $END_DATE$);",
        "user_rebate_daily": "select uid, day_time, trade_volume, fee, rebate from user_rebate_daily where (day_time between $START_DATE$ and $END_DATE$)",
        "invite_user": "select uid, create_time, parent_id, first_id, chain, user_type, (create_time between $START_DATE$ and $END_DATE$) as new_created_flag from invite_user;" ,
        "user_usdt_record": "select uid, sum(amount), biz_type, day_time from user_usdt_record group by uid, day_time, biz_type;"
    }
    
    def __init__(self, start_date:str, end_date:str) -> None:
        self.start_date = str(start_date)
        self.end_date = str(end_date)
        
    
    def get_data(self, connection)->None:
        # partner
        partner_pd = pd.read_sql(
            self.query_dict["partner"],
            connection,
        ) 
        partner_pd["business"] = partner_pd["business"].apply(lambda x: str(x).lower().replace("ziv","zivb")) 
        
        self.partner_pd = partner_pd.copy()
        
        # partner_rebate_daily
        partner_rebate_pd = pd.read_sql(
            self.query_dict["partner_rebate"].replace("$START_DATE$",self.start_date).replace("$END_DATE$",self.end_date),
            connection
        ) 
        self.partner_rebate_pd = partner_rebate_pd.copy()

        # partner_team_data_daily
        partner_team_data_daily_pd = pd.read_sql(
            self.query_dict["partner_team_data_daily"].replace("$START_DATE$",self.start_date).replace("$END_DATE$",self.end_date),
            connection
        ) 
        self.partner_team_data_daily_pd = partner_team_data_daily_pd.copy()
        
        # invite_user
        invite_user_pd = pd.read_sql(
            self.query_dict["invite_user"].replace("$START_DATE$",self.start_date).replace("$END_DATE$",self.end_date),
            connection
        ) 
        self.invite_user_pd = invite_user_pd.copy()
        
        # user_rebate_daily
        user_rebate_daily_pd = pd.read_sql(
            self.query_dict["user_rebate_daily"].replace("$START_DATE$",self.start_date).replace("$END_DATE$",self.end_date),
            connection
        ) 
        self.user_rebate_daily_pd = user_rebate_daily_pd.copy()

        # user_usdt_record
        user_usdt_record_pd = pd.read_sql(
            self.query_dict["user_usdt_record"],
            connection
        )
        def f(df):
            df[df["biz_type"]=="recharge"]["sum(amount)"] 
            df[df["biz_type"]=="withdrawal"]["sum(amount)"] 
            return(pd.Series({
                "入金":df[df["biz_type"]=="recharge"]["sum(amount)"].sum(),
                "出金":df[df["biz_type"]=="withdrawal"]["sum(amount)"].sum() 
            }))
        self.user_usdt_record = user_usdt_record_pd.groupby(["uid", "day_time"]).apply(f).reset_index(drop=False)

    def _find_descendant_uid(self, uid):
        df = self.invite_user_pd.copy()
        uid = str(uid)
        df = df[df.apply(lambda x: ( uid in str(x["chain"])) or ( str(x["uid"]) ==uid),axis=1)]
        return([str(i) for i in df["uid"].tolist()])

    def summary_report(self):
        # 按 uid 统计 user 交易信息    
        df = self.user_rebate_daily_pd.copy()
        def f(df):
            return(pd.Series({
                "trade_volume": df["trade_volume"].sum(),
                "fee": df["fee"].sum(),
                "rebate": df["rebate"].sum(),
                # "new_created_flag": df[""]
            }))
        df = df.groupby(["uid"]).apply(f).reset_index(drop=False)
        df["返佣核算比例"] = df["rebate"] / df["fee"]
        user_rebate_pd = df.copy()
    
        # 按BD 统计 BD团队内uid 信息
        def f(df): # BD_uid_level_summary_df
            uid = df["uid"] # 商务BD - uid
            uid_team_list = [str(i) for i in self._find_descendant_uid(uid)]# 找到商务BD团队List
            df_1 = user_rebate_pd[user_rebate_pd["uid"].apply(lambda x: str(x) in uid_team_list)]
            df_2 = self.invite_user_pd[self.invite_user_pd["uid"].apply(lambda x: str(x) in uid_team_list)]
            df_2 = df_2[["uid", "parent_id", "first_id", "chain", "user_type", "new_created_flag"]]
            r = pd.merge(
                df_1, df_2, how="right", on="uid"
            )
            
            return(pd.DataFrame({
                "uid": r["uid"],
                "BD": df["business"],
                "是否统计期内新增": r["new_created_flag"],
                "链路": r["chain"],
                "父节点": r["parent_id"],
                "首节点": r["first_id"],
                "用户类型": r["user_type"],
                "交易量": r["trade_volume"],
                "手续费": r["fee"],
                "团队返佣": r["rebate"], 
                "统计日期": f"{self.start_date}-{self.end_date}",
            }))
        BD_uid_level_summary_df = pd.concat(self.partner_pd.apply(lambda x: f(x), axis=1).tolist())
        BD_uid_level_summary_df = pd.merge(BD_uid_level_summary_df , self.partner_pd[["uid", "mark","rebate_rate"]], on="uid", how="left")
        df = self.user_usdt_record.groupby("uid").sum().reset_index(drop=False) 
        df = df[["uid", "入金", "出金"]]
        df.columns = ["uid", "创建以来累计入金", "创建以来累计出金"]
        BD_uid_level_summary_df = pd.merge(BD_uid_level_summary_df , df, on="uid", how="left")
        BD_uid_level_summary_df["是否统计期内有效"] = BD_uid_level_summary_df[["交易量", "创建以来累计入金", "创建以来累计出金"]].sum(axis=1)
        BD_uid_level_summary_df["是否统计期内有效"] = 1*(BD_uid_level_summary_df["是否统计期内有效"] > 0 )
        BD_uid_level_summary_df = BD_uid_level_summary_df.rename({"mark":"备注", "rebate_rate":"返佣比率"},axis=1)
        df = self.partner_rebate_pd.copy()
        df.columns = ["uid", "预估节点返佣", "实际节点返佣", "禁用返佣数"]
        BD_uid_level_summary_df = pd.merge(BD_uid_level_summary_df , df, on="uid", how="left")
        self.BD_uid_level_summary_df = BD_uid_level_summary_df.copy()
        
        def f(df): # BD_level_summary_df 
            return(pd.Series({
                # "uid": 
                "团队人数":df.shape[0],
                "统计期新增代理数":df["是否统计期内新增"].sum(),
                "统计期有效代理数":df["是否统计期内有效"].sum(),
                "交易量": df["交易量"].sum(),
                "手续费": df["手续费"].sum(),
                "团队返佣": df["团队返佣"].sum(),
                "创建以来团队累计入金": df["创建以来累计入金"].sum(),
                "创建以来团队累计出金": df["创建以来累计出金"].sum(),
                "统计日期": f"{self.start_date}-{self.end_date}",
            }))
        BD_level_summary_df = BD_uid_level_summary_df.groupby("BD").apply(f).reset_index(drop=False)
        self.BD_level_summary_df = BD_level_summary_df.copy()
        
    
    def save_summary_report(self, save_path_root: pathlib.Path) -> None:
        
        os.makedirs(save_path_root, exist_ok=True)
        if self.start_date == self.end_date:
            save_path = pathlib.Path(f"商务BD报表_{self.start_date}.xlsx")
        else:
            save_path = pathlib.Path(f"商务BD报表_{self.start_date}_至_{self.end_date}.xlsx")
        
        writer = pd.ExcelWriter(save_path_root / save_path, engine="openpyxl")
        self.BD_level_summary_df.to_excel(writer, index=False, sheet_name="按BD汇总")
        self.BD_uid_level_summary_df.to_excel(writer, index=False, sheet_name="按uid汇总")
        
        for sheet,df in zip(writer.sheets, [self.BD_level_summary_df,self.BD_uid_level_summary_df]):
            worksheet = writer.sheets[sheet]
            for idx, col in enumerate(df):
                series = df[col]
                max_len = max((
                    series.astype(str).map(len).max(),
                    len(str(series.name))
                    )) + 3
                worksheet.column_dimensions[chr(65+idx)].width = max_len
        
        writer.close()
        
        def f(df):
            bd = df["business"] # 商务BD
            if self.start_date == self.end_date:
                save_path = pathlib.Path(f"商务BD报表_{bd}_{self.start_date}.xlsx")
            else:
                save_path = pathlib.Path(f"商务BD报表_{bd}_{self.start_date}_至_{self.end_date}.xlsx")
            writer = pd.ExcelWriter(save_path_root / save_path, engine="openpyxl")
            df1 = self.BD_level_summary_df[self.BD_level_summary_df["BD"]==bd]
            df2 = self.BD_uid_level_summary_df[self.BD_uid_level_summary_df["BD"]==bd]
            df1.to_excel(writer, index=False, sheet_name="按BD汇总")
            df2.to_excel(writer, index=False, sheet_name="按uid汇总")
            
            for sheet,df in zip(writer.sheets, [df1, df2]):
                worksheet = writer.sheets[sheet]
                for idx, col in enumerate(df):
                    series = df[col]
                    max_len = max((
                        series.astype(str).map(len).max(),
                        len(str(series.name))
                        )) + 3
                    worksheet.column_dimensions[chr(65+idx)].width = max_len
                    
            writer.close()
        self.partner_pd.apply(lambda x: f(x), axis=1)
