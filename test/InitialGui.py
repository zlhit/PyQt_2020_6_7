'''
对界面的布局进行初始化
'''


# from PyQt5.QtWidgets import QTabWidget,QWidget
from PyQt5 import QtCore, QtWidgets, QtGui
import os
import pickle
import sys
# from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from sklearn.neighbors import LocalOutlierFactor
from sklearn.ensemble import IsolationForest
from sklearn.covariance import EllipticEnvelope
import datetime
import pymysql
import pandas as pd
import numpy as np
import threading

class Initial_Gui(QTabWidget):
    
    # 定义信号
    signal_write_msg = QtCore.pyqtSignal(str)
    mysql_write_msg = QtCore.pyqtSignal(str)
    instance_data_msg = QtCore.pyqtSignal(str)
    abnormal_sound_write_msg = QtCore.pyqtSignal(str)
    date_time_show_msg = QtCore.pyqtSignal(str)
    new_model_msg = QtCore.pyqtSignal(str)
   
    def __init__(self):
    # 继承父类初始化方法
        super(Initial_Gui, self).__init__()
        # 将tab窗口放在下面
        self.setTabPosition(QtWidgets.QTabWidget.South)
        # 隐藏关闭和最大化按钮
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
        # 设置窗口名称
        self.setWindowTitle('宁波世典焊接科技有限公司')
        # 设置窗口大小
        self.setFixedSize(1000, 730)
        # self.setMinimumSize(1000, 700)
        # self.setMaximumSize(2000, 768)
        # 设置tabbar的格式
        self.setStyleSheet("QTabBar::tab{min-height: 70px; min-width: 80px;};")
        # "QTabWidget::left-corner { width: 60px;height: 25px; subcontrol-position: left bottom;")

        # 将tab实例化
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
        ##添加模型训练子线程

        # 添加一个widget,使tabbar靠右显示
        self.tabbar_widget = QWidget()
        self.layour_tabbar = QHBoxLayout()
        self.layour1_tabbar = QVBoxLayout()
        self.layour2_tabbar = QVBoxLayout()

        #添加控件并修改控件大小与字体大小
        self.machine_num_show = QLabel()
        self.machine_num_show.setFixedWidth(150)
        self.machine_num_show.setFont(QtGui.QFont("Roman times", 10, QtGui.QFont.Bold))
        self.chain_num_show = QLabel()
        self.chain_num_show.setFont(QtGui.QFont("Roman times", 10, QtGui.QFont.Bold))
        self.para_num_show = QLabel()
        self.para_num_show.setFont(QtGui.QFont("Roman times", 10, QtGui.QFont.Bold))
        self.name_num_show = QLabel()
        self.name_num_show.setFont(QtGui.QFont("Roman times", 10, QtGui.QFont.Bold))

        self.labelbar_showtime = QLabel()
        self.labelbar_showtime.setFont(QtGui.QFont("Roman times", 20, QtGui.QFont.Bold))
        self.labelbar_showtime.setFixedWidth(240)

        self.layour1_tabbar.addWidget(self.machine_num_show)
        self.layour1_tabbar.addWidget(self.chain_num_show)

        self.layour2_tabbar.addWidget(self.para_num_show)
        self.layour2_tabbar.addWidget(self.name_num_show)

        self.layour_tabbar.addLayout(self.layour1_tabbar)
        self.layour_tabbar.addLayout(self.layour2_tabbar)
        self.layour_tabbar.addWidget(self.labelbar_showtime)
        self.tabbar_widget.setLayout(self.layour_tabbar)

        self.setCornerWidget(self.tabbar_widget, Qt.TopLeftCorner)

        # 将tab添加到窗口
        self.addTab(self.tab1, '特征值监控')
        # self.tab1.setFont(QtGui.QFont("Roman times", 15, QtGui.QFont.Bold))
        # self.addTab(self.tab1,QtGui.QIcon(QtGui.QPixmap("icon.png").scaled(3000, 2000)), '特征值监控')
        self.addTab(self.tab2, '数据库查询')
        self.addTab(self.tab3, '焊点查询')
        self.addTab(self.tab4, '瞬时值')
        self.addTab(self.tab5, '设定')
        self.setIconSize(QtCore.QSize(60, 100))

        self.init_model()
        self.init_tab5()
        self.init_tab1()
        self.init_tab2()
        self.init_tab3()
        self.init_tab4()
    #读取本地模型
    def init_model(self):
        try:
            with open(os.getcwd() + '\model\model_select.txt') as f:
                new_route = f.readline()
        except:
            new_route ='initial_model'
        print(new_route)
        route = open(os.getcwd() + '\model\{}\ilf.model'.format(new_route), 'rb')
        self.model = pickle.load(route)
        route.close()
        route1 = open(os.getcwd() + '\model\{}\elf.model'.format(new_route), 'rb')
        self.model1 = pickle.load(route1)
        route1.close()
        route2 = open(os.getcwd() + '\model\{}\lof.model'.format(new_route), 'rb')
        self.model2 = pickle.load(route2)
        route2.close()

    def init_tab1(self):
        # 设置QWidgets

        # 添加Tab选项
        # self.tabWidget = QtWidgets.QTabWidget()
        # self.tabWidget.setObjectName("tabWidget")
        # self.tab = QtWidgets.QWidget()
        # self.tab.setObjectName("特征值监控")
        # self.tabWidget.addTab(self.tab, "")
        # self.tab_2 = QtWidgets.QWidget()
        # self.tab_2.setObjectName("tab_2")
        # self.tabWidget.addTab(self.tab_2, "")
        # 添加控件
        self.tcp_character_open = QPushButton('开始采集')
        # 修改字体格式
        self.tcp_character_open.setFont(QtGui.QFont("Roman times", 15, QtGui.QFont.Bold))
        # 与对应函数建立连接
        self.tcp_character_open.clicked.connect(self.tcp_server_start)

        self.tcp_character_close = QPushButton('停止采集')
        self.tcp_character_close.setFont(QtGui.QFont("Roman times", 15, QtGui.QFont.Bold))
        self.tcp_character_close.clicked.connect(self.tcp_server_stop)

        self.window_close = QPushButton('关闭窗口')
        self.window_close.setFixedHeight(40)
        self.window_close.setFont(QtGui.QFont("Roman times", 20, QtGui.QFont.Bold))
        self.window_close.clicked.connect(self.window_close_fun)
        self.window_close.setEnabled(False)

        self.reset_net = QPushButton('下位机复位')
        self.reset_net.setFixedHeight(40)
        self.reset_net.setFont(QtGui.QFont("Roman times", 20, QtGui.QFont.Bold))
        self.reset_net.setEnabled(False)
        self.reset_net.clicked.connect(self.reset_net_fun)

        # 设置相关焊接参数显示
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

        # 工艺参数
        self.process_parameter = QLabel('工艺参数')
        self.process_parameter.setStyleSheet("background-color:gray;")
        self.process_parameter.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

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

        # 设备参数
        self.machine_info = QLabel('设备信息')
        self.machine_info.setStyleSheet("background-color:gray;")
        self.machine_info.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

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
        pg.setConfigOption('background', (245, 245, 245))
        # 设置电阻曲线的表示
        self.pw = pg.PlotWidget(name='Plot1')
        self.pw.addLegend()
        self.pw.showGrid(x=True, y=True)
        self.pw.setLabel("left", "电流/电压/电阻")
        self.pw.setLabel("bottom", "半周波数")

        # 设置位移曲线的表示
        self.pw_dis = pg.PlotWidget(name='Plot_dis')
        self.pw_dis.addLegend()
        self.pw_dis.showGrid(x=True, y=True)
        self.pw_dis.setLabel("left", "位移")
        self.pw_dis.setLabel("bottom", "半周波数")

        # 设置布局
        # 设置子布局
        self.leftbox = QVBoxLayout()
        self.leftbox1 = QGridLayout()
        self.leftbox2 = QHBoxLayout()
        self.leftbox3 = QGridLayout()
        self.rightbox = QVBoxLayout()
        self.rightbox1 = QHBoxLayout()
        self.rightbox2 = QVBoxLayout()
        self.boxall = QHBoxLayout()

        ##设置分割线
        self.tab1_Hline1 = QtWidgets.QFrame()
        # self.tab1_Hline1.setGeometry(QtCore.QRect(120, 170, 118, 50))
        self.tab1_Hline1.setFrameShape(QtWidgets.QFrame.HLine)
        self.tab1_Hline1.setFrameShadow(QtWidgets.QFrame.Sunken)

        # 添加控件
        # self.newbox1.addWidget(self.label_welding_cycle)
        # self.newbox1.addWidget(self.welding_cycle)
        # self.newbox1.addWidget(self.textBrowser_recv)
        # self.leftbox.addWidget(self.textBrowser_recv)
        # self.leftbox.addLayout(self.leftbox1)

        # self.newbox2.addWidget(self.label_welding_num)
        # self.newbox2.addWidget(self.welding_num)
        # self.leftbox1.addWidget(self.welding_cycle)

        # 添加第一列

        self.leftbox1.addWidget(self.label_abnormal_welding_num, 1, 0)
        # self.leftbox1.addWidget(self.pre_display,2,0)

        # self.leftbox1.addWidget(self.process_parameter,3,0)
        self.leftbox1.addWidget(self.label_welding_cycle, 4, 0)
        self.leftbox1.addWidget(self.label_welding_current_mean, 5, 0)
        self.leftbox1.addWidget(self.label_welding_time, 6, 0)
        self.leftbox1.addWidget(self.label_current_ratio_mean_value, 7, 0)
        self.leftbox1.addWidget(self.label_distance_value, 8, 0)

        # 设备信息
        # self.leftbox1.addWidget(self.machine_info,9,0)
        # self.leftbox1.addWidget(self.label_welding_material,10,0)
        # self.leftbox1.addWidget(self.label_welding_machine, 11, 0)
        # self.leftbox1.addWidget(self.label_welding_parameter_num, 12, 0)
        # self.leftbox1.addWidget(self.tcp_character_open, 13, 0)

        # 添加第二列

        self.leftbox1.addWidget(self.abnormal_welding_num, 1, 1)
        # self.leftbox1.addWidget(self.clear_number, 2, 1)
        self.leftbox1.addWidget(self.welding_cycle, 4, 1)
        self.leftbox1.addWidget(self.welding_current_mean, 5, 1)
        self.leftbox1.addWidget(self.welding_time, 6, 1)
        self.leftbox1.addWidget(self.current_ratio_mean_value, 7, 1)
        self.leftbox1.addWidget(self.distance_value, 8, 1)

        # 设备信息
        # self.leftbox1.addWidget(self.welding_material, 10, 1)
        # self.leftbox1.addWidget(self.welding_machine, 11, 1)
        # self.leftbox1.addWidget(self.welding_parameter_num, 12, 1)

        # 添加左侧的第二个box
        self.leftbox2.addWidget(self.spacer_split)
        self.spacer_split.setStyleSheet("background-color:white;")

        # 添加左侧第三个box
        # self.leftbox3.addWidget(self.tcp_character_open)
        # self.leftbox3.addWidget(self.tcp_character_close)
        # self.leftbox3.addWidget(self.clear_number)

        #修改控件的背景颜色
        self.tcp_character_open.setStyleSheet("background-color:white;")
        self.tcp_character_close.setStyleSheet("background-color:white;")
        self.clear_number.setStyleSheet("background-color:white;")
        self.window_close.setStyleSheet("background-color:white;")
        self.reset_net.setStyleSheet("background-color:white;")

        self.leftbox.addLayout(self.leftbox1)
        self.leftbox.addWidget(self.tab1_Hline1)
        self.leftbox.addLayout(self.leftbox2)
        self.leftbox.addWidget(self.tcp_character_open)
        self.leftbox.addWidget(self.tcp_character_close)
        self.leftbox.addWidget(self.clear_number)
        self.leftbox.addWidget(self.reset_net)
        self.leftbox.addWidget(self.window_close)

        self.rightbox1.addWidget(self.label_welding_num)
        self.rightbox1.addWidget(self.welding_num)
        self.rightbox1.addWidget(self.label_welding_num2)

        self.rightbox2.addWidget(self.pw)
        self.rightbox2.addWidget(self.pw_dis)

        self.rightbox.addLayout(self.rightbox1)
        self.rightbox.addLayout(self.rightbox2)

        # 添加布局
        self.boxall.addLayout(self.rightbox)
        self.boxall.addLayout(self.leftbox)
        self.boxall.setStretch(0, 5)
        self.boxall.setStretch(1, 1)
        self.tab1.setLayout(self.boxall)
        self.tab1.setStyleSheet("background-color:rgb(245,245,245);")
        # 数组初始化

    def init_tab2(self):

        #添加控件并修改字体大小
        self.mysql_search = QPushButton('开始查找')
        self.mysql_search.setFont(QtGui.QFont("Roman times", 15))
        self.mysql_to_csv = QPushButton('导出为csv')
        self.mysql_to_csv.setFont(QtGui.QFont("Roman times", 15))
        self.label_time_start = QLabel('查询起始时间:')
        self.label_time_start.setFont(QtGui.QFont("Roman times", 15))
        self.label_time_start.setFixedHeight(60)
        self.label_time_stop = QLabel('查询终止时间:')
        self.label_time_stop.setFixedHeight(60)
        self.label_time_stop.setFont(QtGui.QFont("Roman times", 15))

        #将查询的起始时间与终止时间设定为当前时间
        self.date_time_start = QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.date_time_start.setCalendarPopup(True)
        self.date_time_start.setFixedHeight(80)
        self.date_time_start.setFont(QtGui.QFont("Roman times", 15))
        self.date_time_stop = QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.date_time_stop.setCalendarPopup(True)
        self.date_time_stop.setFixedHeight(80)
        self.date_time_stop.setFont(QtGui.QFont("Roman times", 15))

        # 初始化图形显示界面
        #设置图片背景
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOption('background', (220, 220, 198, 30))
        #设置横坐标与纵坐标
        self.pw2 = pg.PlotWidget(name='Plot2')
        self.pw2.addLegend()
        self.pw2.showGrid(x=True, y=True)
        self.pw2.setLabel("left", "位移下降速度")
        self.pw2.setLabel("bottom", "查询时间")

        self.pw2_2 = pg.PlotWidget(name='Plot2')
        self.pw2_2.addLegend()
        self.pw2_2.showGrid(x=True, y=True)
        self.pw2_2.setLabel("left", "电阻上升速度")
        self.pw2_2.setLabel("bottom", "查询时间")

        # 建立时间标签的layout，将相关的部件添加到布局中
        self.date_time_start_label = QVBoxLayout()
        self.date_time_start_label.addWidget(self.label_time_start)
        self.date_time_start_label.addWidget(self.date_time_start)

        self.date_time_stop_label = QVBoxLayout()
        self.date_time_stop_label.addWidget(self.label_time_stop)
        self.date_time_stop_label.addWidget(self.date_time_stop)

        self.tab2_left = QVBoxLayout()
        self.tab2_right = QVBoxLayout()
        self.tab2_box_all = QHBoxLayout()

        self.tab2_left.addLayout(self.date_time_start_label)
        self.tab2_left.addLayout(self.date_time_stop_label)
        self.tab2_left.addWidget(self.mysql_search)
        self.tab2_left.addWidget(self.mysql_to_csv)
        self.tab2_right.addWidget(self.pw2)
        self.tab2_right.addWidget(self.pw2_2)

        self.tab2_box_all.addLayout(self.tab2_right)
        self.tab2_box_all.addLayout(self.tab2_left)

        self.tab2_box_all.setStretch(0, 3)
        self.tab2_box_all.setStretch(1, 1)

        self.tab2.setLayout(self.tab2_box_all)

        self.mysql_search.clicked.connect(self.mysql_search_start)
        self.mysql_to_csv.clicked.connect(self.to_csv)

    def init_tab3(self):
        ##显示数据库查到的值

        self.welding_cycle_show = QLabel('周波数')
        # self.welding_cycle_show.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))
        # self.welding_cycle_show.setFixedHeight(40)
        self.welding_current_mean_show = QLabel('电流值')
        # self.welding_current_mean_show.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))
        self.welding_time_show = QLabel('焊接时间')
        # self.welding_time_show.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))
        self.current_ratio_mean_value_show = QLabel('焊接通流比%')
        # self.current_ratio_mean_value_show.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))
        self.distance_value_show = QLabel('最终位移量')
        # self.distance_value_show.setFont(QtGui.QFont("Roman times", 12, QtGui.QFont.Bold))



        #添加相关需要的控件，并修改控件大小，背景颜色，以及字体大小
        self.mysql_search_pre_result = QLabel('警报')
        self.mysql_search_pre_result.setFixedHeight(100)
        # self.mysql_search_pre_result.setFixedWidth(100)
        self.mysql_search_pre_result.setStyleSheet("background-color:green;")
        self.mysql_search_pre_result.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.mysql_search_last_point = QPushButton('查询当前数据')
        self.mysql_search_last_point.setFixedHeight(60)
        self.mysql_search_last_point.setFont(QtGui.QFont("Roman times", 15))

        self.mysql_search_previous_point = QPushButton('查询上一条数据')
        self.mysql_search_previous_point.setFixedHeight(60)
        self.mysql_search_previous_point.setFont(QtGui.QFont("Roman times", 15))
        self.mysql_abnormal_data = QPushButton('查询异常数据')
        self.mysql_abnormal_data.setEnabled(False)
        self.mysql_abnormal_data_list = QComboBox()
        self.mysql_abnormal_data_list.setFixedHeight(60)
        self.mysql_abnormal_data_list.setFont(QtGui.QFont("Roman times", 15))

        ##初始化绘图界面
        ##修改图片的背景色
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOption('background', (220, 220, 198, 30))
        ##设置横坐标与纵坐标
        self.pw3 = pg.PlotWidget(name='查询电阻曲线')
        self.pw3.addLegend()
        self.pw3.showGrid(x=True, y=True)
        self.pw3.setLabel("left", "电阻")
        self.pw3.setLabel("bottom", "查询时间")
        self.pw4 = pg.PlotWidget(name='查询位移曲线')
        self.pw4.addLegend()
        self.pw4.showGrid(x=True, y=True)
        self.pw4.setLabel("left", "位移")
        self.pw4.setLabel("bottom", "查询时间")

        ##设置布局，并将相关的控件添加到布局中
        self.tab3_left = QVBoxLayout()
        self.tab3_right = QVBoxLayout()
        self.tab3_box_all = QHBoxLayout()

        self.tab3_left.addWidget(self.mysql_search_pre_result)
        self.tab3_left.addWidget(self.welding_cycle_show)
        self.tab3_left.addWidget(self.welding_current_mean_show)
        self.tab3_left.addWidget(self.welding_time_show)
        self.tab3_left.addWidget(self.current_ratio_mean_value_show)
        self.tab3_left.addWidget(self.distance_value_show)
        self.tab3_left.addWidget(self.mysql_search_last_point)
        self.tab3_left.addWidget(self.mysql_search_previous_point)
        self.tab3_left.addWidget(self.mysql_abnormal_data)
        self.tab3_left.addWidget(self.mysql_abnormal_data_list)

        self.tab3_right.addWidget(self.pw3)
        self.tab3_right.addWidget(self.pw4)

        self.tab3_box_all.addLayout(self.tab3_right)
        self.tab3_box_all.addLayout(self.tab3_left)

        #设置左右半边的显示比例
        self.tab3_box_all.setStretch(0, 4)
        self.tab3_box_all.setStretch(1, 1)

        self.tab3.setLayout(self.tab3_box_all)

        #将按钮动作与相关的作用函数连接
        self.mysql_abnormal_data_list.activated.connect(self.abnormal_data_display)
        self.mysql_search_last_point.clicked.connect(self.mysql_last_point)
        self.mysql_search_previous_point.clicked.connect(self.mysql_previous_point)

    def init_tab4(self):
        #在界面添加相应的控件
        self.Tcp_instance_open = QPushButton('开启瞬时值采集')
        #设置控件的固定高度
        self.Tcp_instance_open.setFixedHeight(100)
        #设置字体格式与大小
        self.Tcp_instance_open.setFont(QtGui.QFont("Roman times", 20))
        #将开启瞬时值采集按钮与相应的处理函数连接
        self.Tcp_instance_open.clicked.connect(self.Tcp_instance_model_start)

        self.Tcp_instance_close = QPushButton('关闭瞬时值采集')
        self.Tcp_instance_close.setFixedHeight(100)
        self.Tcp_instance_close.setFont(QtGui.QFont("Roman times", 20))
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
        # 设置电阻曲线的表示，同时设置图像的横轴标签与纵轴标签
        self.pw_instance = pg.PlotWidget(name='Plot_ins')
        self.pw_instance.addLegend()
        self.pw_instance.showGrid(x=True, y=True)
        self.pw_instance.setLabel("left", "电流/电压/电流微分")
        self.pw_instance.setLabel("bottom", "Time (H)")

        ###添加控制瞬时值显示的控制模式

        self.recover_scale_push = QPushButton('复原')
        self.recover_scale_push.clicked.connect(self.recover_scale)

        #添加控制放大程度的slider
        self.move_slider = QSlider(QtCore.Qt.Horizontal)
        self.move_slider.setMaximum(20)
        self.move_slider.setSingleStep(0.005)
        self.move_slider.setValue(10)
        ##设定一个对比值
        self.contrast_value = 10
        self.move_slider.valueChanged.connect(self.move_changeValue)
        ##添加放大与缩小按钮
        self.blowup = QPushButton('放大')
        self.blowup.clicked.connect(self.changeValue)

        self.narrow = QPushButton('缩小')
        self.narrow.clicked.connect(self.changeValue_narrow)



        self.pw_distance_ins = pg.PlotWidget(name='Plot_dis')
        self.pw_distance_ins.addLegend()
        self.pw_distance_ins.showGrid(x=True, y=True)
        self.pw_distance_ins.setLabel("left", "位移 (mm)")
        self.pw_distance_ins.setLabel("bottom", "Time (H)")

        self.tab4_leftbox1 = QVBoxLayout()
        self.tab4_leftbox2 = QGridLayout()
        self.tab4_leftbox3 = QVBoxLayout()

        self.tab4_leftbox = QVBoxLayout()
        self.tab4_rightbox = QVBoxLayout()
        self.tab4_rightbox1 = QVBoxLayout()
        self.tab4_rightbox2 = QHBoxLayout()
        self.tab4_rightbox3 = QHBoxLayout()
        self.tab4_allbox = QHBoxLayout()

        self.tab4_leftbox1.addWidget(self.serial_display)

        self.tab4_leftbox2.addWidget(self.serial_open, 0, 0)
        self.tab4_leftbox2.addWidget(self.serial_close, 0, 1)
        self.tab4_leftbox2.addWidget(self.serial_write, 2, 0)
        self.tab4_leftbox2.addWidget(self.serial_character, 1, 1)
        self.tab4_leftbox2.addWidget(self.serial_instance, 1, 0)
        self.tab4_leftbox2.addWidget(self.serial_change, 2, 1)

        self.tab4_leftbox3.addWidget(self.Tcp_instance_open)
        self.tab4_leftbox3.addWidget(self.Tcp_instance_close)

        self.tab4_leftbox.addLayout(self.tab4_leftbox3)
        self.tab4_leftbox.addLayout(self.tab4_leftbox1)
        self.tab4_leftbox.addLayout(self.tab4_leftbox2)

        self.tab4_rightbox1.addWidget(self.pw_instance)
        self.tab4_rightbox1.addWidget(self.move_slider)

        self.tab4_rightbox2.addWidget(self.blowup)
        self.tab4_rightbox2.addWidget(self.recover_scale_push)
        self.tab4_rightbox2.addWidget(self.narrow)

        self.tab4_rightbox3.addWidget(self.pw_distance_ins)

        self.tab4_rightbox.addLayout(self.tab4_rightbox1)
        self.tab4_rightbox.addLayout(self.tab4_rightbox2)
        self.tab4_rightbox.addLayout(self.tab4_rightbox3)

        self.tab4_allbox.addLayout(self.tab4_rightbox)
        self.tab4_allbox.addLayout(self.tab4_leftbox)

        self.tab4_allbox.setStretch(0, 4)
        self.tab4_allbox.setStretch(1, 1)

        self.tab4.setLayout(self.tab4_allbox)

    def init_tab5(self):

        # self.tabbar_widget = QWidget()
        # self.tabbar_widget.setFixedHeight(170)
        # self.tabbar_widget.setFixedWidth(100)

        # 建立一个下拉控件显示机台号
        self.machine_num = QComboBox()
        # 修改控件颜色
        self.machine_num.setStyleSheet('QComboBox {background-color: #A3C1DA;color: red;}')
        # self.machine_num.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        # 调整控件大小
        # self.machine_num.setFixedHeight(25)
        # self.machine_num.setFixedWidth(100)
        # 添加需要显示的内容
        self.machine_num.addItems(['焊机编号', 'A01', 'A02', 'A03', 'A04', 'A05', 'A06', 'A07', 'A08', 'A09', 'A10', 'A11',
                                   '------', 'A12', 'A13', 'A14', 'A15', 'A16'])
        # 设置默认值
        self.machine_num.setCurrentIndex(4)
        # 默认设置不可修改
        self.machine_num.setEnabled(False)
        self.machine_num.setFont(QtGui.QFont("Roman times", 20))

        #添加显示链环规格的下拉列表
        self.chain_num = QComboBox()
        self.chain_num.setStyleSheet('QComboBox {background-color: #A3C1DA;color: red;}')
        # self.chain_num.setFixedHeight(25)
        # self.chain_num.setFixedWidth(100)
        self.chain_num.addItems(
            ['链环规格', 'G806x18', 'G807x21', 'G808x24', 'G809x27', 'G8010x30', 'G8011x33', 'G8011x66', 'G8012x36',
             'G8013x39', 'G8013x81', 'G8016x81',
             '------', 'T4x12', 'T5x15', 'T6x18', 'T6.3x19', 'T7x21', 'T7.1x21', 'T8x24', 'T9x27', 'T10x30'])
        self.chain_num.setCurrentIndex(3)
        self.chain_num.setEnabled(False)
        self.chain_num.setFont(QtGui.QFont("Roman times", 20))

        self.para_num = QComboBox()
        self.para_num.setStyleSheet('QComboBox {background-color: #A3C1DA;color: red;}')
        # self.para_num.setFixedHeight(25)
        # self.para_num.setFixedWidth(100)
        self.para_num.addItems(['规范编号', '1', '2', '3', '4'])
        self.para_num.setCurrentIndex(1)
        self.para_num.setEnabled(False)
        self.para_num.setFont(QtGui.QFont("Roman times", 20))

        self.name_num = QComboBox()
        self.name_num.setStyleSheet('QComboBox {background-color: #A3C1DA;color: red;}')
        # self.name_num.setFixedHeight(25)
        # self.name_num.setFixedWidth(100)
        self.name_num.addItems(['员工编号', '01', '02', '03', '04'])
        self.name_num.setCurrentIndex(1)
        self.name_num.setEnabled(False)
        self.name_num.setFont(QtGui.QFont("Roman times", 20))

        self.push_button = QPushButton('修改')
        # self.push_button.setStyleSheet('QPushButton {border: none;}')
        self.push_button.clicked.connect(self.infor_display)
        # self.push_button.setFixedHeight(25)
        # self.push_button.setFixedWidth(100)
        self.push_button.setFont(QtGui.QFont("Roman times", 20))

        # self.tabbar_widget.setLayout(self.tabBar_layout)

        self.set_machine_info = QLineEdit('A4')
        self.set_machine_info.setFixedWidth(100)
        self.label_set_machine_info = QLabel('焊接机台:')

        self.set_material_info = QLineEdit('8mm')
        self.set_material_info.setFixedWidth(100)
        self.label_set_material_info = QLabel('链环规格:')

        self.set_parameter_info = QLineEdit('1')
        self.set_parameter_info.setFixedWidth(100)
        self.label_set_parameter_info = QLabel('规范编号:')
        # 设置可选的异常报警信号
        self.abnormal_sound_choice = QCheckBox('关闭报警音')
        self.abnormal_sound_choice.setChecked(True)

        self.shuntdown_signal = QCheckBox('关闭关机信号')
        self.shuntdown_signal.setChecked(True)

        # 定义一个占位的控件
        self.spacer_dis = QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum,
                                      QtWidgets.QSizePolicy.Expanding)

        ##定义更新模型的相关按钮
        self.new_model = QPushButton('开始训练')
        self.new_model.setFont(QtGui.QFont("Roman times", 20))
        self.new_model.clicked.connect(self.start_establish_model)

        ##选择模型训练量
        self.model_data_num = QComboBox()
        self.model_data_num.setFont(QtGui.QFont("Roman times", 20))
        # 添加需要显示的内容
        self.model_data_num.addItems(['训练数据量：2000', '训练数据量：4000','训练数据量：6000', '训练数据量：8000',
                                      '训练数据量：10000','训练数据量：12000', '训练数据量：14000', '训练数据量：16000', '训练数据量：18000', '训练数据量：20000'])
        ##显示可选模型
        self.model_select = QComboBox()
        self.model_select.setFont(QtGui.QFont("Roman times", 20))
        ##获得可选用的list
        model_list = os.listdir(os.getcwd() + '\model')
        model_list.remove('model_select.txt')
        self.model_select.addItems(model_list)

        #显示当前使用的模型
        with open(os.getcwd() + '\model\model_select.txt') as f:
            model_using = f.readline()
        self.model_using = QLabel()
        self.model_using.setFont(QtGui.QFont("Roman times", 20))
        self.model_using.setFixedWidth(300)
        self.model_using.setText('正在使用模型:\r\n'+ model_using)

        #更改模型
        self.update_new_model = QPushButton('更改为当前选择模型')
        self.update_new_model.setFont(QtGui.QFont("Roman times", 20))
        self.update_new_model.clicked.connect(self.update_new_model_fun)

        # 初始化整体的布局
        self.tab5_leftbox1 = QVBoxLayout()
        self.tab5_leftbox2 = QVBoxLayout()
        self.tab5_rightbox1 = QHBoxLayout()
        self.tab5_allbox = QHBoxLayout()

        self.tab5_leftbox1.addWidget(self.push_button)
        self.tab5_leftbox1.addWidget(self.machine_num)
        self.tab5_leftbox1.addWidget(self.chain_num)
        self.tab5_leftbox1.addWidget(self.para_num)
        self.tab5_leftbox1.addWidget(self.name_num)
        self.tab5_leftbox1.addWidget(self.shuntdown_signal)
        self.tab5_leftbox1.addWidget(self.abnormal_sound_choice)

        self.tab5_leftbox2.addWidget(self.new_model)
        self.tab5_leftbox2.addWidget(self.model_data_num)
        self.tab5_leftbox2.addWidget(self.model_using)
        self.tab5_leftbox2.addWidget(self.model_select)
        self.tab5_leftbox2.addWidget(self.update_new_model)


        self.tab5_rightbox1.addItem(self.spacer_dis)

        # 将左右部分的布局添加到整体布局中
        self.tab5_allbox.addLayout(self.tab5_rightbox1)
        self.tab5_allbox.addLayout(self.tab5_leftbox1)
        self.tab5_allbox.addLayout(self.tab5_leftbox2)

        # 设置左右布局的比例
        self.tab5_allbox.setStretch(0, 2)
        self.tab5_allbox.setStretch(1, 2)
        self.tab5_allbox.setStretch(2, 2)

        self.tab5.setLayout(self.tab5_allbox)

        # 设置显示在tab1内容
        self.machine_num_show.setText('机台：' + self.machine_num.currentText())
        self.chain_num_show.setText('链环：' + self.chain_num.currentText())
        self.para_num_show.setText('规范：' + self.para_num.currentText())
        self.name_num_show.setText('工号：' + self.name_num.currentText())

    def window_close_fun(self):
        # 建立一个对话框
        msgBox = QMessageBox()
        msgBox.setWindowTitle('关闭测试窗口 or 关机')
        msgBox.addButton('关闭测试窗口', QMessageBox.AcceptRole)
        msgBox.addButton('关机', QMessageBox.RejectRole)
        msgBox.addButton('取消', QMessageBox.DestructiveRole)
        reply = msgBox.exec()
        if reply == QMessageBox.AcceptRole:
            # self.st.stop_thread(self.sever_date_time_show)
            #点击关闭测试窗口，将窗口关闭
            self.close()
        elif reply == QMessageBox.RejectRole:
            #点击关机，则将上位机关机
            os.system('shutdown -s -t 0')
        else:
            #否则空操作
            pass

    def infor_display(self):
        #定义修改按钮的相关操作，状态改变的同时，修改其他按钮的状态
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

            # 更新首页显示的数据
            self.machine_num_show.setText('机台：' + self.machine_num.currentText())
            self.chain_num_show.setText('链环：' + self.chain_num.currentText())
            self.para_num_show.setText('规范：' + self.para_num.currentText())
            self.name_num_show.setText('工号：' + self.name_num.currentText())


    # 清除焊接计数
    def clear_all_number(self):
        #将计数的全局变量清零
        self.welding_number = 0
        self.abnormal_welding_number = 0
        self.welding_num.setText(str(self.welding_number))
        self.abnormal_welding_num.setText(str(self.abnormal_welding_number))


    ###定义图片放缩等功能

    def changeValue(self):
        try:
            # self.pw_instance.setXRange(self.move_slider.value()/20*len(self.I_data_instance), (1-self.move_slider.value()/20)*len(self.I_data_instance), padding=0)

            self.pw_instance.setXRange(self.pw_instance.visibleRange().getRect()[0]+ 0.1 * (self.pw_instance.visibleRange().getRect()[0] + self.pw_instance.visibleRange().getRect()[2]),
                              self.pw_instance.visibleRange().getRect()[0] + self.pw_instance.visibleRange().getRect()[2]-0.1 * (
                                          self.pw_instance.visibleRange().getRect()[0] + self.pw_instance.visibleRange().getRect()[2]),
                              padding=0)
            # print(self.pw_instance.visibleRange().getRect()[0])
            # print(self.pw_instance.visibleRange())
            # self.move_slider1.setMaximum(self.move_slider.value())
        except Exception as e:
            print(e)

    def changeValue_narrow(self):
        try:
            # self.pw_instance.setXRange(self.move_slider.value()/20*len(self.I_data_instance), (1-self.move_slider.value()/20)*len(self.I_data_instance), padding=0)

            self.pw_instance.setXRange(self.pw_instance.visibleRange().getRect()[0]- 0.3 * (self.pw_instance.visibleRange().getRect()[0] + self.pw_instance.visibleRange().getRect()[2]),
                              self.pw_instance.visibleRange().getRect()[0] + self.pw_instance.visibleRange().getRect()[2]+0.3 * (
                                          self.pw_instance.visibleRange().getRect()[0] + self.pw_instance.visibleRange().getRect()[2]),
                              padding=0)
            # print(self.pw_instance.visibleRange().getRect()[0])
            # print(self.pw_instance.visibleRange())
        except Exception as e:
            print(e)

    def move_changeValue(self):
        try:
            if self.move_slider.value() > self.contrast_value:
                self.pw_instance.setXRange(self.pw_instance.visibleRange().getRect()[0] + len(self.I_data_instance)/40,
                                  self.pw_instance.visibleRange().getRect()[0] + self.pw_instance.visibleRange().getRect()[2] + len(self.I_data_instance)/40,
                                  padding=0)
            else:
                self.pw_instance.setXRange(
                    self.pw_instance.visibleRange().getRect()[0] -  len(self.I_data_instance) / 40,
                    self.pw_instance.visibleRange().getRect()[0] + self.pw_instance.visibleRange().getRect()[
                        2] - len(self.I_data_instance) / 40,
                    padding=0)
            self.contrast_value = self.move_slider.value()
            # print('moving')
        except Exception as e:
            print(e)


    def recover_scale(self):
        try:
            self.pw_instance.setXRange(0,len(self.I_data_instance))
            self.move_slider.setValue(10)
            self.contrast_value = 10
        except Exception as e:
            print(e)

    def start_establish_model(self):
        self.sever_establish_model_th = threading.Thread(target=self.establish_model)  # concurrency并行
        self.sever_establish_model_th.start()

    ##建立模型
    def establish_model(self):
        ##更改按钮状态
        self.new_model.setEnabled(False)
        self.new_model.setText('训练中')

        conn = pymysql.connect(host='localhost', port=3306, user='root', password='', database='resistance')
        cs1 = conn.cursor()
        all_character = pd.DataFrame()
        cs1.execute('use resistance')
        print(self.model_data_num.currentText().split('：'))
        cs1.execute("select * from {}_{} order by id desc limit {}".format(datetime.datetime.now().year,
                                                                           datetime.datetime.now().month,
                                                                           int(self.model_data_num.currentText().split('：')[1])))

        columns_name = cs1.fetchall()
        cs1.close()
        character_data = pd.DataFrame(np.array(columns_name)).iloc[:, -12:]
        print(character_data.shape)
        now_time = datetime.datetime.now()
        os.makedirs(os.getcwd() + '\\model\\{}'.format(
            str(now_time.year) + '-' + str(now_time.month) + '-' + str(now_time.day) + ' ' +
            str(now_time.hour) + '_' + str(now_time.minute) + '_' + str(now_time.second)))
        self.new_model_dir = str(now_time.year) + '-' + str(now_time.month) + '-' + str(now_time.day) + ' ' + str(now_time.hour) + '_' + str(now_time.minute) + '_' + str(now_time.second)
        ##使用LOF进行预测
        lof = LocalOutlierFactor(novelty=True, n_neighbors=10, contamination=0.028)  # LOF模型实例化，0.028表示异常点在所有数据点中所占的比率
        # error_lof_index = data_ana[clf.fit_predict(data_ana) == -1].index  #将LOF模型判断为异常的点的索引列出
        lof_result = lof.fit(character_data)
        with open(os.getcwd() + '\\model\\{}\\lof.model'.format(
                str(now_time.year) + '-' + str(now_time.month) + '-' + str(now_time.day) + ' ' +
                str(now_time.hour) + '_' + str(now_time.minute) + '_' + str(now_time.second)), 'wb') as f:
            pickle.dump(lof, f)

        ##使用孤立森林进行预测

        ilf = IsolationForest(max_samples=100, random_state=42, n_estimators=200, contamination=0.028)  # 模型实例化

        ilf_result = ilf.fit_predict(character_data)
        with open(os.getcwd() + '\\model\\{}\\ilf.model'.format(
                str(now_time.year) + '-' + str(now_time.month) + '-' + str(now_time.day) + ' ' +
                str(now_time.hour) + '_' + str(now_time.minute) + '_' + str(now_time.second)), 'wb') as f:
            pickle.dump(ilf, f)

            ##使用elf进行预测
        elf = EllipticEnvelope(support_fraction=1, contamination=0.028)
        elf_result = elf.fit_predict(character_data)
        with open(os.getcwd() + '\\model\\{}\\elf.model'.format(
                str(now_time.year) + '-' + str(now_time.month) + '-' + str(now_time.day) + ' ' +
                str(now_time.hour) + '_' + str(now_time.minute) + '_' + str(now_time.second)), 'wb') as f:
            pickle.dump(elf, f)
        self.new_model_msg.emit('ok')
        ##更改按钮状态
        self.new_model.setEnabled(True)
        self.new_model.setText('开始训练')
        self.st.stop_thread(self.sever_establish_model_th)

    def update_model_select(self):
        self.model_select.addItem(self.new_model_dir)

    ###更改模型
    def update_new_model_fun(self):
        self.model_using.setText('正在使用模型：\r\n' + self.model_select.currentText())
        with open(os.getcwd() + '\model\model_select.txt','w') as f:
            f.write(self.model_select.currentText())

        self.init_model()