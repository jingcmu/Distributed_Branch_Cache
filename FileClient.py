"""
simple file client using socket
just for test file server
Ke Li, 2014/4/14
"""

import socket

HOST = '128.237.252.161'   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
DIR_PATH = '/home/masterk/18842/project/myclient/'
BUFSIZE = 4096
DEBUG = True

# main program start here:
if DEBUG:
    print 'To use, please change HOST, PORT, DIR_PATH in code line 7-11'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a socket object
if DEBUG:
    print 'Client Socket created'

s.connect((HOST, PORT))
if DEBUG:
    print 'Client connected to HOST'

def recvfile(filename):
    fname = DIR_PATH + filename
    f = open(fname, 'wb')
    while True:
        filedata = s.recv(BUFSIZE)
        if filedata == 'EOF':
            print "recv file success!"
            break
        f.write(filedata)
    f.close()

if DEBUG:
    print 'Usage: input <message type><TAB><file name>'
    print 'message type: getmeta OR getfile'
    print 'file name: just the file name you want, not the path'

while True:
    msg = raw_input("Message>> ")
    if msg == "exit":
        break

    msgtype, fname = msg.split('\t')
    if DEBUG:
        print 'Your request type is', msgtype
        print 'Your requestd file name is', fname
    s.send(msg)
    recdata = s.recv(1024)

    if not recdata:
        break

    if recdata == 'returnmeta':
        metadata = s.recv(1024)
        print "metadata = ", metadata
    elif recdata == 'returnfile':
        recvfile(fname)
    elif recdata == 'returnfilelist':
        filelist = s.recv(1024)
        print "file list = ", filelist
    else:
        print 'Bad recdata:', recdata

s.close()
