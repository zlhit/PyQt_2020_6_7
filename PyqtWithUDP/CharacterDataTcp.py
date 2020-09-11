import socket
import threading
import serial
import time
import binascii
import numpy as np
import pyqtgraph as pg
import pymysql
import datetime
import winsound

class character_data:

    def tcp_server_start(self):
        """
        功能函数，TCP服务端开启的方法
        :return: None
        """
        self.msg_list = []
        self.msg_list_sub = []
        # 将瞬时值采集设为不可用
        self.Tcp_instance_open.setEnabled(False)
        # 将特征值采集设为不可用
        self.tcp_character_open.setEnabled(False)
        # 将特征值采集关闭按钮设为可用
        self.tcp_character_close.setEnabled(True)
        # 将关闭窗口设为不可用
        self.window_close.setEnabled(False)

        # 将查询数据禁用
        self.tab2.setEnabled(False)
        self.tab3.setEnabled(False)
        # 禁用串口
        self.serial_open.setEnabled(False)

        # 建立TCP连接
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.setblocking(False)

        # 建立udp发送数据
        # self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_connect = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            # 特征值采集服务器的端口号
            self.port = int(4144)
            # 提取本机IP
            self.ip = socket.gethostbyname(socket.gethostname())
            self.tcp_socket.bind((self.ip, self.port))
            # self.udp_socket.bind((self.ip, 9998))
            self.udp_connect.bind((self.ip, 9998))
            print(self.ip)
            print('绑定端口')
        except Exception as e:
            print(e)
        else:
            # 打开tcp监听
            self.tcp_socket.listen()
            # 开一个tcp采集数据的子线程
            self.sever_th = threading.Thread(target=self.tcp_server_concurrency)
            self.sever_th.start()
            # self.msg = 'TCP服务端正在监听端口:%s\n' % str(self.port)
            # self.signal_write_msg.emit("写入")

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
            # self.udp_socket.close()
            self.udp_connect.close()
            self.st.stop_thread(self.sever_th)
            print('close')
        except:
            pass

        # 将特征值信号清空
        self.msg_list = []
        self.msg_list_sub = []
        # 切换按钮状态
        self.tcp_character_open.setEnabled(True)
        self.tcp_character_close.setEnabled(False)
        self.Tcp_instance_open.setEnabled(True)
        self.window_close.setEnabled(True)
        # 将查询数据启用
        self.tab2.setEnabled(True)
        self.tab3.setEnabled(True)
        # 禁用串口
        self.serial_open.setEnabled(True)

    def tcp_server_concurrency(self):
        """
        功能函数，供创建线程的方法；
        使用子线程用于监听并创建连接，使主线程可以继续运行，以免无响应
        使用非阻塞式并发用于接收客户端消息，减少系统资源浪费，使软件轻量化
        :return:None
        """
        ##向串口发送信息，进入特征值模式
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
                # 0.001s以后继续监听
                time.sleep(0.001)
            else:
                self.client_socket.setblocking(False)
                # 将创建的客户端套接字存入列表
                self.client_socket_list.append((self.client_socket, self.client_address))
            # 轮询客户端套接字列表，接收数据
            for client, address in self.client_socket_list:
                try:
                    # 将tcp收到的数赋予变量
                    self.recv_msg = client.recv(1024)

                except:
                    pass
                else:
                    if self.recv_msg:
                        # 将16进制转换为字符串
                        data_ = str(binascii.b2a_hex(self.recv_msg), 'utf-8')
                        # 将字符串切割为2各一组
                        data_list_ = [data_[i:i + 2] for i in range(0, len(data_), 2)]


                       # print(len(self.msg_list))

                        ##如果本次拿到的数大于4个，就对是否存在标头进行判断
                        if len(data_list_) > 4:
                            if data_list_[0]+ data_list_[1]+data_list_[2] == 'aabbcc':
                                # 取出半波数
                                self.msg_list = []
                                self.halfwave_num = int(data_list_[3], 16)
                        else:
                            ##不是第一次拿到
                            if len(self.msg_list) > 0:
                                pass
                            ##第一次拿到
                            else:
                                self.halfwave_num = 30
                        self.msg_list.extend(data_list_)
                        if len(self.msg_list) > self.halfwave_num * 30 + 6 + 1:
                            self.msg_list = []

                        # 如果收集到的数达到指定数量，开始继续处理
                        if len(self.msg_list) == self.halfwave_num * 30 + 6:
                            self.msg_list_sub = self.msg_list[3:]
                            print(len(self.msg_list))
                            print(self.halfwave_num)
                            #print(self.msg_list)
                            
             
                            try:
                                self.time1 = time.time()
                                # print(self.msg_list_sub)
                                # print(self.msg_list_sub)
                                # print(len(self.msg_list_sub))
                                # self.msg_list_sub = [self.msg[i:i+2] for i in range(0,len(self.msg),2)]

                                # 取出通流比数据
                                self.current_ratio = sum([int(self.msg_list_sub[1:self.halfwave_num * 2 + 1][i + 1] +
                                                              self.msg_list_sub[1:self.halfwave_num * 2 + 1][i], 16) for i
                                                          in range(0, self.halfwave_num * 2, 2)]) / (
                                                                 10.0 * self.halfwave_num)
                                # 取出电流有效值
                                self.current_rms_str_list = self.msg_list_sub[
                                                            1 + 2 * self.halfwave_num:1 + 2 * self.halfwave_num + 8 * self.halfwave_num]

                                self.current_rms_list = [(int(
                                    self.current_rms_str_list[i + 7] + self.current_rms_str_list[i + 6] +
                                    self.current_rms_str_list[i + 5] + self.current_rms_str_list[i + 4] +
                                    self.current_rms_str_list[i + 3] + self.current_rms_str_list[i + 2] +
                                    self.current_rms_str_list[i + 1] + self.current_rms_str_list[i], 16)) ** 0.5
                                                         for i in range(0, self.halfwave_num * 8, 8)]
                                # 取出电压有效值
                                self.voltage_rms_str_list = self.msg_list_sub[
                                                            1 + 2 * self.halfwave_num + 8 * self.halfwave_num:1 + 2 * self.halfwave_num + 8 * self.halfwave_num + 8 * self.halfwave_num]

                                self.voltage_rms_list = [(int(
                                    self.voltage_rms_str_list[i + 7] + self.voltage_rms_str_list[i + 6] +
                                    self.voltage_rms_str_list[i + 5] + self.voltage_rms_str_list[i + 4] +
                                    self.voltage_rms_str_list[i + 3] + self.voltage_rms_str_list[i + 2] +
                                    self.voltage_rms_str_list[i + 1] + self.voltage_rms_str_list[i], 16)) ** 0.5
                                                         for i in range(0, self.halfwave_num * 8, 8)]
                                # 取出电流平均值
                                self.current_mean_str_list = self.msg_list_sub[
                                                             1 + 2 * self.halfwave_num + 2 * 8 * self.halfwave_num:1 + 2 * self.halfwave_num + 8 * self.halfwave_num * 2 + 4 * self.halfwave_num]

                                self.current_mean_list = [
                                    int(self.current_mean_str_list[i + 3] + self.current_mean_str_list[i + 2] +
                                        self.current_mean_str_list[i + 1] + self.current_mean_str_list[i], 16)
                                    for i in range(0, self.halfwave_num * 4, 4)]

                                # 取出电压平均值
                                self.voltage_mean_str_list = self.msg_list_sub[
                                                             1 + 2 * self.halfwave_num + 2 * 8 * self.halfwave_num + 4 * self.halfwave_num:1 + 2 * self.halfwave_num + 8 * self.halfwave_num * 2 + 4 * self.halfwave_num * 2]

                                self.voltage_mean_list = [
                                    int(self.voltage_mean_str_list[i + 3] + self.voltage_mean_str_list[i + 2] +
                                        self.voltage_mean_str_list[i + 1] + self.voltage_mean_str_list[i], 16)
                                    for i in range(0, self.halfwave_num * 4, 4)]

                                # 计算电阻值
                                self.resistance_list = [
                                    int(self.voltage_mean_list[i] * 10000 / self.current_mean_list[i]) for i in
                                    range(self.halfwave_num)]

                                # 取出位移的平均值
                                self.distance_mean_str_list = self.msg_list_sub[
                                                              1 + 2 * self.halfwave_num + 2 * 8 * self.halfwave_num + 4 * self.halfwave_num * 2:1 + 2 * self.halfwave_num + 8 * self.halfwave_num * 2 + 4 * self.halfwave_num * 3]

                                self.distance_list = [
                                    int(self.distance_mean_str_list[i + 3] + self.distance_mean_str_list[i + 2] +
                                        self.distance_mean_str_list[i + 1] + self.distance_mean_str_list[i], 16)
                                    for i in range(0, self.halfwave_num * 4, 4)]

                                ##开始计算特征值
                                # 电阻特征值
                                # print(list(self.Z_score(self.resistance_list)))
                                self.resistance_max = max(self.Z_score(self.resistance_list))  # 电阻峰值
                                self.resistance_min = min(self.Z_score(self.resistance_list))  # 电阻基值
                                self.resistance_max_index = self.Z_score(self.resistance_list).index(
                                    self.resistance_max)
                                self.resistance_min_index = self.Z_score(self.resistance_list).index(
                                    self.resistance_min)
                                ##电阻上升速度
                                self.resistance_increase_rate = (self.resistance_max - self.resistance_min) / (
                                            self.resistance_max_index - self.resistance_min_index)
                                # 电阻上升时间占总时间的比例
                                self.resistance_increase_ratio = (
                                                                             self.resistance_max_index - self.resistance_min_index) / self.halfwave_num
                                # 电阻初始值与最小值的差值
                                self.resistance_first_min = self.Z_score(self.resistance_list)[
                                                                0] - self.resistance_min + 0.5
                                # 电阻最终值与峰值的差值
                                self.resistance_last_max = self.resistance_max - self.Z_score(self.resistance_list)[
                                    -1] + 0.5

                                ##位移特征值
                                self.distance_max = max(self.Z_score(self.distance_list))  # 位移峰值
                                self.distance_min = min(self.Z_score(self.distance_list))  # 位移基值
                                self.distance_max_index = self.Z_score(self.distance_list).index(self.distance_max)
                                self.distance_min_index = self.Z_score(self.distance_list).index(self.distance_min)

                                ##位移下降速度
                                self.distance_decrease_rate = (self.distance_max - self.distance_min) / (
                                            self.distance_max_index - self.distance_min_index)
                                # 位移下降时间占总时间的比例
                                self.distance_decrease_ratio = (
                                                                           self.distance_min_index - self.distance_max_index) / self.halfwave_num
                                # 位移初始值与最大值的差值
                                self.distance_first_max = self.distance_max - self.Z_score(self.distance_list)[0] + 0.5
                                # 位移最终值与最小值的差值
                                self.distance_last_min = self.Z_score(self.distance_list)[-1] - self.distance_min + 0.5

                                # 计算位移的特征
                                self.distance_decr = (max(self.distance_list) - min(self.distance_list)) / max(
                                    self.distance_list)

                                ##整合特征值
                                self.character_data = [[
                                    self.resistance_max, self.resistance_min, self.resistance_increase_rate,
                                    self.resistance_increase_ratio,
                                    self.resistance_first_min, self.resistance_last_max,
                                    self.distance_max, self.distance_min, self.distance_decrease_rate,
                                    self.distance_decrease_ratio,
                                    self.distance_first_max, self.distance_last_min
                                ]]
                                # print(self.character_data)
                                # 判断数据是否异常
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
                                self.msg_list_sub = []
                            else:
                                self.msg_list = []
                                self.msg_list_sub = []
                                self.signal_write_msg.emit("写入")
                                self.tab1.setStyleSheet("background-color:rgb(245,245,245);")

                                ##将数据存入数据库
                                try:
                                    #连接数据库
                                    self.conn_insert = pymysql.connect(host='localhost', port=3306, user='root',
                                                                       password='',
                                                                       database='resistance')
                                    self.cs2 = self.conn_insert.cursor()
                                    self.cs2.execute('use resistance')
                                    # print(len(self.character_data))
                                    
                                    #判断本月的表是否存在
                                    self.cs2.execute(
                                        "SELECT table_name FROM information_schema.TABLES WHERE table_name ='{}_{}'".format(
                                            datetime.datetime.now().year, datetime.datetime.now().month))
                                    #如果存在，空操作
                                    if self.cs2.fetchall():
                                        pass
                                    #如果不存在，就按照既定的数据模式创建新表
                                    else:
                                        sql_create_table = "create table {}_{} (ID int auto_increment primary key,time datetime, preict_result varchar(10), welding_machine varchar(10),welding_material varchar(20)," \
                                                           "welding_parameter varchar(10), welding_num varchar(10), welding_cycle varchar(10),distance_last varchar(10)," \
                                                           "weld1time varchar(10), weld1current varchar(10), weld1ratio varchar(10), weld2time varchar(10),weld2current varchar(10), " \
                                                           "weld2ratio varchar(10),weld3time varchar(10),weld3current varchar(10), weld3ratio varchar(10),distance varchar(200),resistance varchar(200)," \
                                                           "R_max varchar(30),R_min varchar(30),R_increase_rate varchar(30),R_IncreaseTime_ratio varchar(30),R0_Rmin varchar(30),Rlast_Rmax varchar(30)," \
                                                           "D_max varchar(30),D_min varchar(30),D_decrease_rate varchar(30),D_DecreaseTime_ratio varchar(30)," \
                                                           "D0_Dmax varchar(30),Dlast_Dmin varchar(30))".format(
                                            datetime.datetime.now().year, datetime.datetime.now().month)
                                        self.cs2.execute(sql_create_table)
                                        # print(sql_create_table)

                                    #将本次数据存入数据库中
                                    sql_ = "insert into {} values(0,'{}','{}','{}','{}','{}','1','{}','{}','{}','{}','{}',null,null,null,null,null,null,'{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
                                        str(datetime.datetime.now().year) + '_' + str(datetime.datetime.now().month),
                                        datetime.datetime.now(), self.pre_result,
                                        self.machine_num.currentText(), self.chain_num.currentText(),
                                        self.para_num.currentText(), self.halfwave_num,
                                        round(self.distance_decr, 2), self.halfwave_num * 20 / 2,
                                        int(np.mean(self.current_rms_list) / 1e5), round(self.current_ratio, 2),
                                        str(self.distance_list[:-4])[1:-1], str(self.resistance_list)[1:-1],
                                        self.character_data[0][0], self.character_data[0][1], self.character_data[0][2],
                                        self.character_data[0][3], self.character_data[0][4], self.character_data[0][5],
                                        self.character_data[0][6], self.character_data[0][7],
                                        self.character_data[0][8], self.character_data[0][9],
                                        self.character_data[0][10], self.character_data[0][11]
                                        )
                                    self.cs2.execute(sql_)
                                    # self.cs1.execute('select * from 2020_7')
                                    self.conn_insert.commit()
                                    self.conn_insert.close()

                                    print(1)
                                except Exception as e:
                                    print(e)
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
        # 计算一些需要及时显示的数据

        #如果本次数据为异常数据，则创建子线程进行异常报警与关闭机器
        if self.pre_result == -1:
            self.tab1.setStyleSheet("background-color:red;")
            #异常焊点数+1
            self.abnormal_welding_number += 1
            #建立并开启异常报警与关机信号的子线程
            self.sever_sound = threading.Thread(target=self.abnormal_sound_play)
            self.sever_sound.start()
            self.serve_shuntdown = threading.Thread(target=self.shuntdown_signal_process)
            self.serve_shuntdown.start()
        else:
            pass
        #焊接点数+1
        self.welding_number += 1
        # 将之前焊点的图片清空
        self.pw.clear()
        self.pw_dis.clear()
        # 将特征值显示到界面
        self.welding_num.setText(str(self.welding_number))  # 焊接点数
        self.abnormal_welding_num.setText(str(self.abnormal_welding_number))  # 焊接异常点个数
        self.welding_cycle.setText(str(self.halfwave_num / 2))  # 焊接周波数
        self.welding_time.setText(str(self.halfwave_num * 20 / 2))  # 焊接时间
        self.welding_current_mean.setText(str(int(np.mean(self.current_rms_list) / 1e1)))  # 焊接电流
        self.current_ratio_mean_value.setText(str(round(self.current_ratio, 2)))  # 焊接通流比s
        self.distance_value.setText(str(round(self.distance_decr, 2)))  # 最终位移量

        # self.pw.plot(range(self.halfwave_num),(self.current_rms_list-np.mean(self.current_rms_list))/np.std(self.current_rms_list), name='电流', pen=pg.mkPen(color='r'), symbol='s', symbolSize=10, symbolBrush=('r'))
        self.pw.plot(range(self.halfwave_num), self.Z_score(self.current_rms_list), name='电流', pen=pg.mkPen(color='r')
                     # , symbol='+', symbolSize=10, symbolBrush=('r')
                     )
        # self.pw.plot(range(self.halfwave_num), (self.voltage_rms_list-np.mean(self.voltage_rms_list))/np.std(self.voltage_rms_list),name='电压', pen=pg.mkPen(color='b'), symbol='+', symbolSize=10, symbolBrush=('b'))
        self.pw.plot(range(self.halfwave_num), self.Z_score(self.voltage_rms_list), name='电压', pen=pg.mkPen(color='b')
                     # , symbol='+', symbolSize=10, symbolBrush=('b')
                     )
        # self.pw.plot(range(self.halfwave_num), (self.resistance_list-np.mean(self.resistance_list))/np.std(self.resistance_list),name='电阻', pen=pg.mkPen(color='k'), symbol='+',symbolSize=10, symbolBrush=('k'))
        self.pw.plot(range(self.halfwave_num), self.Z_score(self.resistance_list), name='电阻', pen=pg.mkPen(color='k')
                     # , symbol='s',symbolSize=10, symbolBrush=('k')
                     )

        self.pw_dis.plot(range(self.halfwave_num), self.distance_list, name='位移', pen=pg.mkPen(color='r')
                         # , symbol='s', symbolSize=10, symbolBrush=('r')
                         )
        self.time2 = time.time()
        self.udp_connect.sendto(
            ((str(datetime.datetime.now()) + ';' + str(self.pre_result) + ';' + self.machine_num.currentText()
              + ';' + str(round(self.current_ratio, 2)) + ';' + str(self.distance_list[:-4])[1:-1] + ';' + str(
                        self.resistance_list)[1:-1] + ';' +
              str(self.character_data[0])).encode('utf-8')), (self.ip, 1001))
        # self.udp_socket.sendto(str(1122).encode('utf-8'), (self.ip, 1001))
        print(self.time2 - self.time1)

    #异常报警音处理函数
    def abnormal_sound_play(self):
        if self.pre_result == -1:
            # self.pre_display.setStyleSheet("background-color:red;")
            #判断主界面中报警音是否被选中
            if self.abnormal_sound_choice.isChecked():
                pass
            else:
                #如果播放异常报警音，则报警
                winsound.PlaySound('警报1.wav', winsound.SND_FILENAME)
        else:
            pass
        #停止子线程
        self.st.stop_thread(self.sever_sound)

    #建立子线程进行
    def reset_net_fun(self):
        self.sever_reset_net = threading.Thread(target=self.reset_net_fun_theard)
        self.sever_reset_net.start()
        self.reset_net.setEnabled(False)
    
    #定义复位函数
    def reset_net_fun_theard(self):
        #连接串口并向下位机发送相关命令，恢复到之前的状态
        serial_ = serial.Serial(self.com_num, 115200, timeout=0.5)
        serial_.write(b'\x01')
        time.sleep(0.3)
        serial_.write(b'\x35')
        time.sleep(0.1)
        serial_.close()
        time.sleep(0.2)
        
        #自动回到tcp特征值状态采集
        self.tcp_server_start()

        #修改相关按钮状态
        self.Tcp_instance_open.setEnabled(False)
        self.Tcp_instance_close.setEnabled(False)
        self.tcp_character_open.setEnabled(False)
        self.tcp_character_close.setEnabled(True)

    #定义关机信号的相关操作
    def shuntdown_signal_process(self):
        if self.shuntdown_signal.isChecked():
            pass
        else:
            #向下位机发送相关命令，进入停机状态
            serial_ = serial.Serial(self.com_num, 115200, timeout=0.5)
            serial_.write(b'\x01')
            time.sleep(0.3)
            serial_.write(b'\x01')
            time.sleep(0.3)
            serial_.write(b'\x33')
            time.sleep(0.1)
            serial_.close()
            print('signal emit')

            #更改相关的按钮状态
            self.reset_net.setEnabled(True)
            self.Tcp_instance_open.setEnabled(False)
            self.Tcp_instance_close.setEnabled(False)
            self.tcp_character_open.setEnabled(False)
            self.tcp_character_close.setEnabled(False)
        #停止子线程
        self.st.stop_thread(self.serve_shuntdown)