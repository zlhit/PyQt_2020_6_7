import pymysql
conn = pymysql.connect(host='localhost', port=3306, user='root', password='', database='resistance')
cs1 = conn.cursor()
cs1.execute('use resistance')
cs1.execute("select * from 2020_7 order by time desc limit 0,1")
        # self.cs1.execute('select * from 2020_7')
last_data = cs1.fetchall()
print(last_data)
