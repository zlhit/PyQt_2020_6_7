import socket
import pickle
import numpy as np
import time
from PyQt5.QtWidgets import QApplication,QWidget,QSlider,QPushButton
from PyQt5 import QtCore
import threading
import sys
import pyqtgraph as pg
import pymysql
import datetime

import StopThread
import UDP_server

class UDP_display(QWidget,UDP_server.Ui_Form):
    signal_write_msg = QtCore.pyqtSignal(str)
    def __init__(self,st):
        # 继承父类初始化方法
        super(UDP_display, self).__init__()
        self.setupUi(self)

        pg.setConfigOption('foreground', 'k')
        # 设置显示图像的背景颜色
        pg.setConfigOption('background', (245, 245, 245))
        # 设置电阻曲线的表示
        self.pw = pg.PlotWidget(name='Plot1')
        self.pw.addLegend()

        ##设置图形复原按钮
        self.recover_scale_push = QPushButton('复原')


        self.start_udp.clicked.connect(self.start_udp_server)
        self.stop_udp.clicked.connect(self.stop_udp_server)
        self.signal_write_msg.connect(self.write_message)
        self.recover_scale_push.clicked.connect(self.recover_scale)

        #添加控制放大程度的slider
        self.move_slider1 = QSlider(QtCore.Qt.Horizontal)
        self.move_slider = QSlider(QtCore.Qt.Horizontal)
        self.move_slider.setMaximum(20)
        self.move_slider.setSingleStep(0.005)
        self.move_slider.setValue(10)
        ##设定一个对比值
        self.contrast_value = 10
        self.move_slider.valueChanged.connect(self.move_changeValue)

        self.blowup = QPushButton('放大')
        self.blowup.clicked.connect(self.changeValue)

        self.narrow = QPushButton('缩小')
        self.narrow.clicked.connect(self.changeValue_narrow)


        self.verticalLayout_2.addWidget(self.pw)
        # self.verticalLayout_2.addWidget(self.move_slider1)
        self.verticalLayout_2.addWidget(self.move_slider)
        self.verticalLayout_2.addWidget(self.blowup)
        self.verticalLayout_2.addWidget(self.narrow)
        self.verticalLayout_2.addWidget(self.recover_scale_push)

        self.st = st

        self.start_udp_server()


    def start_udp_server(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.udpsock= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpsock.bind((self.ip, 1001))
        self.udp_serve_th = threading.Thread(target=self.udp_serve_concurrency)
        self.udp_serve_th.start()

        self.start_udp.setEnabled(False)
        self.stop_udp.setEnabled(True)

    def udp_serve_concurrency(self):
        print(1)
        while True:
            time.sleep(0.001)
            data, address = self.udpsock.recvfrom(65536)
            if data:
                self.text = data.decode('utf-8').split(';')
                self.signal_write_msg.emit('显示')
                self.dis_list = [int(i) for i in self.text[4].split(',')]
                self.resis_list = [int(i) for i in self.text[5].split(',')]
                self.character_data = [float(i) for i in self.text[6][1:-1].split(',')]

                try:
                    self.conn_insert = pymysql.connect(host='localhost', port=3306, user='root',
                                                       password='',
                                                       database='store')
                    self.cs2 = self.conn_insert.cursor()
                    self.cs2.execute('use store')
                    # print(len(self.character_data))
                    print(1)
                    # 判断本月的表是否存在
                    self.cs2.execute(
                        "SELECT table_name FROM information_schema.TABLES WHERE table_name ='{}__{}'".format(
                            datetime.datetime.now().year, datetime.datetime.now().month))
                    # 如果存在，空操作
                    if self.cs2.fetchall():
                        pass
                    # 如果不存在，就按照既定的数据模式创建新表
                    else:
                        sql_create_table = "create table {}__{} (ID int auto_increment primary key,time datetime, preict_result varchar(10), welding_machine varchar(10),welding_ratio varchar(20)," \
                                           "distance varchar(200),resistance varchar(200)," \
                                           "R_max varchar(30),R_min varchar(30),R_increase_rate varchar(30),R_IncreaseTime_ratio varchar(30),R0_Rmin varchar(30),Rlast_Rmax varchar(30)," \
                                           "D_max varchar(30),D_min varchar(30),D_decrease_rate varchar(30),D_DecreaseTime_ratio varchar(30)," \
                                           "D0_Dmax varchar(30),Dlast_Dmin varchar(30))".format(
                            datetime.datetime.now().year, datetime.datetime.now().month)
                        print(sql_create_table)
                        self.cs2.execute(sql_create_table)
                        # print(sql_create_table)

                    # 将本次数据存入数据库中
                    sql_ = "insert into {} values(0,'{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
                        str(datetime.datetime.now().year) + '__' + str(datetime.datetime.now().month),
                        (self.text[0]).split('.')[0], self.text[1],self.text[2], self.text[3],
                        self.dis_list, self.resis_list,
                        self.character_data[0], self.character_data[1], self.character_data[2],
                        self.character_data[3], self.character_data[4], self.character_data[5],
                        self.character_data[6], self.character_data[7],
                        self.character_data[8], self.character_data[9],
                        self.character_data[10], self.character_data[11])
                    self.cs2.execute(sql_)
                    # self.cs1.execute('select * from 2020_7')
                    self.conn_insert.commit()
                    self.conn_insert.close()
                except Exception as e:
                    print(e)


    def write_message(self):

        self.pw.clear()
        self.textBrowser.setText(str(self.text))
        self.datetime.setText(str((self.text[0]).split('.')[0]))
        self.pre_result.setText(self.text[1])
        self.machine_name.setText(self.text[2])

        self.pw.plot(range(len(self.dis_list)), self.Z_score(self.dis_list), name='位移', pen=pg.mkPen(color='r')
                     # , symbol='s',symbolSize=10, symbolBrush=('k')
                     )
        self.pw.plot(range(len(self.resis_list)), self.Z_score(self.resis_list), name='电阻', pen=pg.mkPen(color='k')
                     # , symbol='s',symbolSize=10, symbolBrush=('k')
                     )
        # print(self.move_slider.value())
        # self.move_slider.setMaximum(len(self.resis_list))
        # self.move_slider.setSingleStep(len(self.resis_list)/10)
        # self.move_slider1.setMaximum(0)
        # self.move_slider.setSingleStep(len(self.resis_list) / 10)

    def changeValue(self):

        # self.pw.setXRange(self.move_slider.value()/20*len(self.resis_list), (1-self.move_slider.value()/20)*len(self.resis_list), padding=0)

        self.pw.setXRange(self.pw.visibleRange().getRect()[0]+ 0.1 * (self.pw.visibleRange().getRect()[0] + self.pw.visibleRange().getRect()[2]),
                          self.pw.visibleRange().getRect()[0] + self.pw.visibleRange().getRect()[2]-0.1 * (
                                      self.pw.visibleRange().getRect()[0] + self.pw.visibleRange().getRect()[2]),
                          padding=0)
        # print(self.pw.visibleRange().getRect()[0])
        # print(self.pw.visibleRange())
        # self.move_slider1.setMaximum(self.move_slider.value())
    def changeValue_narrow(self):

        # self.pw.setXRange(self.move_slider.value()/20*len(self.resis_list), (1-self.move_slider.value()/20)*len(self.resis_list), padding=0)

        self.pw.setXRange(self.pw.visibleRange().getRect()[0]- 0.3 * (self.pw.visibleRange().getRect()[0] + self.pw.visibleRange().getRect()[2]),
                          self.pw.visibleRange().getRect()[0] + self.pw.visibleRange().getRect()[2]+0.3 * (
                                      self.pw.visibleRange().getRect()[0] + self.pw.visibleRange().getRect()[2]),
                          padding=0)
        # print(self.pw.visibleRange().getRect()[0])
        # print(self.pw.visibleRange())
    def move_changeValue(self):
        if self.move_slider.value() > self.contrast_value:
            self.pw.setXRange(self.pw.visibleRange().getRect()[0] + len(self.resis_list)/40,
                              self.pw.visibleRange().getRect()[0] + self.pw.visibleRange().getRect()[2] + len(self.resis_list)/40,
                              padding=0)
        else:
            self.pw.setXRange(
                self.pw.visibleRange().getRect()[0] -  len(self.resis_list) / 40,
                self.pw.visibleRange().getRect()[0] + self.pw.visibleRange().getRect()[
                    2] - len(self.resis_list) / 40,
                padding=0)
        self.contrast_value = self.move_slider.value()
        # print('moving')


    def recover_scale(self):
        self.pw.setXRange(0,len(self.resis_list))
        self.move_slider.setValue(10)
        self.contrast_value = 10

    def stop_udp_server(self):
        self.udpsock.close()
        self.st.stop_thread(self.udp_serve_th)

        self.start_udp.setEnabled(True)
        self.stop_udp.setEnabled(False)

    def Z_score(self, data):
        new_list = list((data - np.mean(data)) / np.std(data))
        return new_list

if __name__ == '__main__':
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    st = StopThread.StopThreading()
    main_window = UDP_display(st)
    main_window.show()
    app.exec()