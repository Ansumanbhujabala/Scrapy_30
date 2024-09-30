
import pandas as pd
import glob
file_list= glob.glob("/opt/CodeRepo/Scrapy_Learn/newdata/jsonfolder/*.json")
import re 

total=0
df_list=[pd.read_json(file) for file in file_list]


for i,df in enumerate(df_list):
    ak=len(df)
    unique=df.nunique().sum()
    name=file_list[i].removeprefix('/opt/CodeRepo/Scrapy_Learn/newdata/jsonfolder/')
    print(name,"---->>>>",ak, "----------------->> unique>>",unique)

    total+=ak
print(total)    
combined_df=pd.concat(df_list)
combined_df.to_excel("CollegeDunia_all_new.xlsx", index=False)
combined_df=combined_df.drop_duplicates()
combined_df.to_json("CollegeDunia_Urls_new.json",orient='records', lines=True)
combined_df.to_excel("CollegeDunia_Urls_new.xlsx", index=False)

