#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from PIL import Image
from io import BytesIO
import threading

"""多线程多链接下载
使用requests
"""
class downloader:

    def __init__(self, url="", num=4):
        self.url = url
        self.num = num
        self.filename = 'pc.jpg'

        r = requests.head(self.url)
        self.length = int(r.headers['Content-Length'])
        print type('total is %s' % (self.length))

    def get_range(self):
        ranges = []
        interval = self.length / self.num
        for i in range(self.num):
            if i != self.num-1:
                ranges.append((i * interval,(i+1)*interval))
            else:
                ranges.append((i*interval,''))
        print ranges
        return ranges

    def run(self):
        self.fd = open(self.filename, 'wb')
        thread_list = []
        for ran in self.get_range():
            start, end = ran
            thread = threading.Thread(target=self.download, args=(start,end))
            thread.start()
            thread_list.append(thread)
        for i in thread_list:
            i.join()
        print 'download %s load success'%(self.filename)
        self.fd.close()

    def download(self,start,end):
        res = requests.get(self.url,headers={'Range':'Bytes=%s-%s' % (start,end),'Accept-Encoding':'*'})
        self.fd.seek(start)
        self.fd.write(res.content)
        print "success %s-%s" % (start, end)


if __name__=='__main__':
    down = downloader('http://pic2.zhimg.com/b6e56100e8a4d25c65dbcfa79347d7fd_b.jpg')
    down.run()
