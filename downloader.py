#!/usr/bin/env python
# coding:utf-8

import sys
import traceback
import json
import os
import time
import getopt
import urllib.request
import urllib.error
from urllib.parse import urlparse
# from urllib   import urlretrieve
import codecs
import socket

socket.setdefaulttimeout(300)

import gzip
import sys
import _thread
import time
from io import StringIO

sys.setrecursionlimit(1000000000)

cnt = []


def getContents(contents, n, savedir, baseurl, parent):
    # 下载content url里的东西
    u = ''
    prefix = ''
    if parent != None and parent != '' and ('/' in parent):
        prefix = parent[0: parent.rindex('/')] + '/'
    if 'content' in n:
        c = n['content']
        if 'url' in c:
            u = c['url']
            u = prefix + u
            contents.append(u)
        if 'uri' in c:
            u = c['uri']
            u = prefix + u
            contents.append(u)
        if len(u) != 0:
            if u.endswith('.json'):
                # 拉取json
                file = savedir + '/' + u

                dirname = os.path.dirname(file)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

                uu = urlparse(baseurl)
                url = baseurl + u + '?' + uu.query

                # 解析
                tile = None
                try:
                    print('解析', u, '数据')
                    tile = readContent(url)
                except Exception as e:
                    print(e)
                getContents(contents, tile['root'], savedir, baseurl, u)

    if 'children' in n:
        children = n['children']
        if children != None:
            for i in range(len(children)):
                c = children[i]
                getContents(contents, c, savedir, baseurl, parent)
    return


def gzdecode(data):
    # with patch_gzip_for_partial():
    compressedStream = StringIO(data)
    gziper = gzip.GzipFile(fileobj=compressedStream)
    data2 = gziper.read()

    # print len(data)
    return data2


def readContent(url):
    try:
        response = urllib.request.urlopen(url)
        html_bytes = response.read()
        return json.loads(html_bytes)
    except urllib.error.ContentTooShortError:
        print('Network conditions is not good.Reloading.')
        readContent(url)
    except socket.timeout:
        print('fetch ', url, ' exceedTime ')
        try:
            readContent(url)
        except:
            print('reload failed')
    except Exception as e:
        traceback.print_exc()
    return {}


def autoDownLoad(url, add):
    try:
        # a表示地址， b表示返回头
        a, b = urllib.request.urlretrieve(url, add)
        keyMap = dict(b)
        if 'content-encoding' in keyMap and keyMap['content-encoding'] == 'gzip':
            # print 'need2be decode'
            objectFile = open(add, 'rb+')  # 以读写模式打开
            data = objectFile.read()
            data = gzdecode(data)
            objectFile.seek(0, 0)
            objectFile.write(data)
            objectFile.close()

        return True

    except urllib.error.ContentTooShortError:
        print('Network conditions is not good.Reloading.')
        autoDownLoad(url, add)
    except socket.timeout:
        print('fetch ', url, ' exceedTime ')
        try:
            urllib.request.urlretrieve(url, add)
        except:
            print('reload failed')
    except Exception as e:
        traceback.print_exc()

    return False


def downloadByThreads(contents, start, end, savedir, baseurl, uu):
    for i in range(start, end):
        c = contents[i]

        file = savedir + '/' + c
        dirname = os.path.dirname(file)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        url = baseurl + c + '?' + uu.query
        if autoDownLoad(url, file):
            print(c + ' download success: ' + str(i + 1) + '/' + str(len(contents)) + '  start:' + str(
                start) + ';end:' + str(end))
        else:
            print(c + ' download failed: ' + str(i + 1) + '/' + str(len(contents)) + '  start:' + str(
                start) + ';end:' + str(end))

        global cnt
        cnt.append(1)
    return


def help():
    print("版本：V20201120.001")
    print("作者：IKangXu")
    print("使用说明：")
    print("     ", "options:")
    print("          ", "--url     / -u    需要下载的3dtiles数据，必填")
    print("          ", "--dir     / -d    输出目录，必填")
    print("          ", "--start   / -s    开始下载的位置下标，默认从0开始，一般是分段下载或者某一个下载失败的时候使用")
    print("          ", "--end     / -e    结束下载的位置下标，默认数据总长度，一般是分段下载或者某一个下载失败的时候使用")
    print("          ", "--threads / -t    启动多线程下载，指定线程数，默认为1")

    return


