#!/usr/bin/python

import xmpp


class BrendyBot:
    def __init__(self, login, password, debug=None):
        self.brendy = None
        self.xmpp_jid = login
        self.xmpp_pwd = password
        self.debug = debug

    def conn(self):
        if self.brendy is None:
            jid = xmpp.JID(self.xmpp_jid)
            self.brendy = xmpp.Client(jid.getDomain(), debug=self.debug)

            if not self.brendy.connect():
                print('Can not connect to server.')
            if not self.brendy.auth(jid.getNode(), self.xmpp_pwd):
                print('Can not auth with server.')

            self.brendy.sendInitPresence(0)

        return self.brendy

    def send(self, to, message):
        self.conn().send(xmpp.Message(to, message, typ='chat'))
