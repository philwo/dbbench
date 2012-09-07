#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Performs randomized INSERT queries on a test database in multiple threads.
#
#   Copyright 2012 by Philipp Wollermann
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

from __future__ import division
import sys
import string
import threading
import logging
from time import time, sleep
from random import choice, randrange

import settings


def randstring(len):
    return ''.join(choice(string.letters) for i in xrange(len))


class Worker(threading.Thread):
    def __init__(self):
        super(Worker, self).__init__()
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        vhost_list = ['www.mycompany.co.jp', 'www.company.info', 'www.service.io', 'www.website.com']
        status_list = [200, 404, 500]
        timestamp = time()

        while not self.stopped():
            start = time()
            conn = settings.db_connect()
            cur = conn.cursor()

            parameters = []
            for i in xrange(settings.INSERT_ROW_COUNT):
                vhost = choice(vhost_list)
                rhost = '.'.join((str(randrange(1, 256)), str(randrange(1, 256)), str(randrange(1, 256)), str(randrange(1, 256))))
                logname = '-'
                username = randstring(10)
                timestamp += randrange(0, 5) / 10
                request = '/%s/%s/%s.html' % (randstring(20), randstring(20), randstring(20))
                status = choice(status_list)
                response_size = randrange(1, 16 * 1024 * 1024)
                parameters.append((vhost, rhost, logname, username, settings.db_TimestampFromTicks(timestamp), request, status, response_size))

            cur.executemany('INSERT INTO ' + settings.DB_TABLE + ' (vhost, rhost, logname, username, timestamp, request, status, response_size) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', parameters)

            conn.commit()
            cur.close()
            conn.close()

            end = time()
            logging.info('Inserting %s records took %.2f seconds... (%.2f seconds per 1000 records)' % (len(parameters), (end - start), (end - start) / len(parameters) * 1000))


def main():
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(levelname)s] (%(threadName)-10s) %(message)s',
    )

    # Start worker threads
    try:
        threads = [Worker() for i in xrange(settings.THREAD_COUNT)]
        for thread in threads:
            thread.start()

        while True:
            sleep(1)
    except (KeyboardInterrupt, SystemExit):
        for thread in threads:
            thread.stop()

if __name__ == "__main__":
    sys.exit(main())
