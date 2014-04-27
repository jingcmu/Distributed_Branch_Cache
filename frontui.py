# !/usr/bin/env/python

import sys
import time
import threading
from filemanager import *
from Tkinter import *
from random import *
from cachepeer import *

CHUNKSIZE = 512

class DBCGui(Frame):
    def __init__(self, firstpeer, hops=2, maxpeers=5, serverport=5678, master=None, cachepath = './'):
        Frame.__init__(self, master)
        self.grid()
        self.creatWidgets()
        self.master.title("Distribute Branch Cache GUI %d" % serverport)
        self.cachepeer = CachePeer( maxpeers, serverport, cachepath )
        self.bind("<Destroy>", self.__onDestroy)

        host, port = firstpeer.split(":")
        self.cachepeer.buildpeers( host, int(port), hops=hops )
        self.updatePeerList()

        logfile = cachepath + '/logfile'
        self.cachepeer.addfile( logfile )

        # start cachepeer thread
        t = threading.Thread( target=self.cachepeer.mainloop, args=[])
        t.start()

        self.cachepeer.startstabilizer( self.cachepeer.checklivepeers, 3)
        self.after(3000, self.onTimer)

    def creatWidgets( self ):

        fileFrame = Frame(self)
        peerFrame = Frame(self)

        rebuildFrame = Frame(self)
        searchFrame = Frame(self)
        addfileFrame = Frame(self)
        fetchpartFrame = Frame(self)
        pbFrame = Frame(self)

        fileFrame.grid(row=0, column=0, sticky=N+S)
        peerFrame.grid(row=0, column=1, sticky=N+S)
        pbFrame.grid(row=2, column=1)
        addfileFrame.grid(row=3)
        searchFrame.grid(row=4)
        fetchpartFrame.grid(row=5)
        rebuildFrame.grid(row=3, column=1)

        Label( fileFrame, text='Available Files' ).grid()
        Label( peerFrame, text='Peer List' ).grid()

        fileListFrame = Frame(fileFrame)
        fileListFrame.grid(row=1, column=0)
        fileScroll = Scrollbar( fileListFrame, orient=VERTICAL )
        fileScroll.grid(row=0, column=1, sticky=N+S)

        self.fileList = Listbox(fileListFrame, selectmode='multiple', height=5,
                    yscrollcommand=fileScroll.set)
        #self.fileList.insert( END, 'a', 'b', 'c', 'd', 'e', 'f', 'g' )
        self.fileList.grid(row=0, column=0, sticky=N+S)
        fileScroll["command"] = self.fileList.yview

        self.fetchButton = Button( fileFrame, text='Fetch',
                       command=self.onFetch)
        self.fetchButton.grid()

        self.fetchpartEntry = Entry(fetchpartFrame, width=25)
        self.fetchpartButton = Button( fetchpartFrame, text='FetchPart',
                       command=self.onFetchPart)
        self.fetchpartEntry.grid(row=0, column=0)
        self.fetchpartButton.grid(row=0, column=1)


        self.deleteButton = Button( fileFrame, text='Delete',
                       command=self.onDelete)
        self.deleteButton.grid()

        self.addfileEntry = Entry(addfileFrame, width=25)
        self.addfileButton = Button(addfileFrame, text='Add',
                       command=self.onAdd)
        self.addfileEntry.grid(row=0, column=0)
        self.addfileButton.grid(row=0, column=1)

        self.searchEntry = Entry(searchFrame, width=25)
        self.searchButton = Button(searchFrame, text='Search',
                       command=self.onSearch)
        self.searchEntry.grid(row=0, column=0)
        self.searchButton.grid(row=0, column=1)

        peerListFrame = Frame(peerFrame)
        peerListFrame.grid(row=1, column=0)
        peerScroll = Scrollbar( peerListFrame, orient=VERTICAL )
        peerScroll.grid(row=0, column=1, sticky=N+S)

        self.peerList = Listbox(peerListFrame, selectmode='multiple', height=5,
                    yscrollcommand=peerScroll.set)
        #self.peerList.insert( END, '1', '2', '3', '4', '5', '6' )
        self.peerList.grid(row=0, column=0, sticky=N+S)
        peerScroll["command"] = self.peerList.yview

        self.removeButton = Button( pbFrame, text='Remove',
                              command=self.onRemove )
        self.refreshButton = Button( pbFrame, text = 'Refresh',
                        command=self.onRefresh )

        self.rebuildEntry = Entry(rebuildFrame, width=25)
        self.rebuildButton = Button( rebuildFrame, text = 'Rebuild',
                        command=self.onRebuild )
        self.removeButton.grid(row=0, column=0)
        self.refreshButton.grid(row=0, column=1)
        self.rebuildEntry.grid(row=0, column=0)
        self.rebuildButton.grid(row=0, column=1)


    def onAdd( self ):
        # add one file to FileList
        file  = self.addfileEntry.get()
        if file.lstrip().rstrip():
            filename = file.lstrip().rstrip()
            self.cachepeer.addfile(filename)
        self.addfileEntry.delete(0, len(file))
        self.updateFileList()

    def onDelete( self ):
        # delete one file from filelist
        selections = self.fileList.curselection()
        if len(selections) == 1:
            selection = self.fileList.get(selections[0]).split(':')
            if len(selection) == 2:
                hashcode = selection[0]
                self.cachepeer.removefile(hashcode)
                for pid in self.cachepeer.getpeerids():
                    self.cachepeer.sendtopeer( pid, DELETE, "%s %s" % (hashcode, self.cachepeer.myid) )


    def onTimer( self ):
        self.onRefresh()
        self.after(3000, self.onTimer)

    def __onDestroy( self, event ):
        self.cachepeer.shutdown = True

    def updatePeerList( self ):
        """ first remove all peers in the list, then insert peers one by one """
        if self.peerList.size() > 0:
            self.peerList.delete(0, self.peerList.size()-1)
        for pid in self.cachepeer.getpeerids():
            # print pid
            self.peerList.insert(END, pid)

    def updateFileList( self ):
        if self.fileList.size() > 0:
            self.fileList.delete(0, self.fileList.size()-1)
        for hashcode in self.cachepeer.cachefile:
            pid = self.cachepeer.cachefile[hashcode][0]
            filesize = self.cachepeer.cachefile[hashcode][1]
            if not pid:
                pid = '(local)'
                self.fileList.insert( END, "%s:%s:%s" % (hashcode, pid, filesize))
            else:
                for p in pid:
                    self.fileList.insert( END, "%s:%s:%s" % (hashcode, p, filesize))
    '''
    def onSearch( self ):
        # search on peers and auto fetch file or parts
        hashcode = self.searchEntry.get()
        self.searchEntry.delete(0, len(hashcode))

        for pid in self.cachepeer.getpeerids():
            self.cachepeer.sendtopeer(pid, QUERY, "%s %s 4" % (self.cachepeer.myid, hashcode))

        time.sleep(10)
        pid = self.cachepeer.cachefile[filename][0]
        filesize = self.cachepeer.cachefile[filename][1]
        #self.autoFetch(filename, pid[0], filesize) #test fetch whole file

        # arrange chunks to peers
        pid_num = len(pid)
        chunk_num = int(filesize)/(CHUNKSIZE*1024) + 1
        chunk_per_peer = chunk_num/pid_num

        for i in xrange(pid_num-1):
            print "pid = ", pid[i]
            self.autoFetchParts(pid[i], hashcode, i*chunk_per_peer, (i+1)*chunk_per_peer)
        # last peer in charge of the remaining chunks
        self.autoFetchParts(pid[pid_num-1], hashcode, (pid_num-1)*chunk_per_peer, chunk_num)
        # combine the temporary files
        filemanager = FileManager(int(filesize), CHUNKSIZE, os.getcwd() + '/cache_path/' + hashcode)
        filemanager.combineFile()
    '''

    def onSearch( self ):
        # search on peers and auto fetch file or parts
        hashcode = self.searchEntry.get()
        self.searchEntry.delete(0, len(hashcode))

        for pid in self.cachepeer.getpeerids():
            self.cachepeer.sendtopeer(pid, QUERY, "%s %s 4" % (self.cachepeer.myid, hashcode))

        time.sleep(1)
        pid = self.cachepeer.cachefile[hashcode][0]
        filesize = self.cachepeer.cachefile[hashcode][1]
        #self.autoFetch(hashcode, pid[0], filesize) #test fetch whole file

        # arrange chunks to peers
        pid_num = len(pid)
        chunk_num = int(filesize)/(CHUNKSIZE*1024) + 1
        chunk_per_peer = chunk_num/pid_num

        stack = []
        for i in xrange(chunk_num):
            stack.append(chunk_num - i - 1)

        while len(stack) != 0 and len(pid) != 0:
            available_pids = self.cachepeer.getpeerids()
            pid = list(set(pid) & set(available_pids)) # remove non-available peer id
            for i in xrange(len(pid)): # fetch a part from each available peer id
                host, port = pid[i].split(':')
                print "fetch part", stack[len(stack)-1], "from", pid[i]
                code = self.fetchPart( hashcode, host, port, stack.pop(), chunk_num )
                if code != -1:
                    stack.append(code)
                if len(stack) == 0:
                    break

        # combine the temporary files
        filemanager = FileManager(int(filesize), CHUNKSIZE, os.getcwd() + '/cache_path/' + hashcode)
        filemanager.combineFile()
        self.cachepeer.cachemanager.newlog(hashcode, filesize)

    def autoFetch( self, hashcode, pid, filesize ):
        #auto fetch from available peers
        try:
            if pid != None:
                host, port = pid.split(':')
                self.fetch(hashcode, host, port, filesize)
        except:
            print "no available peer"

    def fetch( self, hashcode, host, port, filesize ):
        # fetch whole file from host:port
        resp = self.cachepeer.connectandsend( host, port, FILEGET, hashcode)
        for i in xrange(len(resp)):
            if resp[i][0] == REPLY:
                tmppath = os.getcwd() + '/cache_path/tmpfetch'
                if not os.path.exists(tmppath):
                    os.mkdir(tmppath)
                partfilename = tmppath+ '/' + hashcode + ".part." + str(i)
                fd = file(partfilename, 'w')
                fd.write(resp[i][1])
                print len(resp[i][1])
                fd.close()

        # combine the temporary files
        filemanager = FileManager(int(filesize), CHUNKSIZE, os.getcwd() + '/cache_path/' + hashcode)
        filemanager.combineFile()

    def onFetch( self ):
        # fetch file
        selections = self.fileList.curselection()
        if len(selections) == 1:
            selection = self.fileList.get(selections[0]).split(':')
            if len(selection) > 2:
                hashcode, host, port, filesize = selection
                self.fetch(hashcode, host, port, filesize)

    def fetchPart( self, hashcode, host, port, part, chunk_num ):
        # fetch part from host:port
        resp = self.cachepeer.connectandsend( host, port, FPART, "%s %d" % (hashcode, int(part)) )
        if len(resp) and resp[0][0]==REPLY and (len(resp[0][1]) == CHUNKSIZE*1024 or part == chunk_num - 1 ):
            tmppath = os.getcwd() + '/cache_path/tmpfetch'
            if not os.path.exists(tmppath):
                os.mkdir(tmppath)
            partfilename = tmppath + '/' + hashcode + ".part." + str(part)
            fd = file(partfilename, 'w')
            fd.write(resp[0][1])
            fd.close()
            return -1
        else:
            return part

    def onFetchPart( self ):
        part = self.fetchpartEntry.get()
        self.fetchpartEntry.delete(0, len(part))

        selections = self.fileList.curselection()
        if len(selections) == 1:
            selection = self.fileList.get(selections[0]).split(':')
            if len(selection) > 2:
                hashcode, host, port, _ = selection
                self.fetchPart(hashcode, host, port, part)

    def onRemove( self ):
        selections = self.peerList.curselection()
        if len(selections) == 1:
            peerid = self.peerList.get(selections[0])
            self.cachepeer.sendtopeer( peerid, QUIT, self.cachepeer.myid )
            self.cachepeer.removepeer (peerid)

    def onRefresh( self ):
        self.updatePeerList()
        self.updateFileList()

    def onRebuild(self):
        if not self.cachepeer.maxpeersreached():
            peerid = self.rebuildEntry.get()
            self.rebuildEntry.delete( 0, len(peerid) )
            peerid = peerid.lstrip().rstrip()
            try:
                host,port = peerid.split(':')
                self.cachepeer.buildpeers( host, port, hops=3 )
            except:
                if self.cachepeer.debug:
                    traceback.print_exc()

def main():
    if len(sys.argv) < 4:
        print "Syntax: %s server-port max-peers peer-ip:port cache-path" % sys.argv[0]
        sys.exit(-1)
    serverport = int(sys.argv[1])
    maxpeers = sys.argv[2]
    peerid = sys.argv[3]
    if len(sys.argv) > 4:
        cache_path = sys.argv[4]
    app = DBCGui( firstpeer=peerid, maxpeers=maxpeers, serverport=serverport, cachepath = cache_path)
    app.mainloop()


if __name__=='__main__':
    main()

