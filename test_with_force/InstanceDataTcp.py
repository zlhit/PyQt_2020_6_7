import socket
import threading
import serial
import time
import binascii
import numpy as np
import pyqtgraph as pg


class instance__data:

    def Tcp_instance_model_start(self):
        """
        功能函数，TCP服务端开启的方法
        :return: None
        """
        #建立Tcp服务器，并绑定相应的IP地址与相应的端口号
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
            #开启Tcp侦听
            self.tcp_socket_instance.listen()
            #建立并开启收集数据子线程
            self.sever_th_instance = threading.Thread(target=self.tcp_server_concurrency_instance)
            self.sever_th_instance.start()
            # self.msg = 'TCP服务端正在监听端口:%s\n' % str(self.port)
            # self.signal_write_msg.emit("写入")
        #修改相应的按钮状态
        self.Tcp_instance_open.setEnabled(False)
        self.Tcp_instance_close.setEnabled(True)
        self.tcp_character_open.setEnabled(False)
        self.window_close.setEnabled(False)
        # 将查询数据禁用
        self.tab2.setEnabled(False)
        self.tab3.setEnabled(False)
        self.tab5.setEnabled(True)
        # 禁用串口
        self.serial_open.setEnabled(False)

    def tcp_server_concurrency_instance(self):
        """
        功能函数，供创建线程的方法；
        使用子线程用于监听并创建连接，使主线程可以继续运行，以免无响应
        使用非阻塞式并发用于接收客户端消息，减少系统资源浪费，使软件轻量化
        :return:None
        """
        ##向串口发送信息，开启瞬时值采集模式
        self.data_instance = []
        serial_ = serial.Serial(self.com_num, 115200, timeout=0.5)
        serial_.write(b'\x01')
        time.sleep(0.5)
        serial_.write(b'\x13')
        time.sleep(0.1)
        serial_.close()

        ##进入采集数据循环
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
                    #如果数据非空
                    if recv_msg:
                        #将位数据数据转换为字符串数据
                        data = str(binascii.b2a_hex(recv_msg), 'utf-8')
                        #每2个数一组切割字符串
                        data_list = [data[i:i + 2] for i in range(0, len(data), 2)]
                        #将该次收到的数据添加到数据缓冲区
                        self.data_instance.extend(data_list)

                        #如果数据大小超过规定大小，则清空接收缓冲区
                        if len(self.data_instance) > 316001:
                            self.data_instance = []
                        # print(len(self.data_instance))

                        #数据大小正确，进入数据处理模式
                        if len(self.data_instance) == 314000:
                            self.time3 = time.time()
                            print(len(self.data_instance))
                            ##电压瞬时值
                            self.U_data_instance_list = self.data_instance[: 100000]
                            self.U_data_instance = [
                                int(self.U_data_instance_list[i + 1] + self.U_data_instance_list[i], 16)
                                for i in range(0, len(self.U_data_instance_list), 2)]
                            #电流瞬时值
                            self.I_data_instance_list = self.data_instance[100000: 2 * 100000]
                            self.I_data_instance = [
                                int(self.I_data_instance_list[i + 1] + self.I_data_instance_list[i], 16)
                                for i in range(0, len(self.I_data_instance_list), 2)]
                            #电流微分
                            self.I_dis_data_instance_list = self.data_instance[2 * 100000: 3 * 100000]
                            self.I_dis_data_instance = [
                                int(self.I_dis_data_instance_list[i + 1] + self.I_dis_data_instance_list[i], 16)
                                for i in range(0, len(self.I_dis_data_instance_list), 2)]
                            #位移数据
                            self.distance_instance_list = self.data_instance[3 * 100000: 3 * 100000 + 6000]
                            # print(self.distance_instance_list)
                            self.distance_instance = [
                                int(self.distance_instance_list[i] + self.distance_instance_list[i + 1], 16)
                                for i in range(0, len(self.distance_instance_list), 3)]

                            # 压力数据
                            self.force_instance_list = self.data_instance[3 * 100000+ 6000: 3 * 100000 + 2*6000]
                            # print(self.distance_instance_list)
                            self.force_instance = [
                                int(self.force_instance_list[i] + self.force_instance_list[i + 1], 16)
                                for i in range(0, len(self.force_instance_list), 3)]


                            self.point_instance_list = self.data_instance[
                                                       3 * 100000 + 2*6 * 1000: 3 * 100000 + 2*6 * 1000 + 1 * 2000]
                            self.point_instance = [
                                int(self.point_instance_list[i + 1] + self.point_instance_list[i], 16)
                                for i in range(0, len(self.point_instance_list), 2)]

                            #将接受数据缓冲区清空
                            self.data_instance = []
                            #调用绘图函数
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
        #将2个图像的显示曲线清空
        self.pw_instance.clear()
        self.pw_distance_ins.clear()
        #将瞬时值绘制到图中
        self.pw_instance.plot(range(len(self.I_data_instance)), self.I_data_instance, name='电流'
                              , pen=pg.mkPen(color='r')
                              )
        self.pw_instance.plot(range(len(self.U_data_instance)), self.U_data_instance, name='电压'
                              , pen=pg.mkPen(color='b')
                              )
        self.pw_instance.plot(range(len(self.I_dis_data_instance)), self.I_dis_data_instance, name='电流微分'
                              , pen=pg.mkPen(color='k')
                              )

        # self.pw_instance.plot(range(len(self.I_data_instance)), [ 65536 if i in self.point_instance else 1 for i in range(len(self.I_data_instance))], name='时机',
        #                       pen=pg.mkPen(color='g'))

        self.pw_distance_ins.plot(range(len(self.distance_instance)), self.np_move_avg(self.distance_instance, 70),
                                  name='位移'
                                  , pen=pg.mkPen(color='r')
                                  )
        ##压力瞬时值
        self.pw_distance_ins.plot(range(len(self.force_instance)), self.np_move_avg(self.force_instance, 70),
                                  name='压力'
                                  , pen=pg.mkPen(color='r')
                                  )

        #显示运行时间
        self.time4 = time.time()
        print(self.time4 - self.time3)
        # self.data_instance = []

    #关闭Tcp瞬时值采集服务器
    def Tcp_instance_model_close(self):
        #将数据缓冲区清空
        self.data_instance = []
        ##向串口发送信息，退出瞬时值模式
        serial_ = serial.Serial(self.com_num, 115200, timeout=0.5)
        serial_.write(b'\x01')
        time.sleep(0.1)
        serial_.close()

        try:
            for client_, address_ in self.client_socket_instance_list:
                client_.close()
            #关闭瞬时值服务器与子线程
            self.tcp_socket_instance.close()
            self.st.stop_thread(self.sever_th_instance)

        except:
            pass

        #修改相关的按钮状态
        self.Tcp_instance_open.setEnabled(True)
        self.Tcp_instance_close.setEnabled(False)
        self.tcp_character_open.setEnabled(True)
        self.window_close.setEnabled(True)
        # 将查询数据禁用
        self.tab2.setEnabled(True)
        self.tab3.setEnabled(True)
        self.tab5.setEnabled(True)
        # 启用串口
        self.serial_open.setEnabled(True)

    # 建立子线程进行
    def reset_net_fun(self):
        self.sever_reset_net = threading.Thread(target=self.reset_net_fun_theard)
        self.sever_reset_net.start()
        self.reset_net.setEnabled(False)

    # 定义复位函数
    def reset_net_fun_theard(self):
        # 连接串口并向下位机发送相关命令，恢复到之前的状态
        serial_ = serial.Serial(self.com_num, 115200, timeout=0.5)
        serial_.write(b'\x01')
        time.sleep(0.3)
        serial_.write(b'\x35')
        time.sleep(0.1)
        serial_.close()
        time.sleep(0.2)

        # 自动回到tcp特征值状态采集
        self.tcp_server_start()

        # 修改相关按钮状态
        self.Tcp_instance_open.setEnabled(False)
        self.Tcp_instance_close.setEnabled(False)
        self.tcp_character_open.setEnabled(False)
        self.tcp_character_close.setEnabled(True)

    # 定义关机信号的相关操作
    def shuntdown_signal_process(self):
        if self.shuntdown_signal.isChecked():
            pass
        else:
            # 向下位机发送相关命令，进入停机状态
            serial_ = serial.Serial(self.com_num, 115200, timeout=0.5)
            serial_.write(b'\x01')
            time.sleep(0.3)
            serial_.write(b'\x01')
            time.sleep(0.3)
            serial_.write(b'\x33')
            time.sleep(0.1)
            serial_.close()
            print('signal emit')

            # 更改相关的按钮状态
            self.reset_net.setEnabled(True)
            self.Tcp_instance_open.setEnabled(False)
            self.Tcp_instance_close.setEnabled(False)
            self.tcp_character_open.setEnabled(False)
            self.tcp_character_close.setEnabled(False)
        # 停止子线程
        self.st.stop_thread(self.serve_shuntdown)
 