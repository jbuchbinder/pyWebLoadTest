#!/usr/bin/python

from Crypto.Random.random import randint
from logging import Logger
import Queue
import logging
import os.path
import sys
import threading
import time
import urllib2

logging.basicConfig(format="%(threadName)s: %(message)s",level=logging.DEBUG)
logger = logging.getLogger('pyWebLoadTest')

if (len(sys.argv) < 4):
    print "usage: %s threadPoolSize numberOfQueries fileWithUrls" % (sys.argv[0])
    exit(1)

maxThreadCount = 5
if (len(sys.argv) >= 2):
    maxThreadCount = int(sys.argv[1])

maxQueryCount = 20
if (len(sys.argv) >= 3):
    maxQueryCount = int(sys.argv[2])
    
urlFile = os.path.dirname(sys.argv[0]) + "/testUrls.txt"
if (len(sys.argv) >= 4):
    urlFile = sys.argv[3]
if (not os.path.exists(urlFile)):
    Logger.error(logger, "%s does not exist!" % (urlFile))
    exit(1)
              
totalFetchTime = 0.0
totalRequestsCompleted = 0
          
urls = []
          
queue = Queue.Queue()
          
class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
          
    def run(self):
        global logger
        global totalFetchTime
        global totalRequestsCompleted
        while True:
            #grabs host from queue
            host = self.queue.get()
            threadId = threading.current_thread
            
            #grabs urls of urls and prints first 1024 bytes of page
            beginTime = time.time()
            url = urllib2.urlopen(host)
            x = url.read(100000)
            if (not x):
                Logger.warn(logger, "[%s] No data for %s" % (threadId, host))
            endTime = time.time()

            elapsedTime = (endTime - beginTime)
             
            Logger.info(logger, "Request for %s executed in %s" % (host, elapsedTime))
            
            #signals to queue job is done
            totalRequestsCompleted += 1
            totalFetchTime += elapsedTime
            self.queue.task_done()
          
def readUrlsFromFile():
    global urlFile
    global urls
    global logger    
    for line in open(urlFile, 'r').readlines():
        line = line.rstrip("\r\n")
        Logger.debug(logger, "Loading URL %s from %s" % (line, urlFile))
        urls.append(line)
    if (len(urls) < 1):
        print "No urls were able to be loaded from %s, exiting!" % urlFile
        exit(1)

def main():
    global start
    global logger
    
    for i in range(maxThreadCount):
        Logger.debug(logger, "Starting thread #%d" % i)
        t = ThreadUrl(queue)
        t.setDaemon(True)
        t.start()
              
    #populate queue with data
    for j in range(maxQueryCount):
        Logger.debug(logger, "Populating URL #%d" % j)
        queue.put(urls[randint(0,len(urls)-1)])
           
    start = time.time()
    queue.join()

readUrlsFromFile()          
main()

Logger.info(logger, "Cumulative Query Time: %s" % totalFetchTime)
Logger.info(logger, "Total Elapsed Time: %s" % (time.time() - start))
      
