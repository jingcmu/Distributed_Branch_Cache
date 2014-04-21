"""
WSGI config for mysite project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
# os.environ["DJANGO_SETTINGS_MODULE"] = "mysite.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
# from django.core.wsgi import get_wsgi_application
from flup.server.fcgi import WSGIServer
from threading import Thread
from webob import Request
from socket import socket
from select import select
from Queue import Queue
import re

class LiveHTTPStreamer(object):
    def __init__(self):
    	print "init"
        self.urls = [
            ('^/stream.m3u8$', self.index),
            ('^/stream.ts$', self.stream),
        ]
        self.urls = [(re.compile(pattern), func) for pattern, func in self.urls]
        self.queues = []

    def __call__(self, environ, start_response):
    	print "call"
        request = Request(environ)
        
        for pattern, func in self.urls:
            match = pattern.match(request.path_info)
            if match:
            	print "match"
                return func(start_response, request, match)
        print "not match"
        return self.redirect(start_response, request, match)

    def redirect(self, start_response, request, match):
        start_response('302 Found', [('Location', 'http://127.0.0.1:9998/stream.m3u8')])
        return ['']

    def index(self, start_response, request, match):
        start_response('200 OK', [('Content-type', 'application/x-mpegURL')])
        return ['''#EXTM3U
					#EXTINF:10,
					http://127.0.0.1:9998/San_Diego_Clip.ts
					#EXT-X-ENDLIST''']

    def stream(self, start_response, request, match):
        start_response('200 OK', [('Content-type', 'video/MP2T')])
        q = Queue()
        self.queues.append(q)
        print 'Starting output stream for', request.remote_addr
        while True:
            try:
                yield q.get()
            except:
                if q in self.queues:
                    self.queues.remove(q)
                    print 'No longer sending data to', request.remote_addr
                return

def input_loop(app):
    sock = socket()
    sock.bind(('', 9999))
    sock.listen(1)
    while True:
        print 'Waiting for input stream'
        sd, addr = sock.accept()
        print 'Connected input stream from', addr
        data = True
        while data:
            readable = select([sd], [], [], 0.1)[0]
            for s in readable:
                data = s.recv(1024)
                if not data:
                    break
                q = Queue()
                # print "before"
                # q.put(data)
                # print q.get()
                # print "after"
                for q in app.queues:
                    q.put(data)
        print 'Lost input stream from', addr
    
 
application = LiveHTTPStreamer()
t1 = Thread(target=input_loop, args=[application])
t1.setDaemon(True)
t1.start()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
