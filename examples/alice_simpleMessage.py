#!  /usr/bin/env/python
import snakemq.link
import snakemq.packeter
import snakemq.messaging
import snakemq.message
from snakemq.storage.sqlite import SqliteQueuesStorage
from snakemq.message import FLAG_PERSISTENT

def on_recv(conn, ident, message):
    print message

my_link = snakemq.link.Link()
my_packeter = snakemq.packeter.Packeter(my_link)
storage = SqliteQueuesStorage("storage.db")
my_messaging = snakemq.messaging.Messaging("alice", "", my_packeter, storage)

my_link.add_connector(("localhost", 4000))
my_link.add_connector(("localhost", 4001))
my_link.add_listener(("localhost", 4001))

my_messaging.on_message_recv.add(on_recv)


my_link.loop()
