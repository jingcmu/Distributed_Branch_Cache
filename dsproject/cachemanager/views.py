# Create your views here.
import os
import linecache
from sys import argv

class CacheManager:
    def __init__( self, cachepath, capacity = 4*(2**30), debug=False ): # default capacity is 4G
        self.cachepath = cachepath
        self.logfile = cachepath + 'logfile'
        self.capacity = capacity
        self.lines = linecache.getlines(self.logfile) # lines in logfile
        self.size, self.filecount = self.getSize()
        self.LRU = self.initLRU()

    def newlog( self, hashcode, filesize):
        self.LRU.insert(0, hashcode)
        self.lines.append( hashcode + " " + filesize + "\n")
        self.updatelogfile() # update the logfile

    def getSize(self):
        size = 0
        for i in xrange(len(self.lines)):
            strlist = self.lines[i].split(' ')
            size += long(strlist[-1])
        return size, len(self.lines)

    def initLRU(self):
        LRU = []
        for i in xrange(len(self.lines)):
            strlist = self.lines[i].split(' ')
            LRU.append(strlist[0])
        return LRU

    def updateCache(self):
        if self.size > self.capacity * 0.9:
            # get the last file's hash code in the LRU list
            hashcode = self.LRU[self.filecount-1]
            # get the last file's name
            filename = self.cachepath + hashcode
            # remove the last file in the LRU list
            if os.path.exists(filename):
                os.remove(filename)
            else:
                print filename + " does not exist!"
            # remove the last record in LRU list
            self.LRU.pop()
            self.filecount -= 1
            self.writeLog()

    def updatelogfile(self):
        # update the logfile
        with open(self.logfile, "wt") as f:
            for i in xrange(len(self.LRU)):
                for j in xrange(len(self.lines)):
                    if self.lines[j].find(self.LRU[i]) != -1:
                        f.write(self.lines[j])
            f.close()

    def LRUmaintain(self, hashcode):
        for i in xrange(len(self.LRU)):
            if self.LRU[i] == hashcode:
                self.LRU.remove(hashcode)
                self.LRU.insert(0, hashcode)