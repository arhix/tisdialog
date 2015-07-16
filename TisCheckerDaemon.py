#!/usr/bin/env python

import sys
import time

from daemon import Daemon
from TisChecker import TisChecker


class TisCheckerDaemon(Daemon):
    def run(self):
        c = TisChecker()
        while True:
            c.check()
            time.sleep(c.get_daemon_timeout())


if __name__ == "__main__":
    daemon = TisCheckerDaemon('/tmp/daemon-example.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
