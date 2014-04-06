
class FileManager:
    def __init__( self, size, debug=False ):
        self.spacesize = size # space size of cache
        self.filehandler = None

    #open a file and get the file handler
    def openfile(self, filename):
        self.filehandler = open(filename)

    #close a file
    def close( self ):
        self.filehandler.close()

    def __debug( self, msg ):
        print msg
