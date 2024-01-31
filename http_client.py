"""
HTTP client simulator. It simulate a number of concurrent users and calculate the response time for each request.
"""

import requests
import time
import threading
from torch.utils.tensorboard import SummaryWriter
import sys

req_time = []
mut = threading.Lock()

if len(sys.argv) < 4:
    print('To few arguments; you need to specify 3 arguments.')
    print('Default values will be used for server_ip, no of users and think time.\n')
    swarm_master_ip = '10.2.9.108'  # ip address of the Swarm master node
    no_users = 1  # number of concurrent users sending request to the server
    think_time = 1  # the user think time (seconds) in between consequent requests
else:
    print('Default values have be overwritten.')
    swarm_master_ip = sys.argv[1]
    no_users = int(sys.argv[2])
    think_time = float(sys.argv[3])


class MyThread(threading.Thread):
    def __init__(self, name, counter):
        threading.Thread.__init__(self)
        self.threadID = counter
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + self.name + str(self.counter))
        workload(self.name + str(self.counter))


def workload(user):
    while True:
        t0 = time.time()
        requests.get('http://' + swarm_master_ip + ':8000/')
        t1 = time.time()
        mut.acquire()
        req_time.append(t1 - t0) # append resp time to list
        mut.release()
        time.sleep(think_time)
        print("Response Time for " + user + " = " + str(t1 - t0))

class VisualizerThread(threading.Thread):
    def __init__(self, logger):
        threading.Thread.__init__(self)
        self.logger = logger

    def run(self):
        print("Starting Visualizer")
        visualizer_workload(logger)


def visualizer_workload(logger):
    counter = 0
    req_time_local = None
    while True:
        mut.acquire()
        req_time_local = req_time.copy()
        mut.release()
        ave_req_time = (sum(req_time_local)/len(req_time_local)) if req_time_local else 0
        print("Average Request Time: ", ave_req_time)
        logger.add_scalar("average request time", ave_req_time, counter)
        logger.flush()
        counter += 1
        time.sleep(20)


if __name__ == "__main__":
    threads = []
    logger = SummaryWriter()
    for i in range(no_users):
        threads.append(MyThread("User", i))
    threads.append(VisualizerThread(logger))
    
    for i in range(no_users+1):
        threads[i].start()

    for i in range(no_users+1):
        threads[i].join()
    