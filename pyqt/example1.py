import pickle
from pymysql import *
import os
import time
import pandas as pd
#from sklearn.externals import joblib
from sklearn.ensemble import RandomForestClassifier
time1 = time.time()
conn = connect(host='localhost',port=3306,user='root',password='mysql',database='resistance')
cs1 = conn.cursor()
all_character = pd.DataFrame()
cs1.execute('use resistance')
cs1.execute('select * from 2020_7')
all_name = cs1.fetchall()
# cs1.execute("desc aaa")
# columns_name = cs1.fetchall()
# all_name = [name[0] for name in columns_name][3:]
# for i,name in enumerate(all_name):
#     cs1.execute("select %s from data" % name)
#     features = cs1.fetchall()
#     data = pd.DataFrame([float(feature[0]) for feature in features])
#     all_character = pd.concat([all_character,data],axis=1)
# all_character.columns = all_name
print([name[0] for name in all_name])
print([name[1] for name in all_name])
print([name[2] for name in all_name])
# data = pd.DataFrame(all_name)
# print(data.iloc[:,0])
# print(data.iloc[:,1])
# print(data.iloc[:,2])
time2 = time.time()
print(time2-time1)

