
class FileManager:
    def __init__( self, size, debug=False ):
        self.spacesize = size # space size of cache
        self.filehandler = None

    #open a file and get the file handler
    def openfile(self, filename):
        self.filehandler = open(filename)

	import os

	def split(self, pathfilename, chunksize):
		#split a file into many small files with chunksize bytes
		#the small files will be put into \tmp under local path
		statinfo = os.stat(pathfilename)
		path, filename = os.path.split(pathfilename)
		tmppath = path + '\\tmp'
		if not os.path.exists(tmppath):
			os.mkdir(tmppath)
		print "file size: %d(mb)" % (statinfo.st_size/(1024*1024))
		with open(pathfilename, "rb") as f:
			index = 0
			while True:
				chunk = f.read(chunksize)
				if(chunk):
					fn = "%s\%s.part.%d" % (tmppath, filename, index)
					index = index + 1
					print "creating", fn
					with open(fn, "wb") as fw:
						fw.write(chunk)
				else:
					break

    #close a file
    def close( self ):
        self.filehandler.close()

    def __debug( self, msg ):
        print msg
