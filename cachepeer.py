#! /usr/bin/env/python

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
            ERROR:  self.__error_handler,
            REPLY:  self.__reply_handler
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


    def __join_handler(self, peerconn, data):
        """handle join network message, JOIN, data format : "peerid  host  port" """


    def __query_handler(self, peerconn, data):
        """handle query message, QUERY, data format : "peer-id  keyword  ttl" """

    def __processquery(self, peerid, key, ttl):
        """process the query message in this function, replying with either a RESP if file found, 
        or propagating msg to its all peers """

    def __resp_handler(self, peerconn, data):
        """handle response message, RESP, data format should be "file-name, peer-id" """   

    def __fileget_handler(self, peerconn, data):
        """handle file get message, FILEGET data format should  a string "file-name" """

    def __quit_handler(self, peerconn, data):
        """handle peer quit message, data is not needed """
    
    def __name_handler(self, peerconn, data):
        """handle query peer node id message, NAME, data is not needed"""

    def addfile( self, filename ):
        """add file into local cache based on LRU policy"""

    def removefile(sefl, filename):
        """remove file from the local cache based on LRU policy """


    def buildpeers(self, host, port, hops=1):
    """ Build the local peer list up to the limit stored by
    self.maxpeers, using a simple depth-first search given an
    initial host and port as starting point. The depth of the
    search is limited by the hops parameter. """









