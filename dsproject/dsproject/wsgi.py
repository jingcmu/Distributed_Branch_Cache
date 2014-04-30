"""
WSGI config for dsproject project.

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
from cachepeer.views import *
from dsproject.settings import *

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
# os.environ["DJANGO_SETTINGS_MODULE"] = "dsproject.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dsproject.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from threading import Thread
from webob import Request
from socket import socket
from select import select
from Queue import Queue
import re
from django.core.wsgi import get_wsgi_application

# def input_loop(app):
#     sock = socket()
#     sock.bind(('', 9999))
#     sock.listen(1)
#     while True:
#         print 'Waiting for input stream'
#         sd, addr = sock.accept()
#         print 'Connected input stream from', addr
#         data = True
#         while data:
#             readable = select([sd], [], [], 0.1)[0]
#             for s in readable:
#                 data = s.recv(1024*1024*4)
#                 if not data:
#                     break
#                 for q in app.queues:
#                     q.put(data)
#         print 'Lost input stream from', addr


application = get_wsgi_application()
with open('configure', 'r') as f:
    configuration = {}
    for line in f:
        key, value = line.split(":")
        configuration[key] = value

cache_path = os.getcwd() + CACHE_FILE_DIRS
cachepeer = CachePeer( configuration['maxpeers'], configuration['serverport'] , cache_path)
cachepeer.buildpeers( configuration['host'], int(configuration['port']), hops=configuration['hops'] )
logfile = os.getcwd() + CACHE_FILE_DIRS + configuration['logfile']
cachepeer.addfile( logfile )
print cachepeer.cachefile
# start cachepeer thread
t = threading.Thread( target=cachepeer.mainloop, args=[])
t.start()
cachepeer.startstabilizer( cachepeer.checklivepeers, 3)

# start streaming thread 
# t1 = Thread(target=input_loop, args=[application])
# t1.setDaemon(True)
# t1.start()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
