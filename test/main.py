import numpy as np
import pandas as pd
# from pylab import *
from PyQt5.QtWidgets import QApplication
import sys


import StopThread
import CharacterDataTcp
import InstanceDataTcp
import MysqlSearch
import InitialGui
import InitialSerial

class App(InitialGui.Initial_Gui,InitialSerial.Initial_Serial,CharacterDataTcp.character_data,InstanceDataTcp.instance__data,
			MysqlSearch.Mysql_Search):

    def __init__(self, st):
        
        # 继承父类初始化方法
        super(App, self).__init__()
        # self.setTabBar(TabBar(self))

        # 设置停止子线程方法
        self.st = st

        # Tcp采集特征值的槽
        self.signal_write_msg.connect(self.write_msg)

        # 初始化已连接特征值客户端的ip和端口号
        self.client_socket_list = list()
        # 初始化已连接瞬时值客户端的ip和端口号
        self.client_socket_instance_list = list()

        # 初始化瞬时值列表
        self.data_instance = list()
        # 初始化特征值列表
        self.msg_list = []
        self.msg_list_sub = []
       
        # 数据库查询结果显示的槽
        self.mysql_write_msg.connect(self.mysql_data_display)
        # 瞬时值显示的槽
        self.instance_data_msg.connect(self.instance_data_display)
        # 发出报警音的槽
        self.abnormal_sound_write_msg.connect(self.abnormal_sound_play)
        # # 实时显示时间的槽
        # self.date_time_show_msg.connect(self.updateTime)
        ##更新模型的槽
        self.new_model_msg.connect(self.update_model_select)


        # 初始化单个点查找的索引值
        self.index = 0
        # 初始化焊点数
        self.welding_number = 0
        # 初始化异常焊点数
        self.abnormal_welding_number = 0

        self.tcp_server_start()
        # 打开时间显示函数
    #定义mysql查询到的数据存到csv中
    def to_csv(self):
        pd.DataFrame(self.all_name).to_csv('查找数据.csv')
    #定义Zscore均一化方法
    def Z_score(self, data):
        new_list = list((data - np.mean(data)) / np.std(data))
        return new_list
    #定义滑动平均滤波函数
    def np_move_avg(self, a, n, mode='same'):
        return (np.convolve(a, np.ones((n,)) / n, mode=mode))

    # def date_time_show(self):
    #     self.sever_date_time_show = threading.Thread(target=self.date_time_show_start)
    #     self.sever_date_time_show.start()

    # def date_time_show_start(self):
    #     while True:
    #         time.sleep(1)
    #         self.date_time_show_msg.emit("写入")

    # def updateTime(self):
    #     self.labelbar_showtime.setText(QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss dddd'))

# 运行程序
if __name__ == '__main__':
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    st = StopThread.StopThreading()
    main_window = App(st)
    main_window.show()
    app.exec()
