"""
simple file server using socket
Ke Li, 2014/4/14
"""

import socket
import sys
import thread
import traceback
import os
import time
import json
import hashlib

HOST = '128.237.169.215'   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
DIR_PATH = '/home/masterk/18842/project/resource/'
BUFSIZE = 4096
#METADATA_FILE = DIR_PATH + 'metadata.txt'
DEBUG = True

def md5_for_file(pathfilename, block_size=2**20):
        """ to get md5 hash for a file, return string """
        md5 = hashlib.md5()
        with open(pathfilename, "rb") as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                md5.update(data)
        return md5.hexdigest()

def scanfiles(path):
    if not os.path.isdir(path):
        print 'err in scan file path'
        return None

    filesmatadata = {}
    metalist = []
    for root, dirs, files in os.walk(path):
        for name in files:
            fname = name.split('.')[0]
            fullname = os.path.join(root, name)
            hashcode = md5_for_file(fullname)
            fsize = os.path.getsize(fullname)
            filesmatadata[hashcode] = fname
            metalist.append((fname, hashcode, fsize))
            if DEBUG:
                print fname, hashcode, fsize
    return filesmatadata, metalist

# main program start here:
if DEBUG:
    print 'To use, please change HOST, PORT, DIR_PATH in code line 13-19'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if DEBUG:
    print 'Socket created'

#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
if DEBUG:
    print 'Socket bind complete'

#Start listening on socket
s.listen(10)
if DEBUG:
    print 'Socket now listening'

"""
# read files matadata for future response
filesmatadata = {}
with open(METADATA_FILE, 'r') as f:
    for line in f:
        fname, hashcode, fsize = line.split('\t')
        filesmatadata[fname] = hashcode + ' ' + fsize
        if DEBUG:
            print line,
"""
filesmatadata, metalist = scanfiles(DIR_PATH)

def sendfile(clientsocket, filename):
    # need to add file type
    fn = DIR_PATH + filename + ".mp4"
    # if requested file exists
    if os.path.exists(fn):
        if DEBUG:
            print "starting send file..."
        clientsocket.send("returnfile")
        time.sleep(1)
        with open(fn, 'rb') as f:
            while True:
                filedata = f.read(BUFSIZE)
                if not filedata:
                    break
                clientsocket.send(filedata)

            time.sleep(1)
            clientsocket.send("EOF")
            if DEBUG:
                print "finish send file."
    else:
        reply = 'File Not Found'
        clientsocket.send(reply)

def sendfilelist(clientsocket):
    clientsocket.send("returnfilelist")
    clientsocket.send(json.dumps(metalist))

#Function for handling connections. This will be used to create threads
def clientthread_handler(clientsocket):
    #infinite loop so that function do not terminate and thread do not end.
    try:
        while True:
            #Receiving from client
            data = clientsocket.recv(1024)
            if not data:
                print "Data from client is None, break connection"
                break
            
            if '\t' in data:
                msg = data.split('\t')
                msgtype = msg[0]
                hashcode = msg[1]
            else:
                msgtype = data

            if DEBUG:
                print "server received data : ", data
                print 'msgtype = ', msgtype
                print 'hashcode = ', hashcode

            # deal with request of metadata
            if msgtype == 'getmeta':
                try:
                    metadata = hashcode
                    if DEBUG:
                        print 'send meata data: ', metadata
                    clientsocket.send('returnmeta')
                    clientsocket.send(metadata)
                except KeyError:
                    clientsocket.send('File Metadata Not Found')

            # deal with request of file
            elif msgtype == 'getfile':
                fname = filesmatadata[hashcode]
                sendfile(clientsocket, fname)
            elif msgtype == 'getfilelist':
                sendfilelist(clientsocket)
            else:
                reply = 'Bad Request'
                clientsocket.send(reply)

    except socket.error:
        traceback.print_exc()
        print "Socket Error happened, exit thread"
        thread.exit()
    finally:
        #came out of loop
        clientsocket.close()

#now keep talking with the client
while True:
    #wait to accept a connection - blocking call
    clientsocket, addr = s.accept()
    if DEBUG:
        print 'Connected with ' + addr[0] + ':' + str(addr[1])

    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    thread.start_new_thread(clientthread_handler ,(clientsocket,))

s.close()
