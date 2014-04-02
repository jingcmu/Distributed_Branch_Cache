#! /usr/bin/env/python
import snakemq.link
import snakemq.packeter
import snakemq.messaging
import snakemq.message
from snakemq.storage.sqlite import SqliteQueuesStorage
from snakemq.message import FLAG_PERSISTENT
import time


my_link = snakemq.link.Link()
my_packeter = snakemq.packeter.Packeter(my_link)
storage = SqliteQueuesStorage("storage.db")
my_messaging = snakemq.messaging.Messaging("bob", "", my_packeter, storage)
rh = snakemq.messaging.ReceiveHook(my_messaging)


my_link.add_listener(("", 4000))  # listen on all interfaces and on port 4000
my_link.add_connector(("localhost", 4001))
message = snakemq.message.Message(b"hello", ttl=600, flags=FLAG_PERSISTENT)

def on_conn(conn, ident):
    while True:
        my_messaging.send_message("alice", message)
        print "sending"
        time.sleep(1)

my_messaging.on_connect.add(on_conn)
#my_messaging.send_message("alice", message)

print "ready to go"
my_link.loop()
