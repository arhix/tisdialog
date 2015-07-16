#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import ConfigParser
import re
import urllib2
import base64

from BeautifulSoup import BeautifulSoup
from BrendyBot import BrendyBot


class TisChecker:
    headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}

    def get_daemon_timeout(self):
        return self.daemon_timeout

    def __init__(self):
        # log init
        logging.basicConfig(filename=os.path.dirname(os.path.abspath(__file__)) + '/TisChecker.log',
                            level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%Y-%m-%d %I:%M:%S')
        logging.info('TisChecker init')

        # read config
        config = ConfigParser.ConfigParser()
        config_path = os.path.dirname(os.path.abspath(__file__)) + '/config.cfg'
        if os.path.exists(config_path):
            config.read(config_path)
        else:
            message = 'File "config.cfg" does not exist. All stopped.'
            logging.error(message)
            sys.exit(2)

        # -- daemon timeout
        if config.has_option('daemon', 'timeout'):
            self.daemon_timeout = config.getint('daemon', 'timeout')

        # -- tis config
        try:
            self.tisURL = config.get('tis', 'url')
            self.tisLogin = config.get('tis', 'login')
            self.tisPassword = config.get('tis', 'password')
        except ConfigParser.Error:
            logging.error('Not configurated tis". All stopped.')
            sys.exit(2)

        # -- brendy config
        try:
            self.xmpp_jid = config.get('brendy', 'login')
            self.xmpp_pwd = config.get('brendy', 'password')
            self.reportTo = config.get('brendy', 'recipient')
        except ConfigParser.Error:
            logging.error('Not configurated brendy. All stopped.')
            sys.exit(2)

        logging.info('Fire!!')

    def check(self):
        logging.info('TisChecker start')

        page_request = urllib2.Request(self.tisURL, headers=self.headers)
        page_request.add_header('Authorization', b'Basic ' + base64.b64encode(self.tisLogin + b':' + self.tisPassword))
        page_data = urllib2.urlopen(page_request)

        if page_data.getcode() not in [200]:
            logging.error('Page code {}'.format(page_data.getcode()))
            return

        try:
            soup = BeautifulSoup(page_data.read()).find('table', 'usrtbl')
            cells = soup.find(text=u"На счёте: ").findNext().text
            val = re.findall("\d+,\d+", cells)[0]
        except BeautifulSoup.Exception:
            logging.error('Not found data')
            return

        val = float(val.replace(',', '.'))
        its = 'Good' if val > 10 else 'Bad'

        brendy = BrendyBot(self.xmpp_jid, self.xmpp_pwd)
        brendy.send(self.reportTo, 'You have {} Rub. It is {}!'.format(val, its))

        logging.info('Check completed.')


if __name__ == '__main__':
    c = TisChecker()
    c.check()
