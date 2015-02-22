#!/usr/bin/python

import time, heapq

class pytimer:
    def __init__(self):
        self.pq = []

    def next(self):
        # Get(remove) next event from PQ.
        # Retrieve endtime.
        (endtime, evt) = heapq.heappop(self.pq)
        # If endtime in future:
        #   Sleep for required time
        sleeptime = endtime - time.time()
        if sleeptime > 0:
            time.sleep(sleeptime)
        # Execute the event
        evt.fire()

        # Enqueue same event with next endtime
        self.enqueue(evt)

    def enqueue(self, evt):
        endtime = evt.set_next_endtime()
        heapq.heappush(self.pq, (endtime, evt))


class timed_event:
    def __init__(self, name, interval):
        self.interval = interval
        self.count = 0
        self.starttime = time.time()
        self.name = name

    def set_next_endtime(self):
        count = self.count + 1
        endtime = self.starttime + self.interval * count
        while (endtime < time.time()):
            count += 1
            endtime = self.starttime + (self.interval * count)
        self.count = count
        self.endtime = endtime
        return endtime

    def fire(self):
        print "Firing event " + self.name + " at ", time.time()


