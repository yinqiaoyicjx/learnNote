#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import time
import select
import Queue
class STATE:

    def __init__(self):
        self.state = "accept"
        self.have_read = 0
        self.need_read = 5
        self.have_write = 0
        self.need_write = 0

        self.buff_read = ""
        self.buff_write = ""
        self.sock_obj = ""

    def printState(self):
        print('\n - current state of fd: %d' % self.sock_obj.fileno())
        print(" - - state: %s" % self.state)
        print(" - - have_read: %s" % self.have_read)
        print(" - - need_read: %s" % self.need_read)
        print(" - - have_write: %s" % self.have_write)
        print(" - - need_write: %s" % self.need_write)
        print(" - - buff_write: %s" % self.buff_write)
        print(" - - buff_read:  %s" % self.buff_read)
        print(" - - sock_obj:   %s" % self.sock_obj)

class nbNetBase:
    def __init__(self, addr, port, logic):
        print('\n__init__: start!')

        self.conn_state = {}

        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

        self.listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.listen_sock.bind((addr, port))

        self.listen_sock.listen(5)  # backlog

        self.setFd(self.listen_sock)

        self.logic = logic

    def setFd(self, sock):

        print ("\n -- setFd start")
        tmp_state = STATE()
        tmp_state.sock_obj = sock
        self.conn_state[sock.fileno()] = tmp_state
        self.conn_state[sock.fileno()].printState()
        print "\n -- setFd end."

    def accept(self, sock):
        print "\n accept start"
        #sock_state = self.conn_state[fd]
        #sock = sock_state.sock_obj
        conn, addr = sock.accept()
        conn.setblocking(0)
        self.setFd(conn)
        self.conn_state[conn.fileno()].state = "read"
        print "\n--accept end "
        return conn

    def close(self, fd):
        try:
            sock = self.conn_state[fd].sock_obj
            self.inputs.remove(fd)
            self.outputs.remove(fd)
            sock.close()
        except:
            print "close fd: %s abnormal" % fd
        finally:
            self.conn_state.pop(fd)

    def read(self, fd):
        try:
            sock_state = self.conn_state[fd]
            conn = sock_state.sock_obj
            if sock_state.need_read <= 0:
                raise socket.error

            one_read = conn.recv(sock_state.need_read)
            print("\tread func fd: %d, one_read: %s, need_read: %d" %
                     (fd, one_read, sock_state.need_read))
            if len(one_read) == 0:
                raise socket.error

            sock_state.buff_read += one_read
            sock_state.have_read += len(one_read)
            sock_state.need_read -= len(one_read)
            #sock_state.printState()

            if sock_state.have_read == 5:
                header_said_need_read = int(sock_state.buff_read)
                if header_said_need_read <= 0:
                    raise socket.error
                sock_state.need_read += header_said_need_read
                sock_state.buff_read = ''

                #sock_state.printState()
                return "readcontent"
            elif sock_state.need_read == 0:
                self.inputs.remove(fd)
                print self.logic(sock_state.buff_read)
                return "process"
            else:
                return "readmore"
        except (socket.error, ValueError), msg:
            try:
                if msg.errno == 11:
                    print("11 " + msg)
                    return "retry"
            except:
                pass
            return "closing"

    def write(self, fd):
        sock_state = self.conn_state[fd]
        sock_state.need_write = 10
        sock_state.buff_write = "00005hello"
        conn = sock_state.sock_obj
        last_have_send = sock_state.have_write
        try:
            have_send = conn.send(sock_state.buff_write[last_have_send:])
            sock_state.have_write += have_send
            sock_state.need_write -= have_send
            if sock_state.need_write == 0 and sock_state.have_write != 0:
                sock_state.printState()
                print('\n write data completed!')
                self.outputs.remove(fd)
                return "writecomplete"
            else:
                return "writemore"
        except socket.error, msg:
            self.close(fd)
    def run(self):
        """
        这个函数是装个状态机的主循环所在
        """
        self.inputs = [self.listen_sock]
        self.outputs = []
        message_queues = {}
        timeout = 20
        while True:
            print u"等待活动连接......"
            readable , writable , exceptional = select.select(self.inputs, self.outputs, self.inputs, timeout)

            if not (readable or writable or exceptional) :
                print u"select超时无活动连接，重新select...... "
                continue
            for s in readable :
                if s is self.listen_sock:
                    conn=self.accept(self.listen_sock)
                    self.inputs.append(conn.fileno())
                    if conn.fileno() not in self.outputs:
                        self.outputs.append(conn.fileno())
                else:
                    a = self.read(s)

            for s in writable:
                print self.write(s)

            for s in exceptional:
                print self.close(s)
    def state_machine(self, fd):
        """
        这里的逻辑十分的简单：“按照不同fd的state，调用不同的函数即可”
        具体的对应表见nbNet的__init__()
        """
        sock_state = self.conn_state[fd]
        self.sm[sock_state.state](fd)

if __name__ == '__main__':
    # 这个是我们演示用的“业务逻辑”，做的事情就是将请求的数据反转
    # 例如：
    #   收到：0000000005HELLO
    #   回应：0000000005OLLEH
    def logic(d_in):
        return(d_in[::-1])

    # 监听在0.0.0.0:9076
    reverseD = nbNetBase('0.0.0.0', 9090, logic)

    # 状态机开始运行，除非被kill，否则永不退出
    reverseD.run()




