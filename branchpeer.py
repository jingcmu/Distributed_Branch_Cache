#!/usr/bin/env/python

import socket
import struct
import threading
import time
import traceback


def debughelper( msg ):
    """ print current thread id and msg """
    print "[%s] %s" % ( str(threading.currentThread().getName()), msg )


#==============================================================================
class BranchPeer:

    def __init__( self, maxpeers, serverport, myid=None, serverhost = None ):
	""" Initializes a peer servent (sic.) with the ability to catalog
	information for up to maxpeers number of peers (maxpeers may
	be set to 0 to allow unlimited number of peers), listening on
	a given server port , with a given canonical peer name (id)
	and host address. If not supplied, the host address
	(serverhost) will be determined by attempting to connect to an
	Internet host like Google.
	"""
        self.debug = 0

        self.maxpeers = int(maxpeers)
        self.serverport = int(serverport)

        # If not supplied, the host name/IP address will be determined
        # by attempting to connect to an Internet host like Google.
        if serverhost: 
            self.serverhost = serverhost
        else: 
            self.__initserverhost()
        # If not supplied, the peer id will be composed of the host address
        # and port number
        if myid: 
            self.myid = myid
        else: 
            self.myid = '%s:%d' % (self.serverhost, self.serverport)
        # list (dictionary/hash table) of known peers
        self.peers = {}  

        # used to stop the main loop
        self.shutdown = False  

        self.handlers = {}
        self.router = None

        # end of __init__ function
    def __initserverhost( self ):
	""" using Google as host to determine local ip address. """
	
    
    def __debug( self, msg ):
    """ calling  debughelper function. """	



    def __handlepeer( self, clientsock ):
	""" Dispatches messages from the socket connection """
        self.__debug( 'Connected ' + str(clientsock.getpeername()) )

        host, port = clientsock.getpeername()
        peerconn = BTPeerConnection( None, host, port, clientsock, debug=False )
        
        try:
            msgtype, msgdata = peerconn.recvdata()
            if msgtype: msgtype = msgtype.upper()
            if msgtype not in self.handlers:
                self.__debug( 'Not handled: %s: %s' % (msgtype, msgdata) )
            else:
                self.__debug( 'Handling peer msg: %s: %s' % (msgtype, msgdata) )
                self.handlers[ msgtype ]( peerconn, msgdata )
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
        
        self.__debug( 'Disconnecting ' + str(clientsock.getpeername()) )
        peerconn.close()

    # end handlepeer method



    def __runstabilizer( self, stabilizer, delay ):



    def setmyid( self, myid ):



    def startstabilizer( self, stabilizer, delay ):
	""" Runs the provided 'stabilizer' function in a separate thread, 
    activating it repeatedly after every delay seconds, 
    until the shutdown flag of the Peer object is set
	"""



    def addhandler( self, msgtype, handler ):
	""" Registers the handler for the given message type with this peer """



    def addrouter( self, router ):
	""" Registers a routing function with this peer. 
	"""



    def addpeer( self, peerid, host, port ):
	""" Adds a peer name and host:port mapping to the known list of peers.

	"""



    def getpeer( self, peerid ):
	""" Returns the (host, port) tuple for the given peer name """



    def removepeer( self, peerid ):
	""" Removes peer information from the known list of peers. """



    def addpeerat( self, loc, peerid, host, port ):
	""" Inserts a peer's information at a specific position in the
	list of peers. 
	"""



    def getpeerat( self, loc ):



    def removepeerat( self, loc ):



    def getpeerids( self ):
	""" Return a list of all known peer id's. """



    def numberofpeers( self ):
	""" Return the number of known peer's. """



    def maxpeersreached( self ):
	""" Returns whether the maximum limit of names has been added to the
	list of known peers. Always returns True if maxpeers is set to
	0.
	"""



    def makeserversocket( self, port, backlog=5 ):
	""" Constructs and prepares a server socket listening on the given
	port.

	"""
        s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        s.bind( ( '', port ) )
        s.listen( backlog )
        return s



    def sendtopeer( self, peerid, msgtype, msgdata, waitreply=True ):
	"""
	sendtopeer( peer id, message type, message data, wait for a reply )
	 -> [ ( reply type, reply data ), ... ]
	"""
        if self.router:
            nextpid, host, port = self.router( peerid )
        if not self.router or not nextpid:
            self.__debug( 'Unable to route %s to %s' % (msgtype, peerid) )
            return None
        return self.connectandsend( host, port, msgtype, msgdata, pid=nextpid,
                    waitreply=waitreply )

    # end sendtopeer method




    def connectandsend( self, host, port, msgtype, msgdata,
			pid=None, waitreply=True ):
	"""
    connectandsend( host, port, message type, message data, peer id,
	wait for a reply ) -> [ ( reply type, reply data ), ... ]
	"""
        msgreply = []   # list of replies
        try:
            peerconn = BTPeerConnection( pid, host, port, debug=self.debug )
            peerconn.senddata( msgtype, msgdata )
            self.__debug( 'Sent %s: %s' % (pid, msgtype) )
            
            if waitreply:
            onereply = peerconn.recvdata()
            while (onereply != (None,None)):
                msgreply.append( onereply )
                self.__debug( 'Got reply %s: %s' % ( pid, str(msgreply) ) )
                onereply = peerconn.recvdata()
            peerconn.close()
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
            traceback.print_exc()
        
        return msgreply

    def checklivepeers( self ):
	""" Attempts to ping all currently known peers in order to ensure that
	they are still active. Removes any from the peer list that do
	not reply. This function can be used as a simple stabilizer.

	"""
    def mainloop( self ):
        s = self.makeserversocket( self.serverport )
        s.settimeout(2)
        self.__debug( 'Server started: %s (%s:%d)'
              % ( self.myid, self.serverhost, self.serverport ) )

        while not self.shutdown:
            try:
                self.__debug( 'Listening for connections...' )
                clientsock, clientaddr = s.accept()
                clientsock.settimeout(None)

                t = threading.Thread( target = self.__handlepeer, args = [ clientsock ] )
                t.start()
            except KeyboardInterrupt:
                self.shutdown = True
                continue
            except:
                if self.debug:
                    traceback.print_exc()
                    continue
        # end while loop
        self.__debug( 'Main loop exiting' )
        s.close()
    # end mainloop method

# end BranchPeer class

# **********************************************************




class BranchPeerConnection:

    def __init__( self, peerid, host, port, sock=None, debug=False ):


    def __makemsg( self, msgtype, msgdata ):


    def __debug( self, msg ):


    def senddata( self, msgtype, msgdata ):
	"""
	Send a message through a peer connection. Returns True on success
	or False if there was an error.
	"""



    def recvdata( self ):
	"""
	Receive a message from a peer connection. Returns (None, None)
	if there was any error.
	"""



    def close( self ):
	"""
	Close the peer connection. The send and recv methods will not work
	after this call.
	"""

    def __str__( self ):
