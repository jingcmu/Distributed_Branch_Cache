#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time

import snakemq
import snakemq.link
import snakemq.packeter
import snakemq.messaging
import snakemq.rpc

class A(object):
    def get_fo(self, data=None):
        print(data)
        return "fo value"

s = snakemq.link.Link()

s.add_listener(("", 4000))

tr = snakemq.packeter.Packeter(s)
m = snakemq.messaging.Messaging("boss", "", tr)
rh = snakemq.messaging.ReceiveHook(m)
srpc = snakemq.rpc.RpcServer(rh)
srpc.register_object(A(), "abc")

s.loop()
