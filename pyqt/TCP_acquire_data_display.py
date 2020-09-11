import numpy as np
import sys
import matplotlib

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


class App(QWidget):
    def __init__(self, parent=None):
        # 父类初始化方法
        super(App, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('TCP_acquire_data')
        self.setWindowIcon(QIcon('电力图标.jpg'))
        self.setWindowIcon(QIcon('2345_image_file_copy_1.jpg'))
        self.setFixedSize(1200, 700)
        self.setMinimumSize(1200, 700)
        self.setMaximumSize(1200, 700)
        # 几个QWidgets

        self.welding_cycle = QLabel('waiting for welding')
        self.label_welding_cycle = QLabel('焊接周波数:')




        self.welding_num = QLabel('waiting for welding')
        self.label_welding_num = QLabel('焊接数:')



        self.start_sample = QPushButton('开始采集')
        self.start_sample.clicked.connect(self.showTime)




        # 图像模块
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        #设置布局
        #设置子布局
        self.newbox1 = QHBoxLayout()
        self.newbox2 = QHBoxLayout()

        self.leftbox1 = QVBoxLayout()
        self.rightbox1 = QHBoxLayout()
        self.boxall = QHBoxLayout()

        # 添加控件
        self.newbox1.addWidget(self.label_welding_cycle)
        self.newbox1.addWidget(self.welding_cycle)
        # self.newbox1.addWidget(self.welding_cycle_display)


        self.newbox2.addWidget(self.label_welding_num)
        self.newbox2.addWidget(self.welding_num)
        #self.leftbox1.addWidget(self.welding_cycle)
        self.leftbox1.addLayout(self.newbox2)
        self.leftbox1.addLayout(self.newbox1)
        self.leftbox1.addWidget(self.start_sample)


        self.rightbox1.addWidget(self.canvas)

        #添加布局
        self.boxall.addLayout(self.leftbox1)
        self.boxall.addLayout(self.rightbox1)
        self.setLayout(self.boxall)
        # 数组初始化
        self.x = []






    def showTime(self):
            print(3)
            shuju = [np.random.random_sample(),np.random.random_sample()] * 10  # 返回一个[0,1)之间的浮点型随机数*10
            print(shuju)
            self.welding_cycle.setText(str(shuju[-1]))
            self.welding_num.setText(str(shuju[-2]))
            self.x = shuju  # 数组更新
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