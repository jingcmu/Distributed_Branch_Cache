import socket
class BranchPeerConnection:
    def __init__( self, peerid=None, host, port, sock=None, debug=False ):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.msgtype = None
        self.msgdata = None
        self.data = None

    def connect( self, num ):
        self.sock.listen(num)
        self.sock.accept()

    def __makemsg( self, msgtype, msgdata ):
        self.msgtype = msgtype
        self.msgdata = msgdata
        self.data = msgtype.encode('utf-8') + msgdata.encode('utf-8')

    def __debug( self, msg ):
        print msg

    """
    Send a message through a peer connection. Returns True on success
    or False if there was an error.
    """
    def senddata( self, msgtype, msgdata ):
        self.__makemsg(msgtype, msgdata)
        self.sock.send(self.data)

    """
    Receive a message from a peer connection. Returns (None, None)
    if there was any error.
    """
    def recvdata( self ):
        self.data = self.sock.recv()

    """
    Close the peer connection. The send and recv methods will not work
    after this call.
    """
    def close( self ):
        self.sock.close()

    def __str__( self ):
        return