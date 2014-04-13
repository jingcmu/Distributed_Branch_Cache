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

    def __init__( self, maxpeers, serverport, myid=None, serverhost="128.2.246.39"):
        """ Initializes a peer servent (sic.) with the ability to catalog
        information for up to maxpeers number of peers (maxpeers may
        be set to 0 to allow unlimited number of peers), listening on
        a given server port , with a given canonical peer name (id)
        and host address. If not supplied, the host address
        (serverhost) will be determined by attempting to connect to an
        Internet host like Google.
        """
        self.debug = 1

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
        
        self.peerlock = threading.Lock()

        # list (dictionary/hash table) of known peers
        self.peers = {}

        # used to stop the main loop
        self.shutdown = False

        self.handlers = {}
        self.router = None

        # end of __init__ function
    def __initserverhost( self ):
        """ using CMU server as host to determine local ip address. """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect (("www.google.com", 80))
        self.serverhost = s.getsockname()[0]
        s.close()

    def __debug( self, msg ):
        """ calling  debughelper function. """
        if self.debug:
            debughelper(msg)


    def __handlepeer( self, clientsock ):
        """ Dispatches messages from the socket connection """
        host, port = clientsock.getpeername()
        peerconn = BranchPeerConnection( None, host, port, clientsock, debug=False )

        try:
            msgtype, msgdata = peerconn.recvdata()
            if msgtype:
                msgtype = msgtype.upper()
            if msgtype not in self.handlers:
                self.__debug( 'Not handled: %s: %s' % (msgtype, msgdata) )
            else:
                self.handlers[ msgtype ]( peerconn, msgdata )
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()

        peerconn.close()

    # end handlepeer method



    def __runstabilizer( self, stabilizer, delay ):
        """run a seperate thread during delay interval """
        stabilizer()
        time.sleep(delay)


    def setmyid( self, myid ):
        self.myid = myid


    def startstabilizer( self, stabilizer, delay ):
        """ Runs the provided 'stabilizer' function in a separate thread,
        activating it repeatedly after every delay seconds,
        until the shutdown flag of the Peer object is set
        """
        t = threading.Thread(target = self.__runstabilizer, args = [stabilizer, delay])
        t.start()


    def addhandler( self, msgtype, handler ):
        """ Registers the handler for the given message type with this peer """
        self.handlers[ msgtype ] = handler


    def addrouter( self, router ):
        """ Registers a routing function with this peer."""
        self.router = router



    def addpeer( self, peerid, host, port ):
        """ Adds a peer name and host:port mapping to the known list of peers.
            Successful, return True
            otherwise, return False
        """
        if peerid not in self.peers and (self.maxpeers == 0 or len(self.peers) < self.maxpeers):
            self.peers[ peerid ] = (host, int(port))
            return True
        else:
            return False


    def getpeer( self, peerid ):
        """ Returns the (host, port) tuple for the given peer name """
        return self.peers[ peerid ]


    def removepeer( self, peerid ):
        """ Removes peer information from the known list of peers. """
        if peerid in self.peers:
            del self.peers[ peerid ]


    def addpeerat( self, loc, peerid, host, port ):
        """ Inserts a peer's information at a specific position in the
        list of peers.
        """
        self.peersp[ loc ] = (peerid, host, int(port))


    def getpeerat( self, loc ):
        if loc not in self.peers:
            return None
        return self.peers[ loc ]


    def removepeerat( self, loc ):
        self.removepeer(self, loc)


    def getpeerids( self ):
        """ Return a list of all known peer id's. """
        return self.peers.keys()


    def numberofpeers( self ):
        """ Return the number of known peer's. """
        return len(self.peers)


    def maxpeersreached( self ):
        """ Returns whether the maximum limit of names has been added to the
        list of known peers. Always returns True if maxpeers is set to
        0.
        """
        return self.maxpeers > 0 and len(self.peers) == self.maxpeers


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
            peerconn = BranchPeerConnection( pid, host, port, debug=self.debug )
            peerconn.senddata( msgtype, msgdata )
            if waitreply:
                onereply = peerconn.recvdata()
            while (onereply != (None,None)):
                msgreply.append( onereply )
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
        deletelist = []
        for pid in self.peers:
            isconn = False
            try:
                host, port = self.peers[ pid ]
                peerconn = BranchPeerConnection( pid, host, port, debug=self.debug)
                peerconn.senddata('ping', '')
                isconn = True
            except:
                deletelist.append( pid )
                if isconn:
                    peerconn.close()

        self.peerlock.acquire()
        try:
            for pid in deletelist:
                if pid in self.peers:
                    del self.peers[ pid ]
        finally:
            self.peerlock.release()

    # end of check peers avaliablity

    def mainloop( self ):
        s = self.makeserversocket( self.serverport )
        s.settimeout(2)

        while not self.shutdown:
            try:
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
        s.close()
    # end mainloop method

# end BranchPeer class

# **********************************************************


class BranchPeerConnection:
    def __init__( self, peerid, host, port, sock=None, debug=False ):
        self.id = peerid
        self.debug = debug

        if sock == None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect ( (host, int(port)) )
        else:
            self.sock = sock

        self.tempfile = self.sock.makefile( 'rw', 0 )

    # def connect( self, num ):
    #     self.sock.listen(num)
    #     self.sock.accept()

    def __makemsg( self, msgtype, msgdata ):
        msglen = len(msgdata)
        msg = struct.pack( "!4sL%ds" % msglen, msgtype, msglen, msgdata )
        return msg

    def __debug( self, msg ):
        if self.debug:
            debughelper(msg)


    def senddata( self, msgtype, msgdata ):
        """
        Send a message through a peer connection. Returns True on success
        or False if there was an error.
        """
        try:
            msg = self.__makemsg(msgtype, msgdata)
            self.tempfile.write(msg)
            self.tempfile.flush()
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
                return False

        return True

    def recvdata( self ):
        """
        Receive a message from a peer connection. Returns (None, None)
        if there was any error.
        """
        try:
            msgtype = self.tempfile.read( 4 )
            if not msgtype:
                return (None, None)
            lenstr = self.tempfile.read( 4 )
            msglen = int ( struct.unpack( "!L", lenstr)[0] )

            msg = ""
            while len(msg) != msglen:
                data = self.tempfile.read(min (1024, msglen - len(msg)))
                if not len(data):
                    break
                msg += data

            if len(msg) != msglen:
                return (None, None)
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
                return (None, None)
        return (msgtype, msg)

    def close( self ):
        """
        Close the peer connection. The send and recv methods will not work
        after this call.
        """
        self.sock.close()
        self.sock = None
        self.tempfile = None

    def __str__( self ):
        return "{%s}" % self.peerid
