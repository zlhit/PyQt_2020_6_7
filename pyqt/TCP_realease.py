import numpy as np
import matplotlib
from sklearn.neighbors import LocalOutlierFactor
from sklearn.ensemble import IsolationForest
from sklearn.covariance import EllipticEnvelope
import socket
import threading
import binascii
import pymysql
import pandas as pd
import ctypes
import datetime
import pickle
import serial
import winsound
import os

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from pylab import *

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
# 使用 matplotlib中的FigureCanvas (在使用 Qt5 Backends中 FigureCanvas继承自QtWidgets.QWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication
from PyQt5.QtCore import QTimer
import sys

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget,QTabWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSlot


##将Tab横向显示并旋转文本
class TabBar(QtWidgets.QTabBar):
    def tabSizeHint(self, index):
        s = QtWidgets.QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        opt = QtWidgets.QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabLabel, opt);
            painter.restore()


#

class App(QTabWidget):
    # 定义信号
    signal_write_msg = QtCore.pyqtSignal(str)
    mysql_write_msg = QtCore.pyqtSignal(str)
    instance_data_msg = QtCore.pyqtSignal(str)
    abnormal_sound_write_msg = QtCore.pyqtSignal(str)

    def __init__(self,st):
        # 父类初始化方法
        super(App, self).__init__()
        # self.setTabBar(TabBar(self))
        self.setTabPosition(QtWidgets.QTabWidget.South)
        #隐藏关闭键
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)

        self.setWindowTitle('宁波世典焊接科技有限公司')
        self.setWindowIcon(QIcon('电力图标.jpg'))
        self.setWindowIcon(QIcon('2345_image_file_copy_1.jpg'))
        self.setFixedSize(1000, 730)
        # self.setMinimumSize(1000, 700)
        # self.setMaximumSize(2000, 768)
        self.setStyleSheet("QTabBar::tab{min-height: 70px; min-width: 80px;};")
                           # "QTabWidget::left-corner { width: 60px;height: 25px; subcontrol-position: left bottom;")

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()

        # pix = QtGui.QPixmap('background.jpg')
        # lb1 = QLabel(self)
        # # lb1.setGeometry(0, 0, 300, 200)
        # # lb1.setStyleSheet("border: 2px solid red")
        # lb1.setPixmap(pix)
        # lb1.setScaledContents(True)
        #
        self.tabbar_widget = QWidget()
        # self.tabbar_widget.setFixedHeight(100)
        # self.tabbar_widget.setFixedWidth(100)


        self.machine_num = QComboBox()
        self.machine_num.setStyleSheet('QComboBox {background-color: #A3C1DA;color: red;}')
        # self.machine_num.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.machine_num.setFixedHeight(25)
        self.machine_num.setFixedWidth(100)
        self.machine_num.addItems(['焊机编号','A01', 'A02', 'A03', 'A04','A05', 'A06', 'A07', 'A08', 'A09', 'A10', 'A11',
                             '------', 'A12','A13', 'A14','A15', 'A16'])
        self.machine_num.setCurrentIndex(4)
        self.machine_num.setEnabled(False)



        self.chain_num = QComboBox()
        self.chain_num.setStyleSheet('QComboBox {background-color: #A3C1DA;color: red;}')
        self.chain_num.setFixedHeight(25)
        self.chain_num.setFixedWidth(76)
        self.chain_num.addItems(['链环规格', 'G806x18', 'G807x21', 'G808x24', 'G809x27', 'G8010x30', 'G8011x33', 'G8011x66', 'G8012x36', 'G8013x39', 'G8013x81', 'G8016x81',
                                   '------', 'T4x12', 'T5x15', 'T6x18', 'T6.3x19', 'T7x21', 'T7.1x21', 'T8x24', 'T9x27', 'T10x30'])
        self.chain_num.setCurrentIndex(3)
        self.chain_num.setEnabled(False)

        self.para_num = QComboBox()
        self.para_num.setStyleSheet('QComboBox {background-color: #A3C1DA;color: red;}')
        self.para_num.setFixedHeight(25)
        self.para_num.setFixedWidth(76)
        self.para_num.addItems(['规范编号', '1', '2', '3', '4'])
        self.para_num.setCurrentIndex(1)
        self.para_num.setEnabled(False)

        self.name_num = QComboBox()
        self.name_num.setStyleSheet('QComboBox {background-color: #A3C1DA;color: red;}')
        self.name_num.setFixedHeight(25)
        self.name_num.setFixedWidth(76)
        self.name_num.addItems(['员工编号', '01', '02', '03', '04'])
        self.name_num.setCurrentIndex(1)
        self.name_num.setEnabled(False)

        self.push_button = QPushButton('修改')
        # self.push_button.setStyleSheet('QPushButton {border: none;}')
        self.push_button.clicked.connect(self.infor_display)
        self.push_button.setFixedHeight(25)
        self.push_button.setFixedWidth(76)

        # self.setLayoutDirection(Qt.LayoutDirection.)
        self.tabBar_layout = QHBoxLayout()
        self.tabBar_layout.addWidget(self.push_button)
        self.tabBar_layout.addWidget(self.machine_num)
        self.tabBar_layout.addWidget(self.chain_num)
        self.tabBar_layout.addWidget(self.para_num)
        self.tabBar_layout.addWidget(self.name_num)
        #
        self.tabbar_widget.setLayout(self.tabBar_layout)


        # self.setCornerWidget(self.label,Qt.TopRightCorner)
        self.setCornerWidget(self.tabbar_widget,Qt.TopLestCorner)
        #self.setCornerWidget(self.push_button, Qt.TopRightCorner)

        self.addTab(self.tab1,'特征值监控')
        # self.tab1.setFont(QtGui.QFont("Roman times", 15, QtGui.QFont.Bold))
        # self.addTab(self.tab1,QtGui.QIcon(QtGui.QPixmap("icon.png").scaled(3000, 2000)), '特征值监控')
        self.addTab(self.tab1,'特征值监控')
        self.addTab(self.tab2,'数据库查询')
        self.addTab(self.tab3,'焊点查询')
        self.addTab(self.tab4,'瞬时值')
        self.addTab(self.tab5,'设定')
        self.setIconSize(QtCore.QSize(60, 100))



        self.st = st

        self.signal_write_msg.connect(self.write_msg)
        self.client_socket_list = list()
        self.client_socket_instance_list = list()
        self.data_instance = list()
        self.msg_list = list()
        self.com_num = 'COM1'

        self.mysql_write_msg.connect(self.mysql_data_display)
        self.instance_data_msg.connect(self.instance_data_display)
        self.abnormal_sound_write_msg.connect(self.abnormal_sound_play)


        self.init_model()
        self.init_tab5()
        self.init_tab1()
        self.init_tab2()
        self.init_tab3()
        self.init_tab4()
        #初始化单个点查找的索引值
        self.index = 0
        self.welding_number = 0
        self.abnormal_welding_number = 0

        self.tcp_server_start()

    def init_model(self):
        route = open(os.getcwd()+'\ilf.model', 'rb')
        self.model = pickle.load(route)
        route.close()
        route1 = open(os.getcwd()+'\elf.model', 'rb')
        self.model1 = pickle.load(route1)
        route1.close()
        route2 = open(os.getcwd()+'\lof.model', 'rb')
        self.model2 = pickle.load(route2)
        route2.close()

    def init_tab1(self):
        # 设置QWidgets


        #添加Tab选项
        # self.tabWidget = QtWidgets.QTabWidget()
        # self.tabWidget.setObjectName("tabWidget")
        # self.tab = QtWidgets.QWidget()
        # self.tab.setObjectName("特征值监控")
        # self.tabWidget.addTab(self.tab, "")
        # self.tab_2 = QtWidgets.QWidget()
        # self.tab_2.setObjectName("tab_2")
        # self.tabWidget.addTab(self.tab_2, "")

        self.tcp_character_open = QPushButton('开始采集')
        self.tcp_character_open.setFont(QtGui.QFont("Roman times", 15, QtGui.QFont.Bold))
        self.tcp_character_open.clicked.connect(self.tcp_server_start)


        self.tcp_character_close = QPushButton('停止采集')
        self.tcp_character_close.setFont(QtGui.QFont("Roman times", 15, QtGui.QFont.Bold))
        self.tcp_character_close.clicked.connect(self.tcp_server_stop)

        self.window_close = QPushButton('关闭窗口')
        self.window_close.setFixedHeight(40)
        self.window_close.setFont(QtGui.QFont("Roman times", 20, QtGui.QFont.Bold))
        self.window_close.clicked.connect(self.window_close_fun)
        self.window_close.setEnabled(False)

        #设置相关焊接参数显示
        self.welding_num = QLabel('waiting')
        # self.welding_num.setFixedWidth(60)
        self.welding_num.setFont(QtGui.QFont("Roman times", 40, QtGui.QFont.Bold))
        self.welding_num.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.label_welding_num = QLabel('第:')
        self.label_welding_num.setFont(QtGui.QFont("Roman times", 40, QtGui.QFont.Bold))
        self.label_welding_num.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.label_welding_num2 = QLabel('环')
        self.label_welding_num2.setFont(QtGui.QFont("Roman times", 40, QtGui.QFont.Bold))
        self.label_welding_num2.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)


        self.abnormal_welding_num = QLabel('wait')
        self.abnormal_welding_num.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))
        # self.abnormal_welding_num.setFixedWidth(60)
        self.label_abnormal_welding_num = QLabel('异常计数:')
        self.label_abnormal_welding_num.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))

        self.clear_number = QPushButton('计数清零')
        self.clear_number.setFont(QtGui.QFont("Roman times", 15, QtGui.QFont.Bold))
        # self.clear_number.setStyleSheet('QPushButton {background-color: #A3C1DA;color: red;}')
        self.clear_number.clicked.connect(self.clear_all_number)

        self.pre_display = QLabel('报警')
        self.pre_display.setStyleSheet("background-color:green;")
        self.pre_display.setFixedHeight(60)
        self.pre_display.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        #工艺参数
        self.process_parameter = QLabel('工艺参数')
        self.process_parameter.setStyleSheet("background-color:gray;")
        self.process_parameter.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)

        self.welding_cycle = QLabel('wait')
        self.welding_cycle.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))
        self.welding_cycle.setFixedWidth(60)
        self.label_welding_cycle = QLabel('周波数:')
        self.label_welding_cycle.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))

        self.welding_current_mean = QLabel('wait')
        self.welding_current_mean.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))
        self.welding_current_mean.setFixedWidth(63)
        self.label_welding_current_mean = QLabel('电流值:')
        self.label_welding_current_mean.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))

        self.welding_time = QLabel('wait')
        self.welding_time.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))
        self.welding_time.setFixedWidth(60)
        self.label_welding_time = QLabel('焊接时间:')
        self.label_welding_time.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))

        self.current_ratio_mean_value = QLabel('wait')
        self.current_ratio_mean_value.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))
        self.current_ratio_mean_value.setFixedWidth(60)
        self.label_current_ratio_mean_value = QLabel('焊接通流比%:')
        self.label_current_ratio_mean_value.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))

        self.distance_value = QLabel('wait')
        self.distance_value.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))
        self.distance_value.setFixedWidth(60)
        self.label_distance_value = QLabel('最终位移量：')
        self.label_distance_value.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))


        #设备参数
        self.machine_info = QLabel('设备信息')
        self.machine_info.setStyleSheet("background-color:gray;")
        self.machine_info.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)


        self.welding_material = QLabel(self.set_material_info.text())
        self.label_welding_material = QLabel('链环规格')

        self.welding_machine = QLabel(self.set_machine_info.text())
        self.label_welding_machine = QLabel('焊接机台')

        self.welding_parameter_num = QLabel(self.set_parameter_info.text())
        self.label_welding_parameter_num = QLabel('规范编号')

        self.spacer_split = QLabel()

        vuvupic = QtGui.QPixmap("icon.png")
        self.spacer_split.setPixmap(vuvupic)

        self.spacer_split.setFixedHeight(220)
        self.spacer_split.setFixedWidth(200)
        self.spacer_split.setScaledContents(True)


        # 图像模块
        # 初始化图形显示界面
        pg.setConfigOption('foreground', 'k')
        # 设置显示图像的背景颜色
        pg.setConfigOption('background', (245,245,245))
        #设置电阻曲线的表示
        self.pw = pg.PlotWidget(name='Plot1')
        self.pw.addLegend()
        self.pw.showGrid(x=True, y=True)
        self.pw.setLabel("left", "Resistance (Ω)")
        self.pw.setLabel("bottom", "Time (H)")

        # 设置位移曲线的表示
        self.pw_dis = pg.PlotWidget(name='Plot_dis')
        self.pw_dis.addLegend()
        self.pw_dis.showGrid(x=True, y=True)
        self.pw_dis.setLabel("left", "Distance")
        self.pw_dis.setLabel("bottom", "Time (H)")


        #设置布局
        #设置子布局
        self.leftbox = QVBoxLayout()
        self.leftbox1 = QGridLayout()
        self.leftbox2 = QHBoxLayout()
        self.leftbox3 = QGridLayout()
        self.rightbox = QVBoxLayout()
        self.rightbox1 = QHBoxLayout()
        self.rightbox2 = QVBoxLayout()
        self.boxall = QHBoxLayout()

        # 添加控件
        #self.newbox1.addWidget(self.label_welding_cycle)
        #self.newbox1.addWidget(self.welding_cycle)
        #self.newbox1.addWidget(self.textBrowser_recv)
        #self.leftbox.addWidget(self.textBrowser_recv)
        #self.leftbox.addLayout(self.leftbox1)


        #self.newbox2.addWidget(self.label_welding_num)
        #self.newbox2.addWidget(self.welding_num)
        #self.leftbox1.addWidget(self.welding_cycle)

       #添加第一列


        self.leftbox1.addWidget(self.label_abnormal_welding_num,1,0)
        # self.leftbox1.addWidget(self.pre_display,2,0)

        # self.leftbox1.addWidget(self.process_parameter,3,0)
        self.leftbox1.addWidget(self.label_welding_cycle,4,0)
        self.leftbox1.addWidget(self.label_welding_current_mean,5,0)
        self.leftbox1.addWidget(self.label_welding_time,6,0)
        self.leftbox1.addWidget(self.label_current_ratio_mean_value,7,0)
        self.leftbox1.addWidget( self.label_distance_value,8,0)


       #设备信息
        # self.leftbox1.addWidget(self.machine_info,9,0)
        # self.leftbox1.addWidget(self.label_welding_material,10,0)
        # self.leftbox1.addWidget(self.label_welding_machine, 11, 0)
        # self.leftbox1.addWidget(self.label_welding_parameter_num, 12, 0)
        # self.leftbox1.addWidget(self.tcp_character_open, 13, 0)

        #添加第二列


        self.leftbox1.addWidget(self.abnormal_welding_num, 1, 1)
        # self.leftbox1.addWidget(self.clear_number, 2, 1)
        self.leftbox1.addWidget(self.welding_cycle, 4, 1)
        self.leftbox1.addWidget(self.welding_current_mean, 5, 1)
        self.leftbox1.addWidget(self.welding_time,6,1)
        self.leftbox1.addWidget(self.current_ratio_mean_value,7,1)
        self.leftbox1.addWidget( self.distance_value,8,1)


        #设备信息
        # self.leftbox1.addWidget(self.welding_material, 10, 1)
        # self.leftbox1.addWidget(self.welding_machine, 11, 1)
        # self.leftbox1.addWidget(self.welding_parameter_num, 12, 1)

        #添加左侧的第二个box
        self.leftbox2.addWidget(self.spacer_split)
        self.spacer_split.setStyleSheet("background-color:white;")

        #添加左侧第三个box
        # self.leftbox3.addWidget(self.tcp_character_open)
        # self.leftbox3.addWidget(self.tcp_character_close)
        # self.leftbox3.addWidget(self.clear_number)
        self.tcp_character_open.setStyleSheet("background-color:white;")
        self.tcp_character_close.setStyleSheet("background-color:white;")
        self.clear_number.setStyleSheet("background-color:white;")
        self.window_close.setStyleSheet("background-color:white;")


        self.leftbox.addLayout(self.leftbox1)
        self.leftbox.addLayout(self.leftbox2)
        self.leftbox.addWidget(self.tcp_character_open)
        self.leftbox.addWidget(self.tcp_character_close)
        self.leftbox.addWidget(self.clear_number)
        self.leftbox.addWidget(self.window_close)



        self.rightbox1.addWidget(self.label_welding_num)
        self.rightbox1.addWidget(self.welding_num)
        self.rightbox1.addWidget(self.label_welding_num2)


        self.rightbox2.addWidget(self.pw)
        self.rightbox2.addWidget(self.pw_dis)

        self.rightbox.addLayout(self.rightbox1)
        self.rightbox.addLayout(self.rightbox2)

        #添加布局
        self.boxall.addLayout(self.leftbox)
        self.boxall.addLayout(self.rightbox)
        self.boxall.setStretch(0,1)
        self.boxall.setStretch(1,5)
        self.tab1.setLayout(self.boxall)
        self.tab1.setStyleSheet("background-color:rgb(245,245,245);")
        # 数组初始化

    def init_tab2(self):
        self.mysql_search = QPushButton('开始查找')
        self.mysql_to_csv = QPushButton('导出为csv')
        self.label_time_start = QLabel('查询起始时间')
        self.label_time_stop = QLabel('查询终止时间')

        self.date_time_start = QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.date_time_start.setCalendarPopup(True)
        self.date_time_stop = QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.date_time_stop.setCalendarPopup(True)



        # 初始化图形显示界面
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOption('background', (220, 220, 198, 30))
        self.pw2 = pg.PlotWidget(name='Plot2')
        #建立时间标签的layout
        self.date_time_start_label = QHBoxLayout()
        self.date_time_start_label.addWidget(self.label_time_start)
        self.date_time_start_label.addWidget(self.date_time_start)

        self.date_time_stop_label = QHBoxLayout()
        self.date_time_stop_label.addWidget(self.label_time_stop)
        self.date_time_stop_label.addWidget(self.date_time_stop)

        self.tab2_left = QVBoxLayout()
        self.tab2_right = QHBoxLayout()
        self.tab2_box_all = QHBoxLayout()

        self.tab2_left.addLayout(self.date_time_start_label)
        self.tab2_left.addLayout(self.date_time_stop_label)
        self.tab2_left.addWidget(self.mysql_search)
        self.tab2_left.addWidget(self.mysql_to_csv)
        self.tab2_right.addWidget(self.pw2)

        self.tab2_box_all.addLayout(self.tab2_left)
        self.tab2_box_all.addLayout(self.tab2_right)
        self.tab2_box_all.setStretch(0, 1)
        self.tab2_box_all.setStretch(1, 4)

        self.tab2.setLayout(self.tab2_box_all)

        self.mysql_search.clicked.connect(self.mysql_search_start)
        self.mysql_to_csv.clicked.connect(self.to_csv)

    def init_tab3(self):

        self.mysql_search_pre_result = QLabel('警报')
        self.mysql_search_pre_result.setFixedHeight(100)
        self.mysql_search_pre_result.setFixedWidth(100)
        self.mysql_search_pre_result.setStyleSheet("background-color:green;")
        self.mysql_search_pre_result.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.mysql_search_last_point = QPushButton('查询当前数据')
        self.mysql_search_previous_point = QPushButton('查询上一条数据')
        self.mysql_abnormal_data = QPushButton('查询异常数据')
        self.mysql_abnormal_data.setEnabled(False)
        self.mysql_abnormal_data_list = QComboBox()


        ##初始化图形界面
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOption('background', (220, 220, 198, 30))
        self.pw3 = pg.PlotWidget(name='查询电阻曲线')
        self.pw4 = pg.PlotWidget(name='查询位移曲线')



        self.tab3_left = QVBoxLayout()
        self.tab3_right = QVBoxLayout()
        self.tab3_box_all = QHBoxLayout()

        self.tab3_left.addWidget(self.mysql_search_pre_result)
        self.tab3_left.addWidget(self.mysql_search_last_point)
        self.tab3_left.addWidget(self.mysql_search_previous_point)
        self.tab3_left.addWidget(self.mysql_abnormal_data)
        self.tab3_left.addWidget(self.mysql_abnormal_data_list)

        self.tab3_right.addWidget(self.pw3)
        self.tab3_right.addWidget(self.pw4)


        self.tab3_box_all.addLayout(self.tab3_left)
        self.tab3_box_all.addLayout(self.tab3_right)
        self.tab3_box_all.setStretch(0, 1)
        self.tab3_box_all.setStretch(1, 4)

        self.tab3.setLayout(self.tab3_box_all)
        self.mysql_abnormal_data_list.activated.connect(self.abnormal_data_display)
        self.mysql_search_last_point.clicked.connect(self.mysql_last_point)
        self.mysql_search_previous_point.clicked.connect(self.mysql_previous_point)


    def init_tab4(self):

        self.Tcp_instance_open = QPushButton('开启瞬时值采集')
        self.Tcp_instance_open.clicked.connect(self.Tcp_instance_model_start)

        self.Tcp_instance_close = QPushButton('关闭瞬时值采集')
        self.Tcp_instance_close.clicked.connect(self.Tcp_instance_model_close)
        self.Tcp_instance_close.setEnabled(False)

        self.serial_open = QPushButton('开启串口')
        self.serial_open.clicked.connect(self.serial_start)

        self.serial_write = QPushButton('读取串口数据')
        self.serial_write.clicked.connect(self.serial_read_data)
        self.serial_write.setEnabled(False)

        self.serial_close = QPushButton('关闭串口')
        self.serial_close.clicked.connect(self.serial_stop)
        self.serial_close.setEnabled(False)

        self.serial_character = QPushButton('进入特征值模式')
        self.serial_character.clicked.connect(self.serial_character_mode)
        self.serial_character.setEnabled(False)

        self.serial_instance = QPushButton('进入瞬时值模式')
        self.serial_instance.clicked.connect(self.serial_instance_mode)
        self.serial_instance.setEnabled(False)

        self.serial_change = QPushButton('切换模式')
        self.serial_change.clicked.connect(self.serial_change_mode)
        self.serial_change.setEnabled(False)

        self.serial_display = QTextBrowser()



        pg.setConfigOption('foreground', 'k')
        # 设置显示图像的背景颜色
        pg.setConfigOption('background', (220, 220, 198, 30))
        # 设置电阻曲线的表示
        self.pw_instance = pg.PlotWidget(name='Plot_ins')
        self.pw_instance.addLegend()
        self.pw_instance.showGrid(x=True, y=True)
        self.pw_instance.setLabel("left", "电流/电压、电流微分 (Ω)")
        self.pw_instance.setLabel("bottom", "Time (H)")

        self.pw_distance_ins = pg.PlotWidget(name='Plot_dis')
        self.pw_distance_ins.addLegend()
        self.pw_distance_ins.showGrid(x=True, y=True)
        self.pw_distance_ins.setLabel("left", "位移 (mm)")
        self.pw_distance_ins.setLabel("bottom", "Time (H)")

        self.tab4_leftbox1 = QVBoxLayout()
        self.tab4_leftbox2 =QGridLayout()
        self.tab4_leftbox3 = QHBoxLayout()

        self.tab4_leftbox = QVBoxLayout()
        self.tab4_rightbox = QVBoxLayout()
        self.tab4_allbox = QHBoxLayout()

        self.tab4_leftbox1.addWidget(self.serial_display)

        self.tab4_leftbox2.addWidget(self.serial_open,0,0)
        self.tab4_leftbox2.addWidget(self.serial_close,0,1)
        self.tab4_leftbox2.addWidget(self.serial_write,2,0)
        self.tab4_leftbox2.addWidget(self.serial_character,1,1)
        self.tab4_leftbox2.addWidget(self.serial_instance,1,0)
        self.tab4_leftbox2.addWidget(self.serial_change,2,1)

        self.tab4_leftbox3.addWidget(self.Tcp_instance_open)
        self.tab4_leftbox3.addWidget(self.Tcp_instance_close)

        self.tab4_leftbox.addLayout(self.tab4_leftbox3)
        self.tab4_leftbox.addLayout(self.tab4_leftbox1)
        self.tab4_leftbox.addLayout(self.tab4_leftbox2)


        self.tab4_rightbox.addWidget(self.pw_instance)
        self.tab4_rightbox.addWidget(self.pw_distance_ins)

        self.tab4_allbox.addLayout(self.tab4_leftbox)
        self.tab4_allbox.addLayout(self.tab4_rightbox)
        self.tab4_allbox.setStretch(0, 1)
        self.tab4_allbox.setStretch(1, 4)

        self.tab4.setLayout(self.tab4_allbox)

    def init_tab5(self):
        self.set_machine_info = QLineEdit('A4')
        self.set_machine_info.setFixedWidth(100)
        self.label_set_machine_info = QLabel('焊接机台:')

        self.set_material_info = QLineEdit('8mm')
        self.set_material_info.setFixedWidth(100)
        self.label_set_material_info = QLabel('链环规格:')

        self.set_parameter_info = QLineEdit('1')
        self.set_parameter_info.setFixedWidth(100)
        self.label_set_parameter_info = QLabel('规范编号:')

        self.abnormal_sound_choice = QCheckBox('关闭报警音')
        self.abnormal_sound_choice.setChecked(True)

        self.shuntdown_signal = QCheckBox('关闭关机信号')
        self.shuntdown_signal.setChecked(True)

        self.spacer_dis  = QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum,
                                                QtWidgets.QSizePolicy.Expanding)

        self.tab5_leftbox1 = QGridLayout()

        self.tab5_rightbox1 = QHBoxLayout()
        self.tab5_allbox = QHBoxLayout()

        self.tab5_leftbox1.addWidget(self.label_set_material_info, 0, 0)
        self.tab5_leftbox1.addWidget(self.set_material_info, 0, 1)
        self.tab5_leftbox1.addWidget(self.label_set_machine_info,1,0)
        self.tab5_leftbox1.addWidget(self.set_machine_info,1,1)
        self.tab5_leftbox1.addWidget(self.label_set_parameter_info, 2, 0)
        self.tab5_leftbox1.addWidget(self.set_parameter_info, 2, 1)
        self.tab5_leftbox1.addWidget(self.abnormal_sound_choice,3,0)
        self.tab5_leftbox1.addWidget(self.shuntdown_signal,4,0)

        self.tab5_rightbox1.addItem(self.spacer_dis)

        self.tab5_allbox.addLayout(self.tab5_leftbox1)
        self.tab5_allbox.addLayout(self.tab5_rightbox1)
        self.tab5_allbox.setStretch(0, 1)
        self.tab5_allbox.setStretch(1, 6)


        self.tab5.setLayout(self.tab5_allbox)


    def serial_start(self):
        print('串口打开')
        self.serial_ = serial.Serial(self.com_num, 115200, timeout=0.5)
        self.serial_write.setEnabled(True)
        self.serial_close.setEnabled(True)
        self.serial_character.setEnabled(True)
        self.serial_instance.setEnabled(True)
        self.serial_change.setEnabled(True)
        self.serial_open.setEnabled(False)

    def serial_change_mode(self):
        self.serial_.write(b'\x01')

    def serial_character_mode(self):
        self.serial_.write(b'\x01')
        time.sleep(0.5)
        self.serial_.write(b'\x11')

    def serial_instance_mode(self):
        self.serial_.write(b'\x01')
        time.sleep(0.5)
        self.serial_.write(b'\x13')

    def serial_read_data(self):
        serial_text = self.serial_.read_all()
        self.serial_display.setText(str(serial_text))


    def serial_stop(self):
        self.serial_.close()
        self.serial_write.setEnabled(False)
        self.serial_close.setEnabled(False)
        self.serial_character.setEnabled(False)
        self.serial_instance.setEnabled(False)
        self.serial_change.setEnabled(False)
        self.serial_open.setEnabled(True)


    def tcp_server_start(self):
        """
        功能函数，TCP服务端开启的方法
        :return: None
        """
        self.msg_list = []
        self.Tcp_instance_open.setEnabled(False)
        self.tcp_character_open.setEnabled(False)
        self.tcp_character_close.setEnabled(True)
        self.window_close.setEnabled(False)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.setblocking(False)
        try:
            self.port = int(4144)
            self.ip = socket.gethostbyname(socket.gethostname())
            self.tcp_socket.bind((self.ip, self.port))
            print('绑定端口')
        except:
            pass
        else:
            self.tcp_socket.listen()
            self.sever_th = threading.Thread(target=self.tcp_server_concurrency)
            self.sever_th.start()
            #self.msg = 'TCP服务端正在监听端口:%s\n' % str(self.port)
            #self.signal_write_msg.emit("写入")



    def tcp_server_stop(self):
        try:
            ##向串口发送信息
            serial_ = serial.Serial(self.com_num, 115200, timeout=0.5)
            serial_.write(b'\x01')
            time.sleep(0.1)
            serial_.close()
        except:
            pass

        try:
            for client, address in self.client_socket_list:
                client.close()
            self.tcp_socket.close()
            self.st.stop_thread(self.sever_th)
        except:
            pass
        self.msg_list = []
        self.tcp_character_open.setEnabled(True)
        self.tcp_character_close.setEnabled(False)
        self.Tcp_instance_open.setEnabled(True)
        self.window_close.setEnabled(True)




    def tcp_server_concurrency(self):
        """
        功能函数，供创建线程的方法；
        使用子线程用于监听并创建连接，使主线程可以继续运行，以免无响应
        使用非阻塞式并发用于接收客户端消息，减少系统资源浪费，使软件轻量化
        :return:None
        """
        ##向串口发送信息
        serial_ = serial.Serial(self.com_num, 115200, timeout=0.5)
        serial_.write(b'\x01')
        time.sleep(0.5)
        serial_.write(b'\x11')
        time.sleep(0.1)
        serial_.close()

        while True:
            try:
                self.client_socket, self.client_address = self.tcp_socket.accept()
            except Exception as ret:
                time.sleep(0.001)
            else:
                self.client_socket.setblocking(False)
                # 将创建的客户端套接字存入列表
                self.client_socket_list.append((self.client_socket, self.client_address))
            # 轮询客户端套接字列表，接收数据
            for client, address in self.client_socket_list:
                try:
                    self.recv_msg = client.recv(1024)

                except:
                    pass
                else:
                    if self.recv_msg:
                        data_ = str(binascii.b2a_hex(self.recv_msg), 'utf-8')
                        data_list_ =[data_[i:i+2] for i in range(0, len(data_), 2)]
                        self.msg_list.extend(data_list_)
                        if len(self.msg_list) > 724:
                            self.msg_list = []

                        if len(self.msg_list) == 723:
                            try:
                                self.time1 = time.time()

                                # print(self.msg_list)
                                print(self.msg_list)
                                print(len(self.msg_list))
                                # self.msg_list = [self.msg[i:i+2] for i in range(0,len(self.msg),2)]
                                #取出半波数
                                self.halfwave_num = int(self.msg_list[0],16)
                                #取出通流比数据
                                self.current_ratio =sum([int(self.msg_list[1:self.halfwave_num*2+1][i+1]+self.msg_list[1:self.halfwave_num*2+1][i],16) for i in range(0,self.halfwave_num*2,2)])/(10.0*self.halfwave_num)
                                #取出电流有效值
                                self.current_rms_str_list = self.msg_list[1+2*self.halfwave_num:1+2*self.halfwave_num+8*self.halfwave_num]

                                self.current_rms_list = [int(self.current_rms_str_list[i+7]+self.current_rms_str_list[i+6]+self.current_rms_str_list[i+5]+self.current_rms_str_list[i+4]+
                                                         self.current_rms_str_list[i+3] + self.current_rms_str_list[i+2]+self.current_rms_str_list[i+1] + self.current_rms_str_list[i],16)
                                                         for i in range(0,self.halfwave_num*8,8)]
                                #取出电压有效值
                                self.voltage_rms_str_list = self.msg_list[1+2 * self.halfwave_num+8 * self.halfwave_num:1+2 * self.halfwave_num+8 * self.halfwave_num+8 * self.halfwave_num]

                                self.voltage_rms_list = [int(
                                    self.voltage_rms_str_list[i + 7] + self.voltage_rms_str_list[i + 6] +
                                    self.voltage_rms_str_list[i + 5] + self.voltage_rms_str_list[i + 4] +
                                    self.voltage_rms_str_list[i + 3] + self.voltage_rms_str_list[i + 2] +
                                    self.voltage_rms_str_list[i + 1] + self.voltage_rms_str_list[i], 16)
                                                         for i in range(0, self.halfwave_num * 8, 8)]
                                #取出电流平均值
                                self.current_mean_str_list = self.msg_list[1+2 * self.halfwave_num + 2*8 * self.halfwave_num:1 + 2 * self.halfwave_num + 8 * self.halfwave_num*2+4 * self.halfwave_num]

                                self.current_mean_list = [int(self.current_mean_str_list[i + 3] + self.current_mean_str_list[i + 2] +
                                                          self.current_mean_str_list[i + 1] + self.current_mean_str_list[i], 16)
                                                            for i in range(0, self.halfwave_num * 4, 4)]

                                #取出电压平均值
                                self.voltage_mean_str_list = self.msg_list[
                                                             1 + 2 * self.halfwave_num + 2 * 8 * self.halfwave_num+4 * self.halfwave_num:1 + 2 * self.halfwave_num + 8 * self.halfwave_num * 2 + 4 * self.halfwave_num*2]

                                self.voltage_mean_list = [
                                    int(self.voltage_mean_str_list[i + 3] + self.voltage_mean_str_list[i + 2] +
                                        self.voltage_mean_str_list[i + 1] + self.voltage_mean_str_list[i], 16)
                                    for i in range(0, self.halfwave_num * 4, 4)]

                                #计算电阻值
                                self.resistance_list = [int(self.voltage_mean_list[i]*10000/self.current_mean_list[i]) for i in range(self.halfwave_num)]

                                # 取出位移的平均值
                                self.distance_mean_str_list = self.msg_list[
                                                             1 + 2 * self.halfwave_num + 2 * 8 * self.halfwave_num + 4 * self.halfwave_num*2:1 + 2 * self.halfwave_num + 8 * self.halfwave_num * 2 + 4 * self.halfwave_num * 3]

                                self.distance_list = [
                                    int(self.distance_mean_str_list[i + 3] + self.distance_mean_str_list[i + 2] +
                                        self.distance_mean_str_list[i + 1] + self.distance_mean_str_list[i], 16)
                                    for i in range(0, self.halfwave_num * 4, 4)]

                                ##开始计算特征值
                                #电阻特征值
                                #print(list(self.Z_score(self.resistance_list)))
                                self.resistance_max = max(self.Z_score(self.resistance_list))  #电阻峰值
                                self.resistance_min = min(self.Z_score(self.resistance_list))  #电阻基值
                                self.resistance_max_index = self.Z_score(self.resistance_list).index(self.resistance_max)
                                self.resistance_min_index = self.Z_score(self.resistance_list).index(self.resistance_min)
                                ##电阻上升速度
                                self.resistance_increase_rate = (self.resistance_max-self.resistance_min)/(self.resistance_max_index-self.resistance_min_index)
                                #电阻上升时间占总时间的比例
                                self.resistance_increase_ratio = (self.resistance_max_index-self.resistance_min_index)/self.halfwave_num
                                #电阻初始值与最小值的差值
                                self.resistance_first_min = self.Z_score(self.resistance_list)[0]-self.resistance_min+0.5
                                #电阻最终值与峰值的差值
                                self.resistance_last_max = self.resistance_max -  self.Z_score(self.resistance_list)[-1] + 0.5

                                ##位移特征值
                                self.distance_max = max(self.Z_score(self.distance_list))  # 位移峰值
                                self.distance_min = min(self.Z_score(self.distance_list))  # 位移基值
                                self.distance_max_index = self.Z_score(self.distance_list).index(self.distance_max)
                                self.distance_min_index = self.Z_score(self.distance_list).index(self.distance_min)

                                ##位移下降速度
                                self.distance_decrease_rate = (self.distance_max - self.distance_min) / (self.distance_max_index - self.distance_min_index)
                                #位移下降时间占总时间的比例
                                self.distance_decrease_ratio = (self.distance_min_index-self.distance_max_index)/self.halfwave_num
                                # 位移初始值与最大值的差值
                                self.distance_first_max = self.distance_max - self.Z_score(self.distance_list)[0] + 0.5
                                # 位移最终值与最小值的差值
                                self.distance_last_min = self.Z_score(self.distance_list)[-1] - self.distance_min  + 0.5

                                #计算位移的特征
                                self.distance_decr = (max(self.distance_list) - min(self.distance_list)) / max(
                                    self.distance_list)

                                ##整合特征值
                                self.character_data = [[
                                    self.resistance_max,self.resistance_min,self.resistance_increase_rate,self.resistance_increase_ratio,
                                    self.resistance_first_min,self.resistance_last_max,0,1,
                                    self.distance_max,self.distance_min,self.distance_decrease_rate,self.distance_decrease_ratio,
                                    self.distance_first_max,self.distance_last_min,0,1
                                ]]
                                # print(self.character_data)
                                pre = self.model.predict(self.character_data)[0]
                                pre1 = self.model1.predict(self.character_data)[0]
                                pre2 = self.model2.predict(self.character_data)[0]
                                pre_sum = pre + pre1 + pre2
                                if pre_sum < 0:
                                    self.pre_result = -1
                                else:
                                    self.pre_result = 1

                                # print(self.Z_score(self.distance_list))
                                # print(self.distance_max)
                                # print(self.distance_last_min)
                                # print(self.distance_decrease_ratio)
                                # print(self.distance_min)
                                # print(self.distance_first_max)

                            except Exception as e:
                                print(e)
                                self.msg_list = []
                            else:
                                self.msg_list = []
                                self.signal_write_msg.emit("写入")
                                self.tab1.setStyleSheet("background-color:rgb(245,245,245);")

                                ##将数据存入数据库
                                try:
                                    self.conn_insert = pymysql.connect(host='localhost', port=3306, user='root', password='',
                                                                database='resistance')
                                    self.cs2 = self.conn_insert.cursor()
                                    self.cs2.execute('use resistance')
                                    # print(len(self.character_data))
                                    self.cs2.execute("SELECT table_name FROM information_schema.TABLES WHERE table_name ='{}_{}'".format(datetime.datetime.now().year,datetime.datetime.now().month))
                                    if self.cs2.fetchall():
                                        pass
                                    else:
                                        sql_create_table = "create table 2020_7 (ID int auto_increment primary key,time datetime, preict_result varchar(10), welding_machine varchar(10),welding_material varchar(20)," \
                                                           "welding_parameter varchar(10), welding_num varchar(10), welding_cycle varchar(10),distance_last varchar(10)," \
                                                           "weld1time varchar(10), weld1current varchar(10), weld1ratio varchar(10), weld2time varchar(10),weld2current varchar(10), " \
                                                           "weld2ratio varchar(10),weld3time varchar(10),weld3current varchar(10), weld3ratio varchar(10),distance varchar(200),resistance varchar(200)," \
                                                           "R_max varchar(30),R_min varchar(30),R_increase_rate varchar(30),R_IncreaseTime_ratio varchar(30),R0_Rmin varchar(30),Rlast_Rmax varchar(30)," \
                                                           "R_Eucl varchar(30),R_corr varchar(30),D_max varchar(30),D_min varchar(30),D_decrease_rate varchar(30),D_DecreaseTime_ratio varchar(30)," \
                                                           "D0_Dmax varchar(30),Dlast_Dmin varchar(30),D_Eucl varchar(30),D_corr varchar(30))"
                                        self.cs2.execute(sql_create_table)
                                        # print(sql_create_table)


                                    sql_ = "insert into {} values(0,'{}','{}','{}','{}','{}','1','{}','{}','{}','{}','{}',null,null,null,null,null,null,'{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(str(datetime.datetime.now().year) +'_'+str(datetime.datetime.now().month),
                                                                                                        datetime.datetime.now(),self.pre_result,
                                                                                                        self.set_machine_info.text(),self.set_material_info.text(),
                                                                                                        self.set_parameter_info.text(),self.halfwave_num,
                                                                                                        round(self.distance_decr,2),self.halfwave_num*20/2,
                                                                                                        int(np.mean(self.current_rms_list) / 1e5),round(self.current_ratio,2),
                                                                                                        str(self.distance_list[:-4])[1:-1],str(self.resistance_list)[1:-1],
                                        self.character_data[0][0],self.character_data[0][1],self.character_data[0][2],self.character_data[0][3],self.character_data[0][4],self.character_data[0][5],self.character_data[0][6],self.character_data[0][7],
                                        self.character_data[0][8], self.character_data[0][9], self.character_data[0][10],self.character_data[0][11], self.character_data[0][12], self.character_data[0][13],self.character_data[0][14], self.character_data[0][15]
                                                                                                           )
                                    self.cs2.execute(sql_)
                                    # self.cs1.execute('select * from 2020_7')
                                    self.conn_insert.commit()
                                    self.conn_insert.close()
                                except :
                                    pass



                            ##将数据存入数据库
                    # else:
                    #     client.close()
                    #     self.client_socket_list.remove((client, address))

    def write_msg(self):
        """
        功能函数，将从tcp接收到的数据发送到相关的显示控件
        信号-槽触发
        tip：PyQt程序的子线程中，使用非规定的语句向主线程的界面传输字符是不允许的
        :return: None
        """
        #计算一些需要及时显示的数据
        if self.pre_result == -1:
            self.tab1.setStyleSheet("background-color:red;")
            self.abnormal_welding_number += 1
            self.sever_sound = threading.Thread(target=self.abnormal_sound_play)
            self.sever_sound.start()
            self.serve_shuntdown = threading.Thread(target=self.shuntdown_signal_process)
            self.serve_shuntdown.start()
        else:
            pass

        self.welding_number += 1
        self.pw.clear()
        self.pw_dis.clear()
        self.welding_num.setText(str(self.welding_number))                              #焊接点数
        self.abnormal_welding_num.setText(str(self.abnormal_welding_number))            #焊接异常点个数
        self.welding_cycle.setText(str(self.halfwave_num/2))                            #焊接周波数
        self.welding_time.setText(str(self.halfwave_num*20/2))                            #焊接时间
        self.welding_current_mean.setText(str(int(np.mean(self.current_rms_list)/1e5)))          #焊接电流
        self.current_ratio_mean_value.setText(str(round(self.current_ratio,2)))             #焊接通流比
        self.distance_value.setText(str(round(self.distance_decr,2)))                         #最终位移量





        #self.pw.plot(range(self.halfwave_num),(self.current_rms_list-np.mean(self.current_rms_list))/np.std(self.current_rms_list), name='电流', pen=pg.mkPen(color='r'), symbol='s', symbolSize=10, symbolBrush=('r'))
        self.pw.plot(range(self.halfwave_num),self.Z_score(self.current_rms_list), name='电流', pen=pg.mkPen(color='r')
                     # , symbol='+', symbolSize=10, symbolBrush=('r')
                     )
        #self.pw.plot(range(self.halfwave_num), (self.voltage_rms_list-np.mean(self.voltage_rms_list))/np.std(self.voltage_rms_list),name='电压', pen=pg.mkPen(color='b'), symbol='+', symbolSize=10, symbolBrush=('b'))
        self.pw.plot(range(self.halfwave_num),self.Z_score(self.voltage_rms_list),name='电压', pen=pg.mkPen(color='b')
                     # , symbol='+', symbolSize=10, symbolBrush=('b')
                     )
        #self.pw.plot(range(self.halfwave_num), (self.resistance_list-np.mean(self.resistance_list))/np.std(self.resistance_list),name='电阻', pen=pg.mkPen(color='k'), symbol='+',symbolSize=10, symbolBrush=('k'))
        self.pw.plot(range(self.halfwave_num), self.Z_score(self.resistance_list),name='电阻', pen=pg.mkPen(color='k')
                     # , symbol='s',symbolSize=10, symbolBrush=('k')
                     )

        self.pw_dis.plot(range(self.halfwave_num), self.distance_list, name='位移', pen=pg.mkPen(color='r')
                         # , symbol='s', symbolSize=10, symbolBrush=('r')
                         )

        self.time2 = time.time()
        print(self.time2-self.time1)

    def shuntdown_signal_process(self):
        if self.shuntdown_signal.isChecked():
            pass
        else:
            serial_ = serial.Serial(self.com_num, 115200, timeout=0.5)
            serial_.write(b'\x01')
            time.sleep(0.3)
            serial_.write(b'\x01')
            time.sleep(0.3)
            serial_.write(b'\x33')
            time.sleep(0.1)
            serial_.close()
            print('signal emit')
            self.Tcp_instance_open.setEnabled(True)
            self.Tcp_instance_close.setEnabled(False)
            self.tcp_character_open.setEnabled(True)
            self.tcp_character_close.setEnabled(False)
        self.st.stop_thread(self.serve_shuntdown)


    def abnormal_sound_play(self):
        if self.pre_result == -1:
            # self.pre_display.setStyleSheet("background-color:red;")
            if self.abnormal_sound_choice.isChecked():
                pass
            else:
                winsound.PlaySound('警报1.wav', winsound.SND_FILENAME)
        else:
            pass
        self.st.stop_thread(self.sever_sound)




    def Tcp_instance_model_start(self):
        """
        功能函数，TCP服务端开启的方法
        :return: None
        """
        self.tcp_socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket_instance.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket_instance.setblocking(False)
        try:
            self.port_instance = int(4145)
            self.ip_instance = socket.gethostbyname(socket.gethostname())
            self.tcp_socket_instance.bind((self.ip_instance, self.port_instance))
            print('绑定端口')
        except Exception as ret:
            print(ret)
        else:
            self.tcp_socket_instance.listen()
            self.sever_th_instance = threading.Thread(target=self.tcp_server_concurrency_instance)
            self.sever_th_instance.start()
            #self.msg = 'TCP服务端正在监听端口:%s\n' % str(self.port)
            #self.signal_write_msg.emit("写入")
        self.Tcp_instance_open.setEnabled(False)
        self.Tcp_instance_close.setEnabled(True)
        self.tcp_character_open.setEnabled(False)
        self.window_close.setEnabled(False)


    def tcp_server_concurrency_instance(self):
        """
        功能函数，供创建线程的方法；
        使用子线程用于监听并创建连接，使主线程可以继续运行，以免无响应
        使用非阻塞式并发用于接收客户端消息，减少系统资源浪费，使软件轻量化
        :return:None
        """
        ##向串口发送信息
        self.data_instance = []
        serial_ = serial.Serial(self.com_num, 115200, timeout=0.5)
        serial_.write(b'\x01')
        time.sleep(0.5)
        serial_.write(b'\x13')
        time.sleep(0.1)
        serial_.close()


        while True:
            try:
                self.client_socket_instace, self.client_address_instance = self.tcp_socket_instance.accept()
            except Exception as ret:
                time.sleep(0.001)
            else:
                self.client_socket_instace.setblocking(False)
                # 将创建的客户端套接字存入列表
                self.client_socket_instance_list.append((self.client_socket_instace, self.client_address_instance))

            # 轮询客户端套接字列表，接收数据
            for client_, address_ in self.client_socket_instance_list:
                try:
                    recv_msg = client_.recv(10000)
                except Exception as ret:
                    pass
                else:
                    if recv_msg:
                        data = str(binascii.b2a_hex(recv_msg),'utf-8')
                        data_list = [data[i:i+2] for i in range(0, len(data), 2)]
                        self.data_instance.extend(data_list)

                        
                        if len(self.data_instance)> 308001:
                            self.data_instance = []
                        print(len(self.data_instance))


                        if len(self.data_instance) == 308000:
                            self.time3  = time.time()
                            print(len(self.data_instance))
                            ##统计瞬时值
                            self.U_data_instance_list = self.data_instance[ : 100000]
                            self.U_data_instance = [int(self.U_data_instance_list[i + 1] + self.U_data_instance_list[i], 16)
                            for i in range(0, len(self.U_data_instance_list), 2)]

                            self.I_data_instance_list = self.data_instance[100000 : 2*100000]
                            self.I_data_instance = [int(self.I_data_instance_list[i + 1] + self.I_data_instance_list[i], 16)
                                                    for i in range(0, len(self.I_data_instance_list), 2)]

                            self.I_dis_data_instance_list = self.data_instance[2*100000 : 3*100000]
                            self.I_dis_data_instance = [int(self.I_dis_data_instance_list[i + 1] + self.I_dis_data_instance_list[i], 16)
                                for i in range(0, len(self.I_dis_data_instance_list), 2)]

                            self.distance_instance_list = self.data_instance[3*100000 : 3*100000 + 6000]
                            print(self.distance_instance_list)
                            self.distance_instance = [int(self.distance_instance_list[i] + self.distance_instance_list[i+1], 16)
                                for i in range(0, len(self.distance_instance_list), 3)]

                            self.point_instance_list = self.data_instance[3 * 100000 + 6*1000 : 3 * 100000 + 6*1000 +1*2000]
                            self.point_instance = [int( self.point_instance_list[i + 1] + self.point_instance_list[i], 16)
                                                      for i in range(0, len(self.point_instance_list), 2)]

                            self.data_instance = []
                            self.instance_data_msg.emit('触发')
                            # print(len(self.data_instance))
                            # print(len(self.I_data_instance))
                            # print(len(self.U_data_instance))
                            # print(len(self.I_dis_data_instance))
                            # print(len(self.distance_instance))
                            # print(len(self.point_instance))
                            # self.pw_instance.clear()
                            # self.pw_distance_ins.clear()
                            # self.pw_instance.plot(range(len(self.I_data_instance)), self.I_data_instance, name='电流',
                            #                       pen=pg.mkPen(color='r'))
                            # self.pw_instance.plot(range(len(self.U_data_instance)), self.U_data_instance, name='电压',
                            #                       pen=pg.mkPen(color='b'))
                            # self.pw_instance.plot(range(len(self.I_dis_data_instance)), self.I_dis_data_instance,
                            #                       name='电流微分', pen=pg.mkPen(color='k'))
                            #
                            # # self.pw_instance.plot(range(len(self.I_data_instance)), [ 65536 if i in self.point_instance else 1 for i in range(len(self.I_data_instance))], name='时机',
                            # #                       pen=pg.mkPen(color='g'))
                            #
                            # self.pw_distance_ins.plot(range(len(self.distance_instance)), self.distance_instance, name='位移',
                            #                       pen=pg.mkPen(color='r'))
                            # self.data_instance = []


                        else:
                            pass

    def instance_data_display(self):
        print(len(self.data_instance))
        print(len(self.I_data_instance))
        print(len(self.U_data_instance))
        print(len(self.I_dis_data_instance))
        print(len(self.distance_instance))
        print(len(self.point_instance))
        self.pw_instance.clear()
        self.pw_distance_ins.clear()
        self.pw_instance.plot(range(len(self.I_data_instance)), self.I_data_instance, name='电流'
                              ,pen=pg.mkPen(color='r')
                              )
        self.pw_instance.plot(range(len(self.U_data_instance)), self.U_data_instance, name='电压'
                              ,pen=pg.mkPen(color='b')
                              )
        self.pw_instance.plot(range(len(self.I_dis_data_instance)), self.I_dis_data_instance,name='电流微分'
                              , pen=pg.mkPen(color='k')
                              )

        # self.pw_instance.plot(range(len(self.I_data_instance)), [ 65536 if i in self.point_instance else 1 for i in range(len(self.I_data_instance))], name='时机',
        #                       pen=pg.mkPen(color='g'))

        self.pw_distance_ins.plot(range(len(self.distance_instance)), self.np_move_avg(self.distance_instance,70), name='位移'
                                  ,pen=pg.mkPen(color='r')
                                  )
        self.time4 = time.time()
        print(self.time4-self.time3)
        # self.data_instance = []

    def Tcp_instance_model_close(self):
        self.data_instance = []
        ##向串口发送信息
        serial_ = serial.Serial(self.com_num, 115200, timeout=0.5)
        serial_.write(b'\x01')
        time.sleep(0.1)
        serial_.close()

        try:
            for client_, address_ in self.client_socket_instance_list:
                client_.close()
            self.tcp_socket_instance.close()
            self.st.stop_thread(self.sever_th_instance)

        except:
            pass
        self.Tcp_instance_open.setEnabled(True)
        self.Tcp_instance_close.setEnabled(False)
        self.tcp_character_open.setEnabled(True)
        self.window_close.setEnabled(True)

    def mysql_search_start(self):
        self.mysql_search.setEnabled(False)
        self.mysql_search.setText('--查找中--')
        self.sever_mysql = threading.Thread(target=self.mysql_server_concurrency)
        self.sever_mysql.start()

    def mysql_server_concurrency(self):
        time3 = time.time()
        date_start = self.date_time_start.text()
        date_stop = self.date_time_stop.text()
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='', database='resistance')
        self.cs1 = self.conn.cursor()
        time4 = time.time()
        self.cs1.execute('use resistance')
        self.cs1.execute("select * from {}_{} where time between '{}' and '{}'".format(datetime.datetime.now().year,datetime.datetime.now().month,date_start,date_stop))
        #self.cs1.execute('select * from 2020_7')
        self.all_name = self.cs1.fetchall()
        self.conn.close()
        print(self.all_name)
        time5  = time.time()
        self.abnormal_data = [ data_ for data_ in self.all_name if data_[2] =='-1']
        self.mysql_date = [str(data_[1]) for data_ in self.abnormal_data]
        time6 = time.time()

        #需要显示的统计函数
        self.num = [float(name[-3]) for name in self.all_name]
        self.mysql_write_msg.emit('触发')
        time7 = time.time()
        print(time4-time3)
        print(time5 - time4)
        print(time6 - time5)
        print(time7 - time6)


    def mysql_data_display(self):
        self.mysql_abnormal_data_list.clear()
        self.mysql_abnormal_data_list.addItems(self.mysql_date)
        self.pw2.clear()
        self.pw2.plot(self.num,pen=pg.mkPen(color='r'))
        self.mysql_search.setEnabled(True)
        self.mysql_search.setText('开始查找')

    def mysql_last_point(self):
        self.mysql_search_pre_result.setStyleSheet("background-color:green;")
        self.index = 0
        self.pw3.clear()
        self.pw4.clear()
        print('a')
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='', database='resistance')
        self.cs1 = self.conn.cursor()
        self.cs1.execute('use resistance')
        self.cs1.execute("select max(id) from {}_{}".format(datetime.datetime.now().year,datetime.datetime.now().month))
        self.last_num = self.cs1.fetchall()
        self.cs1.execute("select * from {}_{} where id = {}".format(datetime.datetime.now().year, datetime.datetime.now().month,self.last_num[0][0]))
        # self.cs1.execute('select * from 2020_7')
        self.last_data = self.cs1.fetchall()
        self.conn.close()
        print(self.last_data[0][2])
        if self.last_data[0][2] == '-1':
            self.mysql_search_pre_result.setStyleSheet("background-color:red;")
        else:
            self.mysql_search_pre_result.setStyleSheet("background-color:green;")

        R_data = [int(last_data_R) for last_data_R in self.last_data[0][19].split(',')]
        D_data = [int(last_data_D) for last_data_D in self.last_data[0][18].split(',')]

        self.pw3.plot(range(len(R_data)),R_data, name='resistance', pen=pg.mkPen(color='r')
                      # , symbol='s', symbolSize=10, symbolBrush=('r')
                      )
        self.pw4.plot(range(len(D_data)), D_data, name='resistance', pen=pg.mkPen(color='b')
                      # , symbol='+', symbolSize=10,symbolBrush=('b')
                      )

    def mysql_previous_point(self):
        self.mysql_search_pre_result.setStyleSheet("background-color:green;")
        self.index += 1
        self.pw3.clear()
        self.pw4.clear()
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
        if self.last_data[0][2] == '-1':
            self.mysql_search_pre_result.setStyleSheet("background-color:red;")
        else:
            self.mysql_search_pre_result.setStyleSheet("background-color:green;")
        R_data = [int(last_data_R) for last_data_R in self.last_data[0][19].split(',')]
        D_data = [int(last_data_D) for last_data_D in self.last_data[0][18].split(',')]

        self.pw3.plot(range(len(R_data)), R_data, name='resistance', pen=pg.mkPen(color='r')
                      # , symbol='s', symbolSize=10,symbolBrush=('r')
                      )
        self.pw4.plot(range(len(D_data)), D_data, name='resistance', pen=pg.mkPen(color='b')
                      # , symbol='+', symbolSize=10,symbolBrush=('b')
                      )

    def abnormal_data_display(self):
        self.mysql_search_pre_result.setStyleSheet("background-color:red;")
        self.pw3.clear()
        self.pw4.clear()
        print(self.mysql_abnormal_data_list.currentText())
        self.searched_data = [data_ for data_ in self.abnormal_data if str(data_[1]) == self.mysql_abnormal_data_list.currentText()]
        #print(self.searched_data[19])
        R_data = [int(last_data_R) for last_data_R in self.searched_data[0][19].split(',')]
        D_data = [int(last_data_D) for last_data_D in self.searched_data[0][18].split(',')]

        self.pw3.plot(range(len(R_data)), R_data, name='resistance', pen=pg.mkPen(color='r')
                      # , symbol='s', symbolSize=10,symbolBrush=('r')
                      )
        self.pw4.plot(range(len(D_data)), D_data, name='resistance', pen=pg.mkPen(color='b')
                      # , symbol='+', symbolSize=10,symbolBrush=('b')
                      )

    def infor_display(self):
        if self.push_button.text() == '修改':
            self.machine_num.setEnabled(True)
            self.chain_num.setEnabled(True)
            self.para_num.setEnabled(True)
            self.name_num.setEnabled(True)
            self.push_button.setText('确定')
        else:
            self.machine_num.setEnabled(False)
            self.chain_num.setEnabled(False)
            self.para_num.setEnabled(False)
            self.name_num.setEnabled(False)
            self.push_button.setText('修改')



    def to_csv(self):
        pd.DataFrame(self.all_name).to_csv('查找数据.csv')

    def Z_score(self,data):
        new_list = list((data-np.mean(data))/np.std(data))
        return new_list

    def np_move_avg(self,a, n, mode='same'):
        return (np.convolve(a, np.ones((n,)) / n, mode=mode))


    #清除焊接计数
    def clear_all_number(self):
        self.welding_number = 0
        self.abnormal_welding_number = 0
        self.welding_num.setText(str(self.welding_number))
        self.abnormal_welding_num.setText(str(self.abnormal_welding_number))

    def window_close_fun(self):
        msgBox = QMessageBox()
        msgBox.setWindowTitle('关闭测试窗口 or 关机')
        msgBox.addButton('关闭测试窗口', QMessageBox.AcceptRole)
        msgBox.addButton('关机', QMessageBox.RejectRole)
        msgBox.addButton('取消', QMessageBox.DestructiveRole)
        reply = msgBox.exec()
        if reply == QMessageBox.AcceptRole:
            self.close()
        elif reply == QMessageBox.RejectRole:
            os.system('shutdown -s')
        else :
            pass

class StopThreading:
    """强制关闭线程的方法"""

    @staticmethod
    def _async_raise(tid, exc_type):
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exc_type):
            exc_type = type(exc_type)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exc_type))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop_thread(self, thread):
        self._async_raise(thread.ident, SystemExit)




# 运行程序
if __name__ == '__main__':
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    st = StopThreading()
    main_window = App(st)
    main_window.show()
    app.exec()
