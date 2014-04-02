#! /usr/bin/env/python
import snakemq.link
import snakemq.packeter
import snakemq.messaging
import snakemq.message
import threading
import time

def on_recv(conn, ident, message):
    print("received from", conn, ident, message.data)

def f():
    time.sleep(1)
    c = None
    while True:
        if list(my_messaging._conn_by_ident.keys()):
            c = 1
        if c:
            message = snakemq.message.Message(b"hello", ttl=600)
            my_messaging.send_message("alice", message)
        time.sleep(2)

my_link = snakemq.link.Link()
my_packeter = snakemq.packeter.Packeter(my_link)
my_messaging = snakemq.messaging.Messaging("bob", "", my_packeter, None)

my_link.add_listener(("", 4000))  # listen on all interfaces and on port 4000
my_link.add_connector(("localhost", 4001))


t = threading.Thread(target=f)    # create a thread objetc by passing a callable object
t.setDaemon(1)
t.start()

my_messaging.on_message_recv.add(on_recv)

my_link.loop()
