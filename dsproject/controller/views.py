# Create your views here.
from django.shortcuts import render_to_response, render
from django.template.context import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
import json
import sys
import time
import threading
from filemanager.views import *
from random import *
from cachepeer.views import *
from dsproject.wsgi import *
from dsproject.settings import *
import sys, traceback
import socket
import logging
logger = logging.getLogger(__name__)

CHUNKSIZE = 512
BUFSIZE = 4096

def index(request):
	logger.debug("logging here....")
	# try:
	# 	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# 	address = "10.10.0.100"
	# 	port = 8888
	# 	s.connect((address, port))
	# 	s.send("getfilelist"+"\t"+"f1")
	# 	recvtype =s.recv(1024)
	# 	recvdata =json.loads(s.recv(1024).strip())
	# 	return render_to_response('index.html', {'movie_list':recvdata}, context_instance=RequestContext(request))
	# except:
	return render_to_response('index.html', {'movie_list':[]}, context_instance=RequestContext(request))

def search(request, hashcode=None, filesize=None):
	if hashcode and filesize:
		hashcode = str(hashcode)
		filesize = int(filesize)
		logger.debug("search begin...")
		for pid in cachepeer.getpeerids():
			cachepeer.sendtopeer(pid, QUERY, "%s %s 4" % (cachepeer.myid, hashcode))

		time.sleep(1)
		if hashcode not in cachepeer.cachefile:
			
			logger.debug("not found in peers clusters...")
			logger.debug("fetch source file from server...")

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			# address = "10.10.0.100"
			# port = 8888
			s.connect((MAINSERVER, MAINPORT))

			s.send("getfile"+"\t"+hashcode)
			recvtype =s.recv(1024)
			if recvtype == "returnfile":
				try:
					logger.debug("Downloading from Main Server...")
					fname =  os.getcwd() + CACHE_FILE_DIRS + hashcode
					f = open(fname, 'wb')
					while True:
						filedata = s.recv(BUFSIZE)
						if filedata == 'EOF':
							break
						f.write(filedata)
					f.close()
					if os.path.getsize(fname) != filesize:
						os.remove(fname)
						return HttpResponse(json.dumps({"error" : "error"}), mimetype="application/json")
					
					logger.debug("update cache file...")
					cachepeer.cachefile[hashcode] = (None, filesize)
					logger.debug("update log file...")
					cachepeer.cachemanager.newlog(hashcode, str(filesize))
					
					return HttpResponse(json.dumps({"success" : "success"}), mimetype="application/json")
				except:
					return HttpResponse(json.dumps({"error" : "error"}), mimetype="application/json")

		pid = cachepeer.cachefile[hashcode][0]
		filesize = cachepeer.cachefile[hashcode][1]

		# arrange chunks to peers
		if pid == None:
			logger.debug("find file on local machine...")
			return HttpResponse(json.dumps({"success" : "success"}), mimetype="application/json")

		logger.debug("fetch file from peers node...")			
		pid_num = len(pid)
		chunk_num = int(filesize)/(CHUNKSIZE*1024) + 1
		chunk_per_peer = chunk_num/pid_num

		stack = []
		for i in xrange(chunk_num):
			stack.append(chunk_num - i - 1)

		while len(stack) != 0 and len(pid) != 0:
			available_pids = cachepeer.getpeerids()
			pid = list(set(pid) & set(available_pids)) # remove non-available peer id
			for i in xrange(len(pid)): # fetch a part from each available peer id
				host, port = pid[i].split(':')
				logger.debug("fetch part "+str(stack[len(stack)-1])+" from: "+str(pid[i]))
				code = fetchPart( hashcode, host, port, stack.pop(), chunk_num )
				if code != -1:
					stack.append(code)
				if len(stack) == 0:
					break

		# combine the temporary files
		filemanager = FileManager(int(filesize), CHUNKSIZE, os.getcwd() + CACHE_FILE_DIRS + hashcode)
		filemanager.combineFile()
		
		logger.debug("update cache file...")
		cachepeer.cachefile[hashcode] = (None, filesize)
		logger.debug("update log file...")
		cachepeer.cachemanager.newlog(hashcode, filesize)
		# print cachepeer.cachefile			

		return HttpResponse(json.dumps({"success" : "success"}), mimetype="application/json")


def fetchPart( hashcode, host, port, part, chunk_num ):
	# fetch part from host:port
	resp = cachepeer.connectandsend( host, port, FPART, "%s %d" % (hashcode, int(part)) )
	if len(resp) and resp[0][0]==REPLY and (len(resp[0][1]) == CHUNKSIZE*1024 or part == chunk_num - 1 ):
		tmppath = os.getcwd() + CACHE_FILE_DIRS +'tmpfetch'
		if not os.path.exists(tmppath):
			os.mkdir(tmppath)
		partfilename = tmppath + '/' + hashcode + ".part." + str(part)
		fd = file(partfilename, 'w')
		fd.write(resp[0][1])
		fd.close()
		return -1
	else:
		return part

    