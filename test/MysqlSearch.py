import threading
import pymysql
import pyqtgraph as pg
import datetime

class Mysql_Search:
    #建立并开启数据库查找数据子线程
    def mysql_search_start(self):
        #点击后将查找数据设置为不可用状态
        self.mysql_search.setEnabled(False)
        self.mysql_search.setText('--查找中--')
        #建立并开启子线程
        self.sever_mysql = threading.Thread(target=self.mysql_server_concurrency)
        self.sever_mysql.start()
    
    #子线程需要处理的函数
    def mysql_server_concurrency(self):
        #读取用户设置的时间
        date_start = self.date_time_start.text()
        date_stop = self.date_time_stop.text()
        # 连接数据库
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='', database='resistance')
        self.cs1 = self.conn.cursor()
        self.cs1.execute('use resistance')
        #根据用户输入时间区间查找数据库
        self.cs1.execute("select * from {}_{} where time between '{}' and '{}'".format(datetime.datetime.now().year,
                                                                                       datetime.datetime.now().month,
                                                                                       date_start, date_stop))
        # self.cs1.execute('select * from 2020_7')
        self.all_name = self.cs1.fetchall()
        self.conn.close()
        #取出所有的异常数据
        self.abnormal_data = [data_ for data_ in self.all_name if data_[2] == '-1']
        self.mysql_date = [str(data_[1]) for data_ in self.abnormal_data][-100:]
        # 需要显示的统计函数
        self.num = [float(name[-4]) for name in self.all_name]
        self.num_2 = [float(name[-10]) for name in self.all_name]
        #进入绘图函数
        self.mysql_write_msg.emit('触发')

    def mysql_data_display(self):
        #向下拉列表控件中添加异常数据的日期时间
        self.mysql_abnormal_data_list.clear()
        self.mysql_abnormal_data_list.addItems(self.mysql_date)
        #清空图像中的数据，并根据新的数据绘图
        self.pw2.clear()
        self.pw2.plot(self.np_move_avg(self.num, 200), pen=pg.mkPen(color='r'))
        self.pw2_2.clear()
        self.pw2_2.plot(self.np_move_avg(self.num_2, 200), pen=pg.mkPen(color='r'))
        
        #
        self.mysql_search.setEnabled(True)
        self.mysql_search.setText('开始查找')

    def mysql_last_point(self):
        #点击按钮后，将按钮状态设置为不可用
        self.mysql_search_last_point.setEnabled(False)
        self.mysql_search_last_point.setText('--查询中--')
        self.mysql_search_pre_result.setStyleSheet("background-color:green;")
        #初始化查询的索引号
        self.index = 0
        #将图像清空
        self.pw3.clear()
        self.pw4.clear()
        print('a')
        #连接数据库
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='', database='resistance')
        self.cs1 = self.conn.cursor()
        self.cs1.execute('use resistance')
        self.cs1.execute(
            "select max(id) from {}_{}".format(datetime.datetime.now().year, datetime.datetime.now().month))
        self.last_num = self.cs1.fetchall()
        self.cs1.execute(
            "select * from {}_{} where id = {}".format(datetime.datetime.now().year, datetime.datetime.now().month,
                                                       self.last_num[0][0]))
        # self.cs1.execute('select * from 2020_7')
        #取出查找到的数据
        self.last_data = self.cs1.fetchall()
        self.conn.close()
        print(self.last_data[0][7])
        self.welding_cycle_show.setText('周波数：  ' + self.last_data[0][7])
        self.distance_value_show.setText('最终位移量：' + self.last_data[0][8])
        self.welding_time_show.setText('焊接时间 ：' + self.last_data[0][9])
        self.welding_current_mean_show.setText('电流值：  ' + self.last_data[0][10])
        self.current_ratio_mean_value_show.setText('通流比：  ' + self.last_data[0][11])


        #如果查找到的数据为异常数据，就将显示控件变为红色
        if self.last_data[0][2] == '-1':
            self.mysql_search_pre_result.setStyleSheet("background-color:red;")
        else:
            self.mysql_search_pre_result.setStyleSheet("background-color:green;")

        #取出电阻数据与位移数据进行展示
        R_data = [int(last_data_R) for last_data_R in self.last_data[0][19].split(',')]
        D_data = [int(last_data_D) for last_data_D in self.last_data[0][18].split(',')]

        #将数据绘图
        self.pw3.plot(range(len(R_data)), R_data, name='电阻曲线', pen=pg.mkPen(color='r')
                      # , symbol='s', symbolSize=10, symbolBrush=('r')
                      )
        self.pw4.plot(range(len(D_data)), D_data, name='位移曲线', pen=pg.mkPen(color='b')
                      # , symbol='+', symbolSize=10,symbolBrush=('b')
                      )
        #改变按钮的状态
        self.mysql_search_last_point.setEnabled(True)
        self.mysql_search_last_point.setText('查询当前数据')

    #查询前一焊点的数据
    def mysql_previous_point(self):
        #改变按钮的状态，并修改背景颜色
        self.mysql_search_previous_point.setEnabled(False)
        self.mysql_search_previous_point.setText('--查询中--')
        self.mysql_search_pre_result.setStyleSheet("background-color:green;")
        #索引号+1，一直向前搜索
        self.index += 1
        #清空图像
        self.pw3.clear()
        self.pw4.clear()
        #连接数据库查找数据
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='', database='resistance')
        self.cs1 = self.conn.cursor()
        self.cs1.execute('use resistance')
        self.cs1.execute(
            "select max(id) from {}_{}".format(datetime.datetime.now().year, datetime.datetime.now().month))
        self.last_num = self.cs1.fetchall()
        self.cs1.execute(
            "select * from {}_{} where id = {}".format(datetime.datetime.now().year, datetime.datetime.now().month,
                                                       self.last_num[0][0] - self.index))
        self.last_data = self.cs1.fetchall()
        print(self.last_data[0][0])
        self.conn.close()
        self.welding_cycle_show.setText('周波数：  ' + self.last_data[0][7])
        self.distance_value_show.setText('最终位移量：' + self.last_data[0][8])
        self.welding_time_show.setText('焊接时间 ：' + self.last_data[0][9])
        self.welding_current_mean_show.setText('电流值：  ' + self.last_data[0][10])
        self.current_ratio_mean_value_show.setText('通流比：  ' + self.last_data[0][11])
        #如果该点异常，就更改显示控件的颜色       
        if self.last_data[0][2] == '-1':
            self.mysql_search_pre_result.setStyleSheet("background-color:red;")
        else:
            self.mysql_search_pre_result.setStyleSheet("background-color:green;")

        #提取出位移数据与电阻数据
        R_data = [int(last_data_R) for last_data_R in self.last_data[0][19].split(',')]
        D_data = [int(last_data_D) for last_data_D in self.last_data[0][18].split(',')]

        #将位移与电阻显示到图表中
        self.pw3.plot(range(len(R_data)), R_data, name='电阻曲线', pen=pg.mkPen(color='r')
                      # , symbol='s', symbolSize=10,symbolBrush=('r')
                      )
        self.pw4.plot(range(len(D_data)), D_data, name='位移曲线', pen=pg.mkPen(color='b')
                      # , symbol='+', symbolSize=10,symbolBrush=('b')
                      )

        self.mysql_search_previous_point.setEnabled(True)
        self.mysql_search_previous_point.setText('查询上一条数据')

    #单点异常数据的显示
    def abnormal_data_display(self):
        #修改背景颜色
        self.mysql_search_pre_result.setStyleSheet("background-color:red;")
        #清空图像
        self.pw3.clear()
        self.pw4.clear()
        print(self.mysql_abnormal_data_list.currentText())
        #找出用输入的日期对应的数据
        self.searched_data = [data_ for data_ in self.abnormal_data if
                              str(data_[1]) == self.mysql_abnormal_data_list.currentText()]
        # print(self.searched_data[19])

        self.welding_cycle_show.setText('周波数：  ' + self.searched_data[0][7])
        self.distance_value_show.setText('最终位移量：' + self.searched_data[0][8])
        self.welding_time_show.setText('焊接时间 ：' + self.searched_data[0][9])
        self.welding_current_mean_show.setText('电流值：  ' + self.searched_data[0][10])
        self.current_ratio_mean_value_show.setText('通流比：  ' + self.searched_data[0][11])
        #从数据中取出电阻与位移数据
        R_data = [int(last_data_R) for last_data_R in self.searched_data[0][19].split(',')]
        D_data = [int(last_data_D) for last_data_D in self.searched_data[0][18].split(',')]

        #将取出的数据绘制到图中
        self.pw3.plot(range(len(R_data)), R_data, name='电阻曲线', pen=pg.mkPen(color='r')
                      # , symbol='s', symbolSize=10,symbolBrush=('r')
                      )
        self.pw4.plot(range(len(D_data)), D_data, name='位移曲线', pen=pg.mkPen(color='b')
                      # , symbol='+', symbolSize=10,symbolBrush=('b')
                      )