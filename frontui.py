# !/usr/bin/env/python

import sys
import threading

from Tkinter import *
from random import *
from cachepeer import *


class DBCGui(Frame):
    def __init__(self, firstpeer, hops=2, maxpeers=5, serverport=5678, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.creatWidgets()
        self.master.title("Distribute Branch Cache GUI %d" % serverport)
        self.cachepeer = CachePeer( maxpeers, serverport )
        self.bind("Destory", self.__onDestory)

        host, port = firstpeer.split(":")
        self.cachepeer.buildpeers( host, int(port), hops=hops )
        self.updatePeerList()

        t = threading.Thread( target=self.cachepeer.mainloop, args=[])
        t.start()

        self.cachepeer.startstabilizer( self.cachepeer.checklivepeers, 3)
        self.after(3000, self.onTimer)

    def onTimer( self ):
        self.onRefresh()
        self.after(3000, self.onTimer)


    def __onDestory( self, event ):
        self.cachepeer.shutdonw = True

    def updatePeerList( self ):
        if self.peerList.size() > 0:
            self.peerList.delete(0, self.peerList.size()-1)
        for pid in self.cachepeer.getpeerids():
            self.peerList.insert(END, pid)
    
    def updateFileList( self ):
        if self.fileList.size() > 0:
            self.fileList.delete(0, self.fileList.size()-1)
        for filename in self.cachepeer.cachefile:
            pid = self.cachepeer.cachefile[filename]
            if not pid:
                pid = '(local)'
                self.fileList.insert( END, "%s:%s" % (filename, pid))
            else:
                for p in pid:
                    self.fileList.insert( END, "%s:%s" % (filename, p))
    
    def creatWidgets( self ):

        fileFrame = Frame(self)
        peerFrame = Frame(self)

        rebuildFrame = Frame(self)
        searchFrame = Frame(self)
        addfileFrame = Frame(self)
        pbFrame = Frame(self)

        fileFrame.grid(row=0, column=0, sticky=N+S)
        peerFrame.grid(row=0, column=1, sticky=N+S)
        pbFrame.grid(row=2, column=1)
        addfileFrame.grid(row=3)
        searchFrame.grid(row=4)
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
        file  = self.addfileEntry.get()
        if file.lstrip().rstrip():
            filename = file.lstrip().rstrip()
            self.cachepeer.addfile(filename)
        self.addfileEntry.delete(0, len(file))
        self.updateFileList()

    def onDelete( self ):
        selections = self.fileList.curselection()
        if len(selections) == 1:
            selection = self.fileList.get(selections[0]).split(':')
            if len(selection) == 2:
                filename = selection[0]
                del self.cachepeer.cachefile[filename]
                for pid in self.cachepeer.getpeerids(): 
                    self.cachepeer.sendtopeer( pid, DELETE, "%s %s" % (filename, self.cachepeer.myid) )

    def onSearch( self ):
        key = self.searchEntry.get()
        self.searchEntry.delete(0, len(key))

        for pid in self.cachepeer.getpeerids():
            self.cachepeer.sendtopeer(pid, QUERY, "%s %s 4" % (self.cachepeer.myid, key))

    def onFetch( self ):
        selections = self.fileList.curselection()
        print len(selections)
        if len(selections) == 1:
            selection = self.fileList.get(selections[0]).split(':')
            if len(selection) > 2:
                filename, host, port = selection
                print selection
                resp = self.cachepeer.connectandsend( host, port, FILEGET, filename)
                if len(resp) and resp[0][0] == REPLY:
                    fd = file(filename, 'w')
                    fd.write(resp[0][1])
                    fd.close()
                    self.cachepeer.cachefile[filename] = None 

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
        print "Syntax: %s server-port max-peers peer-ip:port" % sys.argv[0]
        sys.exit(-1)

    serverport = int(sys.argv[1])
    maxpeers = sys.argv[2]
    peerid = sys.argv[3]
    app = DBCGui( firstpeer=peerid, maxpeers=maxpeers, serverport=serverport )
    app.mainloop()


if __name__=='__main__':
    main()

