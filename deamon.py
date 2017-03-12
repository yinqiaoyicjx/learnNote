#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, time, atexit
from signal import SIGTERM

class Deamon:


    def __init__(self,pidfile='nbMon.pid', stdin='/dev/null', stdout='nbMon.log', stderr='nbMon.log'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile


    def deamonize(self):
        """
        双重fork
        """
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit()#退出第一个爷爷进程
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" %
                             (e.errno, e.strerror))
            sys.exit(1)
        # 改变当前工作目录
        os.chdir("/")
        # 设置sid，成为session Leader
        os.setsid()
        # 重设umask
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit()#退出第一个爷爷进程
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" %
                             (e.errno, e.strerror))
            sys.exit(1)

        # 重定向0、1、2三个fd（依次为标准输入、标准输出、错误输出）
        sys.stdout.flush()#刷新缓存区
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())#fd2指向的文件就变成了fd1指向的文件
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        #写pid文件
        atexit.register(self.delpid)#注册退出时的回调函数
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write("%s\n" % pid)


    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # 开始守护进程
        self.daemonize()
        self.run()


    def stop(self):
        """
        停止守护进程
        """
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return

        # 开始尝试kill掉守护进程
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        """
        子类重写run函数
        例子：一个非常蹩脚的HTTP Server :-P

from daemon import Daemon
import socket
import time

html = "HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nConnection: close\r\nContent-Length: "
html404 = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nContent-Length: 13\r\n\r\n<h1>404 </h1>"

class agentD(Daemon):
  def run(self):
    listen_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    listen_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_fd.bind(("0.0.0.0", 9000))
    listen_fd.listen(10)
    while True:
      conn, addr = listen_fd.accept()
      print "coming", conn, addr
      read_data = conn.recv(10000)
      #print read_data
      try:
        pic_name = read_data.split(" ")[1][1:]
        print pic_name
        with file(pic_name) as f:
          pic_content = f.read()
          length = len(pic_content)
          html_resp = html
          html_resp += "%d\r\n\r\n" % (length)
          print html_resp
          html_resp += pic_content
      except:
        print "404 occur"
        html_resp = html404

      while len(html_resp) > 0:
        sent_cnt = conn.send(html_resp)
        print "sent:", sent_cnt
        html_resp = html_resp[sent_cnt:]
      conn.close()

if __name__ == "__main__":
  agentd = agentD(pidfile="agentd.pid", stdout="agentd.log", stderr="agentd.log")
  agentd.run()
        """
        pass





