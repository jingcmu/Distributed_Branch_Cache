#!  /usr/bin/env/python
import snakemq.link
import snakemq.packeter
import snakemq.messaging
import snakemq.message

def on_recv(conn, ident, message):
    print("received from", conn, ident, message)

my_link = snakemq.link.Link()
my_packeter = snakemq.packeter.Packeter(my_link)
my_messaging = snakemq.messaging.Messaging("alice", "", my_packeter, None)

my_link.add_connector(("localhost", 4000))
my_link.add_listener(("", 4001))

my_messaging.on_message_recv.add(on_recv)


my_link.loop()
