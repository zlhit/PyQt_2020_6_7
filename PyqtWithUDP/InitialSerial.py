import serial
import time

class Initial_Serial:
    def __init__(self):
         # 初始化串口的端口号
        self.com_num = 'COM1'

    def serial_start(self):
        print('串口打开')
        #打开串口
        self.serial_ = serial.Serial(self.com_num, 115200, timeout=0.5)
        #改变相应的按钮状态
        self.serial_write.setEnabled(True)
        self.serial_close.setEnabled(True)
        self.serial_character.setEnabled(True)
        self.serial_instance.setEnabled(True)
        self.serial_change.setEnabled(True)
        self.serial_open.setEnabled(False)

        # 将采集相关按钮关闭
        self.tcp_character_open.setEnabled(False)
        self.tcp_character_close.setEnabled(False)
        self.Tcp_instance_open.setEnabled(False)
        self.Tcp_instance_close.setEnabled(False)

    def serial_change_mode(self):
        #向串口发送01
        self.serial_.write(b'\x01')

    def serial_character_mode(self):
        #向串口发送01，11
        self.serial_.write(b'\x01')
        time.sleep(0.5)
        self.serial_.write(b'\x11')

    def serial_instance_mode(self):
        #向串口发送01，13
        self.serial_.write(b'\x01')
        time.sleep(0.5)
        self.serial_.write(b'\x13')

    def serial_read_data(self):
        #读取串口数据
        serial_text = self.serial_.read_all()
        self.serial_display.setText(str(serial_text))

    def serial_stop(self):
        #将串口关闭
        self.serial_.close()
        
        #改变相关按钮状态
        self.serial_write.setEnabled(False)
        self.serial_close.setEnabled(False)
        self.serial_character.setEnabled(False)
        self.serial_instance.setEnabled(False)
        self.serial_change.setEnabled(False)
        self.serial_open.setEnabled(True)
        # 将采集相关按钮关闭
        self.tcp_character_open.setEnabled(True)
        self.tcp_character_close.setEnabled(False)
        self.Tcp_instance_open.setEnabled(True)
        self.Tcp_instance_close.setEnabled(False)
        # 启用串口
        self.serial_open.setEnabled(True)

