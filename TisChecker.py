#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, logging, tempfile, ConfigParser, re, urllib2, base64
from BeautifulSoup import BeautifulSoup
from BrendyBot import BrendyBot

class TisChecker:
    headers = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' }
    
    def getDaemonTimeout(self):
        return self.daemonTimeout
    
    def __init__(self):
        # log init
        logging.basicConfig(filename = os.path.dirname(os.path.abspath(__file__)) + '/TisChecker.log',
                            level = logging.DEBUG,
                            format = '%(asctime)s %(levelname)s: %(message)s',
                            datefmt = '%Y-%m-%d %I:%M:%S')
        logging.info('Daemon start')
        
        # read config
        config = ConfigParser.ConfigParser()
        configPath = os.path.dirname(os.path.abspath(__file__)) + '/config.cfg'
        if os.path.exists(configPath):
            config.read(configPath)
        else:
            message = 'File "config.cfg" does not exist. Daemon stopped.'
            logging.error(message)
            sys.exit(2)
            
        # -- daemon timeout
        if config.has_option('daemon', 'timeout'):
            self.daemonTimeout = config.getint('daemon', 'timeout')
            
        # -- tis config
        if config.has_option('tis', 'url') and config.has_option('tis', 'login') and config.has_option('tis', 'password'):
            self.tisURL = config.get('tis', 'url')
            self.tisLogin = config.get('tis', 'login')
            self.tisPassword = config.get('tis', 'password')
        else:
            logging.error('Not configurated tis". Daemon stopped.')
            sys.exit(2)
        
        # -- brendy config
        if config.has_option('brendy', 'login') and config.has_option('brendy', 'password') and config.has_option('brendy', 'recipient'):
            self.xmpp_jid = config.get('brendy', 'login')
            self.xmpp_pwd = config.get('brendy', 'password')
            self.reportTo = config.get('brendy', 'recipient')
        else:
            logging.error('Not configurated brendy. Daemon stopped.')
            sys.exit(2)
            
        logging.info('Fire!!')
        
    def check(self):
        pageRequest = urllib2.Request(self.tisURL, headers=self.headers)
        pageRequest.add_header('Authorization', b'Basic ' + base64.b64encode(self.tisLogin + b':' + self.tisPassword))
        pageData = urllib2.urlopen(pageRequest)
        
        if pageData.getcode() not in [200]:
            logging.error('Page code {}'.format(pageData.getcode()))
            return;
        
        try:
            soup = BeautifulSoup(pageData.read()).find('table', 'usrtbl')
            cells = soup.find(text=u"На счёте: ").findNext().text
            val = re.findall("\d+,\d+", cells)[0]
        except Exception:
            logging.error('Not found data')
            return;
        
        val = float(val.replace(',','.'))
        its = 'Good' if val > 10 else 'Bad'
        
        brendy = BrendyBot(self.xmpp_jid, self.xmpp_pwd)
        brendy.send(self.reportTo, 'You have {} Rub. It\'s is {}!'.format(val, its))
        
        logging.info('Check completed.')
        
if __name__ == '__main__':
    c = TisChecker()
    c.check()