def pause():
    print('\n')
    print('================ 使用步骤 =================')
    print('step 1: win + r 输入cmd回车')
    print('step 2: cd进入到对应的dist文件夹中')
    print('step 3: .\downloader.exe --help')
    print('\n')
    input('please input any key to exit!')
    return


if __name__ == "__main__":

    baseurl = ''
    savedir = ''
    start = 0
    end = 0
    threads = 1

    startTime = time.time()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:d:s:e:t:", ["url=", "dir=", "start=", "end=", "threads=", "help"])
    except getopt.GetoptError:
        print('param error')
        pause()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', "--help"):
            help()
            sys.exit()
        elif opt in ("-u", "--url"):
            baseurl = arg
        elif opt in ("-d", "--dir"):
            savedir = arg
        elif opt in ("-s", "--start"):
            start = int(arg)
        elif opt in ("-e", "--end"):
            end = int(arg)
        elif opt in ("-t", "--threads"):
            threads = int(arg)

    if baseurl == '':
        print('please input url param or use --help to see how to use it')
        pause()
        sys.exit(2)
    if savedir == '':
        print('please input dir param or use --help to see how to use it')
        pause()
        sys.exit(2)

    if os.path.isfile(savedir):
        print('savedir can not be a file ', savedir)
        sys.exit(2)

    if not os.path.exists(savedir):
        os.makedirs(savedir)

    # print baseurl
    uu = urlparse(baseurl)
    # print uu
    # print uu.path,uu.query
    # 解析url

    tileseturl = uu.scheme + "://" + uu.netloc + uu.path
    if not tileseturl.endswith('tileset.json'):
        tileseturl += '/tileset.json'

    baseurl = tileseturl[0:tileseturl.find('tileset.json')]
    # print baseurl
    # sys.exit(2)

    tileseturl += '?' + uu.query

    print(tileseturl)

    opener = urllib.request.build_opener()
    opener.addheaders = [
        ('User-Agent',
         'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36'),
        ('Referer', 'http://cesium.marsgis.cn/')
    ]
    urllib.request.install_opener(opener)

    tilesetfile = savedir + '/tileset.json'
    if not autoDownLoad(tileseturl, tilesetfile):
        sys.exit(2)

    print('download tileset.json success')

    # 解析
    tileset = None
    try:
        f = codecs.open(tilesetfile, 'r', 'utf-8')
        s = f.read()
        f.close()

        tileset = json.loads(s)
    except Exception as e:
        print(e)

    contents = []
    getContents(contents, tileset['root'], savedir, baseurl, None)

    print("解析总耗时：", str(time.time() - startTime), 's')

    print(len(contents))
    if end == 0:
        end = len(contents)

    total = end;
    if start != 0:
        total = end - start

    remainder = total % threads
    pagesize = total // threads

    if pagesize == 0:
        threads = 1
        pagesize = total

    if threads == 1:
        remainder = 0

    for i in range(0, threads):
        if remainder == 0:
            _thread.start_new_thread(downloadByThreads,
                                     (contents, i * pagesize + start, (i + 1) * pagesize + start, savedir, baseurl, uu))
        if remainder > 0 and (i + 1) != threads:
            if (i + 1) <= remainder:
                _thread.start_new_thread(downloadByThreads,
                                         (contents, i * (pagesize + 1) + start, (i + 1) * (pagesize + 1) + start,
                                          savedir, baseurl, uu))
            if (i + 1) > remainder:
                _thread.start_new_thread(downloadByThreads, (
                    contents, (remainder * (pagesize + 1)) + ((i - remainder) * pagesize) + start,
                    (remainder * (pagesize + 1)) + (((i + 1) - remainder) * pagesize) + start, savedir, baseurl, uu))
        if remainder > 0 and (i + 1) == threads:
            _thread.start_new_thread(downloadByThreads, (
                contents, (remainder * (pagesize + 1)) + ((i - remainder) * pagesize) + start, end, savedir, baseurl,
                uu))

    flag = True
    while flag:
        if len(cnt) == (end - start):
            flag = False
            print("下载完成,总数据量：", str(len(contents) + 1), ",本次下载总量：" + str(end - start) + "总耗时：",
                  str(time.time() - startTime), 's')

    # 下载tilesetjson
