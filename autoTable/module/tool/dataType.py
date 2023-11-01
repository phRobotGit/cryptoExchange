 
#%%
import pandas as pd 
import numpy as np 


class AssetPool():
    df = None # data core, stored in pandas-dataframe format
    string = None # repr, stored in str 
    
    def __init__(self, string:str) -> None: 
        string = str(string).strip() 
        if string.lower() in ("", "nan", "nat"):
            self.string = ""
            self.df = pd.DataFrame({"asset":[], "number":[]})
        else:
            self.string = string 
            asset_list = string.split(",")
            df = pd.DataFrame({
                "asset": [i.split(":")[0].strip() for i in asset_list],
                "number":[i.split(":")[-1].strip() for i in asset_list]
            })
            df["asset"] = df["asset"].astype(str)
            df["number"] = df["number"].astype(float)
            self.df = df.copy()
    
    def _df_to_string(self, df) -> str:
        pair_zip = zip(df["asset"], df["number"])
        return(
            ", ".join([ f"{a}:{n}" for a,n in pair_zip]) 
        )
    
    def __add__(self, other):
        if pd.isna(other):
            return(AssetPool(self.string))
        df = pd.concat([self.df, other.df]).groupby(["asset"]).sum().reset_index(drop=False)
        return(
            AssetPool(self._df_to_string(df))
        )
        
    def __radd__(self, other):
        if pd.isna(other):
            return(AssetPool(self.string))
    
    def __sub__(self, other):
        if pd.isna(other):
            return(AssetPool(self.string))
        
        other_df = other.df.copy()
        other_df["number"] = -1*other_df["number"]
        df = pd.concat([self.df, other_df]).groupby(["asset"]).sum().reset_index(drop=False)
        return(
            AssetPool(self._df_to_string(df))
        )
        
    def __rsub__(self, other):
        if pd.isna(other):
            return(AssetPool(self.string))
    
    def __repr__(self) -> str:
        return(
            f"AssetPool( {self.string} )"
        )
    
    def is_zero(self):
        return(
            self.df["number"].sum() == 0
        )

# qqq = AssetPool(np.nan)
# a = "MATIC:0.0, TUSDT:0.0, DASH:0.17"
# # b = "BCH:0.05, DASH:0.07, DOGE:0.0, LTC:0.2, MATIC:2.0"
# # c = "TUSDT:0.0   "


# # # [ f"{a}:{n:.4f}" for a,n in zip(c["asset"], c["number"]) ]

# aaa = AssetPool(a)
# bbb = AssetPool(b)
# ccc = AssetPool(c)
# d = aaa+bbb

# aa = pd.DataFrame({
#     "asset": [i.split(":")[0] for i in a.split(", ")],
#     "number":[i.split(":")[-1] for i in a.split(", ")]
# })
# aa["asset"] = aa["asset"].astype(str)
# aa["number"] = aa["number"].astype(float)

# bb = pd.DataFrame({
#     "asset": [i.split(":")[0] for i in b.split(", ")],
#     "number":[i.split(":")[-1] for i in b.split(", ")]
# })
# bb["asset"] = bb["asset"].astype(str)
# bb["number"] = bb["number"].astype(float)


pd.isna(np.nan)