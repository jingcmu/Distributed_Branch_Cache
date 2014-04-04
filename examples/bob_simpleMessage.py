#! /usr/bin/env/python
import snakemq.link
import snakemq.packeter
import snakemq.messaging
import snakemq.message
import time


my_link = snakemq.link.Link()
my_packeter = snakemq.packeter.Packeter(my_link)
my_messaging = snakemq.messaging.Messaging("bob", "", my_packeter, None)


my_link.add_listener(("", 4000))  # listen on all interfaces and on port 4000
my_link.add_connector(("localhost", 4001))
message = snakemq.message.Message(b"hello", ttl=600)

def on_conn(conn, ident):
    while True:
        if list(my_messaging._conn_by_ident.keys()):
            c = 1
        if c:
            my_messaging.send_message("alice", message)
            print ("sending")
        time.sleep(2)
        break

my_messaging.on_connect.add(on_conn)
#my_messaging.send_message("alice", message)

print ("ready to go")
my_link.loop()
