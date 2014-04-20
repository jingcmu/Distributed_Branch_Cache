import os
import hashlib

class FileManager:
    def __init__( self, filesize, chunksize, pathfilename, debug=False ):
        self.filehandler = None
        self.filesize = filesize
        self.chunksize = chunksize
        self.chunkCount = (filesize + chunksize - 1)/chunksize
        self.receivedChunkSigns = [False] * self.chunksize
        self.receivedChunkCount = 0
        self.pathfilename = pathfilename

    #open a file and get the file handler
    def openfile(self, filename):
        self.filehandler = open(filename)

    def splitFile(self):
        #split a file into many small files with chunksize bytes
        #the small files will be put into \tmp under local path
        path, filename = os.path.split(self.pathfilename)
        tmppath = path + '/tmp'
        if not os.path.exists(tmppath):
            os.mkdir(tmppath)
        print "file size: %d(kb)" % (self.filesize/(1024))
        index = 0
        with open(self.pathfilename, "rb") as f:
            while True:
                chunk = f.read(self.chunksize * 1024)
                if(chunk):
                    fn = "%s/%s.part.%d" % (tmppath, filename, index)
                    index = index + 1
                    print "creating", fn
                    with open(fn, "wb") as fw:
                        fw.write(chunk)
                else:
                    break
        print "split finished"
        return index, tmppath

    def combineFile(self, pathfilename, filesize, chunksize):
        # pathfilename: this is the file path outside \tmp folder
        # filesize: how many bytes are in the file, this should be known beforehand
        # chunksize: how many kb for one chunk, default 512 kb
        # brief explain: all the temporary files are in the \tmp folder and after combining the tmp files
        # the tmp files will be destroied
        filenum = filesize/(chunksize*1024) + 1
        path, filename = os.path.split(pathfilename)
        tmppath = path + '/tmp'
        tmppathfilename = tmppath + '/' + filename
        with open(pathfilename, "ab+") as fw:
            for i in xrange(filenum):
                filename = tmppathfilename + ".part." + str(i)
                if os.path.exists(filename):
                    with open(filename, "rb") as f:
                        chunk = f.read(chunksize*1024)
                        if(chunk):
                            print "absorbing ", filename
                            fw.write(chunk)
                            f.close()
                        else:
                            print "missing part " + str(i)
                            break
            #destroy the temporary files
            for i in xrange(filenum):
                filename = tmppathfilename + ".part." + str(i)
                if os.path.exists(filename):
                    os.remove(filename)
                    print "destroyed ", filename
                else:
                    print "missing part " + str(i)
        print "combine finished"

    def md5_for_file(self, pathfilename, block_size=2**20):
        """ to get md5 hash for a file, return string """
        md5 = hashlib.md5()
        with open(pathfilename, "rb") as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                md5.update(data)
        return md5.hexdigest()

    def requestFile(self, filename):
        return

    def findCachedFile(self, filename):
        return

    def responseFileExsistence(self, client):
        return

    '''
    def isFileReceived(self):
        if receivedChunkCount < self.chunkCount:
            return False;
        else:
            # recalculate chunkcount
			chunkcount = 0
            for sign in receivedChunkSigns:
                if sign == True:
                    chunkcount += 1
            if chunkcount == self.chunkCount:
                return True
            else:
                self.chunkCount = chunkcount
        return False
    '''

    def __debug( self, msg ):
        print msg
