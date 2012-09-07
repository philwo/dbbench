#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Performs randomized SELECT queries on a test database in multiple threads.
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
import threading
import logging
from time import time, sleep
from random import randrange

import settings


class Worker(threading.Thread):
    def __init__(self, id_min, id_max):
        super(Worker, self).__init__()
        self._stop = threading.Event()
        self.id_min = id_min
        self.id_max = id_max

    def stop(self):
        logging.debug('Stopping...')
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        logging.debug('Starting...')
        while not self.stopped():
            start = time()
            conn = settings.db_connect()
            cur = conn.cursor()
            for i in xrange(settings.SELECT_ROW_COUNT):
                cur.execute('SELECT * FROM ' + settings.DB_TABLE + ' WHERE id = %s', (randrange(self.id_min, self.id_max),))
            conn.commit()
            cur.close()
            conn.close()
            end = time()
            logging.info('Selecting %s rows from indexes between [%s, %s] took %.2f seconds...' % (settings.SELECT_ROW_COUNT, self.id_min, self.id_max, (end - start),))


def main():
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(levelname)s] (%(threadName)-10s) %(message)s',
    )

    # Get the current minimum and maximum value of the auto_increment primary key in our test table.
    conn = settings.db_connect()
    cur = conn.cursor()
    cur.execute('SELECT id FROM ' + settings.DB_TABLE + ' ORDER BY id ASC LIMIT 1')
    id_min = cur.fetchone()[0]
    cur.execute('SELECT id FROM ' + settings.DB_TABLE + ' ORDER BY id DESC LIMIT 1')
    id_max = cur.fetchone()[0]
    cur.close()
    conn.close()

    # Start worker threads
    try:
        threads = [Worker(id_min, id_max) for i in xrange(settings.THREAD_COUNT)]
        for thread in threads:
            thread.start()

        while True:
            sleep(1)
    except (KeyboardInterrupt, SystemExit):
        for thread in threads:
            thread.stop()

if __name__ == "__main__":
    sys.exit(main())
