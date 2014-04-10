'''
Created on Apr 9, 2014

@author: Jacky
'''
from sys import argv
import os

def split(pathfilename, chunksize):
	#split a file into many small files with chunksize bytes
    statinfo = os.stat(pathfilename)
    path, filename = os.path.split(pathfilename)
    tmppath = path + '\\tmp'
    if not os.path.exists(tmppath):
        os.mkdir(tmppath)
    print "file size: %d(mb)" % (statinfo.st_size/(1024*1024))
    with open(pathfilename, "rb") as f:
        index = 0
        while True:
            chunk = f.read(chunksize)
            if(chunk):
                fn = "%s\%s.part.%d" % (tmppath, filename, index)
                index = index + 1
                print "creating", fn
                with open(fn, "wb") as fw:
                    fw.write(chunk)
            else:
                break

def test():
    pathfilename = argv[1]
    filesize = os.path.getsize(pathfilename)
    chunksize =  filesize / 20
    print "file name:", pathfilename
    print "chunk size: %d(mb)" % (chunksize/(1024 * 1024))
    split(pathfilename, chunksize)

test()