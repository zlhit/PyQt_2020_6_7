import sys
from PyQt5.QtWidgets import QMainWindow,QApplication
from PyQt5.QtGui import QIcon
class FirstMainWindow (QMainWindow):
    def __init__(self):
        super(FirstMainWindow,self).__init__()
        #设置窗口标题
        self.setWindowTitle('电阻点焊')
        self.resize(400,300)
        self.status = self.statusBar()
        self.status.showMessage('停留5秒钟',5000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = FirstMainWindow()
    main.show()
    sys.exit(app.exec_())

