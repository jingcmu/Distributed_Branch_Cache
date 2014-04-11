#! /usr/bin/python

from branchpeer import *
# support query type list as follow
LIST = "LIST"       # list all available peer nodes
JOIN = "JOIN"       # join the p2p network
QUERY = "QUERY"     # query file message
RESP  = "RESP"      # response message
FILEGET = "FILEGET" # fetch a file 
QUIT    = "QUIT"    # quit the p2p network
NAME    = "NAME"    # query a peer's id

ERROR  = "ERROR"    
REPLY  = "REPLY"

class CachePeer( BranchPeer ):

    def __init__(self, maxpeers, serverport):
        BranchPeer.__init__(self, maxpeers, serverport)
        self.cachefile = {} # local cache file  mapping: file-name --> peer id
        self.addrouter(self.__router)
        handlers  =  {
            LIST : self.__list_handler,
            JOIN : self.__join_handler,
            QUERY: self.__query_handler,
            RESP : self.__resp_handler,
            FILEGET: self.__fileget_handler,
            QUIT:   self.__quit_handler,
            NAME:   self.__name_handler,
        }
        for msgtype in handlers:
            self.addhandler(msgtype, handlers[msgtype])

    def __debug( self, msg ):
        if self.__debug:
            debughelper(msg)

    def __router(self, peerid):
        if peerid not in self.getpeerids():
            return (None, None, None)
        else:
            routers = [peerid]
            routers.extend(self.peers[peerid])
            return routers

    def __list_handler(self, peerconn, data):
        """handle list peers request, LIST, data is not needed here """
        self.peerlock.acquire()
        try:
            peerconn.senddata(REPLY, "%d" % self.numberofpeers())
            for pid in self.getpeerids():
                host, port = self.getpeer( pid )
                peerconn.senddata( REPLY, '%s %s %d' % (pid, host, port))
        finally:
            self.peerlock.release()

    def __join_handler(self, peerconn, data):
        """handle join network message, JOIN, data format : "peerid  host  port" """
        self.peerlock.acquire()
        try:
            try:
                pid, host, port = data.split()
                if self.maxpeersreached():
                    peerconn.senddata(ERROR, "Join: too many peers")
                    return

                if pid not in self.getpeerids() and pid != self.myid:
                    self.addpeer(pid, host, port)
                    peerconn.senddata(REPLY, 'Join: peer added: %s' % pid)
                else:
                    peerconn.senddata(ERROR, 'Join: peer %s has already added' % pid)
            except:
                peerconn.senddata( ERROR, 'Join: invalid request arguments')
        finally:
            self.peerlock.release()

    def __query_handler(self, peerconn, data):
        """handle query message, QUERY, data format : "peer-id  keyword  ttl" """
        try:
            pid, key, ttl = data.split()
            peerconn.senddata( REPLY, 'Query Ack: %s' % key)
        except:
            peerconn.senddata( ERROR, 'Query : invalid arguments')

        t = threading.Thread(target=self.__processquery, args=[peerid, key, int(ttl)])
        t.start()


    def __processquery(self, peerid, key, ttl):
        """process the query message in this function, replying with either a RESP if file found, 
        or propagating msg to its all peers """
        for filename in self.cachefile.keys():
            if key in filename:
                filepeerid = self.cachefile[ filename ]
                if not filepeerid:
                    filepeerid = self.myid
                host, port = peerid.split(':')
                self.connectandsend(host, int(port), RESP, 
                    '%s %s' % (filename, filepeerid),
                    pid = peerid)
                return
        # if key is not found in the local cache file
        if ttl > 0:
            msgdata = "%s %s %d" % (peerid, key, ttl-1)
            for nextpid in self.getpeerids():
                self.sendtopeer(nextpid, QUERY, msgdata)



    def __resp_handler(self, peerconn, data):
        """handle response message, RESP, data format should be "file-name, peer-id" """   
        try:
            filename, filepeerid = data.split()
            if filename in self.cachefile:
                pass
            else:
                self.cachefile[filename] = filepeerid
        except:
            traceback.print_exc()
    def __fileget_handler(self, peerconn, data):
        """handle file get message, FILEGET data format should  a string "file-name" """
        filename = data
        if filename not in self.cachefile:
            peerconn.senddata( ERROR, 'File not found')
            return
        try:
            fd = file(filename, 'r')
            filedata = ''
            while True:
                data = fd.read(1024)
                if not len(data):
                    break;
                filedata += data
            fd.close()
        except:
            peerconn.senddata( ERROR, 'Error reading file')
            return

        peerconn.senddata(REPLY, filedata)
    def __quit_handler(self, peerconn, data):
        """handle peer quit message, data is not needed """
        self.peerlock.acquire()
        try:
            peerid = data.lstrip().rstrip()
            if peerid in self.getpeerids():
                msg = 'Quit: peer remove: %s' % peerid
                peerconn.senddata(REPLY, msg)
                self.removepeer(peerid)
            else:
                msg = 'Quit: peer not found: %s' % peerid
                peerconn.senddata( ERROR, msg)
        finally:
            self.peerlock.release()




    def __name_handler(self, peerconn, data):
        """handle query peer node id message, NAME, data is not needed"""
        peerconn.senddata(REPLY, self.myid)

    def addfile( self, filename ):
        """add file into local cache based on LRU policy"""
        self.cachefile[filename] = None

    def removefile(sefl, filename):
        """remove file from the local cache based on LRU policy """


    def buildpeers(self, host, port, hops=1):
        if self.maxpeersreached() or not hops:
            return
        peerid = None
        try:
            _, peerid = self.connectandsend(host, port, NAME, '')[0]

            resp = self.connectandsend(host, port, JOIN, '%s %s %d' %
                    (self.myid, self.serverhost, self.serverport))[0]

            if ( resp[0] != REPLY ) or ( peerid in self.getpeerids() ):
                return

            self.addpeer( peerid, host, port )

            # do dfs search and add peers
            resp = self.connectandsend( host, port, LIST, '', pid=peerid)
            if len(resp) > 1:
                nextpid, host, port = resp.pop()[1].split()
                if nextpid != self.myid:
                    self.buildpeers(host, port, hops-1)
        except:
            if self.debug:
                traceback.print_exc()
                self.removepeer(peerid)
