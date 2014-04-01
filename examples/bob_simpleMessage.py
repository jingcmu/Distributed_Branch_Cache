#! /usr/bin/env/python
import snakemq.link
import snakemq.packeter
import snakemq.messaging
import snakemq.message
from snakemq.storage.sqlite import SqliteQueuesStorage
from snakemq.message import FLAG_PERSISTENT

def on_recv(conn, ident, message):
    print (conn, ident,message)

my_link = snakemq.link.Link()
my_packeter = snakemq.packeter.Packeter(my_link)
storage = SqliteQueuesStorage("storage.db")
my_messaging = snakemq.messaging.Messaging("bob", "", my_packeter, storage)
rh = snakemq.messaging.ReceiveHook(my_messaging)


my_link.add_listener(("", 4000))  # listen on all interfaces and on port 4000
my_link.add_connector(("localhost", 4001))

message = snakemq.message.Message(b"hello", ttl=600, flags=FLAG_PERSISTENT)
my_messaging.send_message("alice", message)


my_link.loop()
