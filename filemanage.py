import os
import hashlib

class FileManager:
    def __init__( self, size, debug=False ):
        self.spacesize = size # space size of cache
        self.filehandler = None

    #open a file and get the file handler
    def openfile(self, filename):
        self.filehandler = open(filename)

	def split(self, pathfilename, chunksize):
		#split a file into many small files with chunksize bytes
		#the small files will be put into \tmp under local path
		statinfo = os.stat(pathfilename)
		path, filename = os.path.split(pathfilename)
		tmppath = path + '\\tmp'
		if not os.path.exists(tmppath):
			os.mkdir(tmppath)
		print "file size: %d(kb)" % (statinfo.st_size/(1024))
		with open(pathfilename, "rb") as f:
			index = 0
			while True:
				chunk = f.read(chunksize * 1024)
				if(chunk):
					fn = "%s\%s.part.%d" % (tmppath, filename, index)
					index = index + 1
					print "creating", fn
					with open(fn, "wb") as fw:
						fw.write(chunk)
				else:
					break
		print "split finished"

	def combine(self, pathfilename, filesize, chunksize):
		# pathfilename: this is the file path outside \tmp folder
		# filesize: how many bytes are in the file, this should be known beforehand
		# chunksize: how many kb for one chunk, default 512 kb
		# brief explain: all the temporary files are in the \tmp folder and after combining the tmp files
		# the tmp files will be destroied
		filenum = filesize/(chunksize*1024) + 1
		path, filename = os.path.split(pathfilename)
		tmppath = path + '\\tmp'
		tmppathfilename = tmppath + '\\' + filename
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
		""" to get md5 hash for a file """
		md5 = hashlib.md5()
		with open(pathfilename, "rb") as f:
			while True:
				data = f.read(block_size)
				if not data:
					break
				md5.update(data)
		return md5.hexdigest()

    #close a file
    def close( self ):
        self.filehandler.close()

    def __debug( self, msg ):
        print msg
