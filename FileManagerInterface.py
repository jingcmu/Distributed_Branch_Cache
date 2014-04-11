# an iterface for FileManager class
# add any function as needed

class FileManager:
    self.filesize
    self.chunkCount
    self.receivedChunkSigns
    self.receivedChunkCount

    def requestFile(self, filename):
    
    def findCachedFile(self, filename):
    
    def responseFileExsistence(self, client):
    
    def requestChunkRange(self, filename, filesize, peerList):
    
    def transmitChunk(self, chunkRange, peer):
    
    def splitFile(self, pathfilename, chunksize):
    
    def combineFile(self, pathfilename, filesize, chunksize):
    	
    def isFileReceived(self):
        if receivedChunkCount < chunkCount:
            return false;
        else:
            # might need to lock the global variable receivedChunkSign and receivedChunkCount
            for sign in receivedChunkSigns:
                if sign == false:
                    return false
            
            return true
    	
    
    
    