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
    swarm_master_ip = '10.2.7.254'  # ip address of the Swarm master node
    no_users = 1  # number of concurrent users sending request to the server
    think_time = 1  # the user think time (seconds) in between consequent requests
elif len(sys.argv) > 4:
    print('Bell Curve Mode. Default values have be overwritten.')
    swarm_master_ip = sys.argv[1]
    no_users = int(sys.argv[2])
    think_time = float(sys.argv[3])
    user_change_interval = int(sys.argv[4])
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
        self.should_run = True

    def run(self):
        print("Starting " + self.name + str(self.counter))
        self.workload(self.name + str(self.counter))

    def workload(self, user):
        while self.should_run:
            t0 = time.time()
            try:
                requests.get('http://' + swarm_master_ip + ':8000/')
            except:
                print("Request failed for", user)
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
        self.should_run = True

    def run(self):
        print("Starting Visualizer")
        self.visualizer_workload(logger)

    def visualizer_workload(self, logger):
        counter = 0
        req_time_local = None
        while self.should_run:
            mut.acquire()
            req_time_local = req_time.copy()
            mut.release()
            ave_req_time = (sum(req_time_local)/len(req_time_local)) if req_time_local else 0
            print("Average Request Time: ", ave_req_time)
            logger.add_scalar("average request time", ave_req_time, counter)
            # logger.flush()
            counter += 20
            time.sleep(20)


if __name__ == "__main__":
    threads = []
    logger = SummaryWriter()
    logger.add_scalar("average request time", 0, 0)
    if len(sys.argv) < 4:
        for i in range(no_users):
            threads.append(MyThread("User", i))
        threads.append(VisualizerThread(logger))
        
        for i in range(no_users+1):
            threads[i].start()

        for i in range(no_users+1):
            threads[i].join()
    else:
        threads.append(VisualizerThread(logger))
        threads[0].start()
        for i in range(1, no_users+1):
            threads.append(MyThread("User", i))
            threads[i].start()
            time.sleep(user_change_interval)
        time.sleep(120)
        for i in range(no_users, -1, -1):
            print("Join thread:", i)
            threads[i].should_run = False
            threads[i].join()
            threads.pop()
            time.sleep(user_change_interval)
