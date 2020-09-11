import numpy as np
import sys
import matplotlib
import socket
import threading

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
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

#

class App(QTabWidget):
    # 定义一个信号
    signal_write_msg = QtCore.pyqtSignal(str)

    def __init__(self):
        # 父类初始化方法
        super(App, self).__init__()

        self.setWindowTitle('TCP_acquire_data')
        self.setWindowIcon(QIcon('电力图标.jpg'))
        self.setWindowIcon(QIcon('2345_image_file_copy_1.jpg'))
        self.setFixedSize(1700, 700)
        self.setMinimumSize(1200, 700)
        self.setMaximumSize(2000, 700)


        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()

        self.addTab(self.tab1,'特征值监控')
        self.addTab(self.tab2,'查询数据库')
        self.addTab(self.tab3,'选项卡3')


        self.init_tab1()
        self.tcp_server_start()
        self.signal_write_msg.connect(self.write_msg)
        self.client_socket_list = list()

    def init_tab1(self):
        # 设置QWidgets


        #添加Tab选项
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("特征值监控")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")

        #设置相关焊接参数显示
        self.welding_cycle = QLabel('waiting for welding')
        self.label_welding_cycle = QLabel('焊接周波数:')


        self.welding_num = QLabel('waiting for welding')
        self.label_welding_num = QLabel('焊接数:')


        # 图像模块
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        #设置布局
        #设置子布局
        self.newbox1 = QHBoxLayout()
        self.newbox2 = QHBoxLayout()


        self.leftbox1 = QGridLayout()
        self.rightbox1 = QHBoxLayout()
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
        self.leftbox1.addWidget(self.welding_cycle,0,1)
        self.leftbox1.addWidget(self.welding_num,1,1)
        self.leftbox1.addWidget(self.label_welding_cycle,0,0)
        self.leftbox1.addWidget(self.label_welding_num,1,0)

        self.rightbox1.addWidget(self.canvas)




        #添加布局
        self.boxall.addLayout(self.leftbox1)
        self.boxall.addLayout(self.rightbox1)
        self.boxall.setStretch(0,1)
        self.boxall.setStretch(1,4)
        self.tab1.setLayout(self.boxall)
        # 数组初始化
        self.x = []

    def tcp_server_start(self):
        """
        功能函数，TCP服务端开启的方法
        :return: None
        """
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.setblocking(False)
        try:
            self.port = int(4144)
            self.tcp_socket.bind(('192.168.8.103', self.port))
            print('绑定端口')
        except Exception as ret:
            self.msg = '请检查端口号\n'
            self.signal_write_msg.emit("写入")
        else:
            self.tcp_socket.listen()
            self.sever_th = threading.Thread(target=self.tcp_server_concurrency)
            self.sever_th.start()
            #self.msg = 'TCP服务端正在监听端口:%s\n' % str(self.port)
            #self.signal_write_msg.emit("写入")
            print('打开TCP连接')

    def tcp_server_concurrency(self):
        """
        功能函数，供创建线程的方法；
        使用子线程用于监听并创建连接，使主线程可以继续运行，以免无响应
        使用非阻塞式并发用于接收客户端消息，减少系统资源浪费，使软件轻量化
        :return:None
        """
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
                    recv_msg = client.recv(1024)
                except Exception as ret:
                    pass
                else:
                    if recv_msg:
                        msg = recv_msg.decode('utf-8')
                        #self.msg = '来自IP:{}端口:{}:\n{}\n'.format(address[0], address[1], msg)
                        self.msg = msg
                        self.signal_write_msg.emit("写入")
                    else:
                        client.close()
                        self.client_socket_list.remove((client, address))


    def write_msg(self):
        """
        功能函数，向接收区写入数据的方法
        信号-槽触发
        tip：PyQt程序的子线程中，使用非规定的语句向主线程的界面传输字符是不允许的
        :return: None
        """
        self.welding_num.setText(self.msg)
        self.welding_cycle.setText(self.msg)
        self.x.append(int(self.msg))  # 数组更新
        ax = self.figure.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.clear()
        ax.plot(self.x)
        self.canvas.draw()



# 运行程序
if __name__ == '__main__':
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    main_window = App()
    main_window.show()
    app.exec()