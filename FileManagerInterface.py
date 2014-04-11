# an iterface for FileManager class
# add any function as needed

class FileManager:

    def requestFile(self, filename):
    
    def findCachedFile(self, filename):
    
    def responseFileExsistence(self, client):
    
    def requestChunkRange(self, filename, filesize, peerList):
    
    def transmitChunk(self, chunkRange, peer):
    
    def splitFile(self, pathfilename, chunksize):
    
    def combineFile(self, pathfilename, filesize, chunksize):
    
    