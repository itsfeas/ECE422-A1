"""
HTTP client simulator. It simulate a number of concurrent users and calculate the response time for each request.
"""

import requests
import time
import threading
import sys
import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv) < 4:
    print('To few arguments; you need to specify 3 arguments.')
    print('Default values will be used for server_ip, no of users and think time.\n')
    swarm_master_ip = '10.2.9.108'  # ip address of the Swarm master node
    no_users = 1  # number of concurrent users sending request to the server
    think_time = 1  # the user think time (seconds) in between consequent requests
elif len(sys.argv) == 5:
    swarm_master_ip = sys.argv[1]
    max_users = int(sys.argv[2])
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

    def run(self):
        print("Starting " + self.name + str(self.counter))
        workload(self.name + str(self.counter))


def workload(user):
    while True:
        t0 = time.time()
        requests.get('http://' + swarm_master_ip + ':8000/')
        t1 = time.time()
        time.sleep(think_time)
        print("Response Time for " + user + " = " + str(t1 - t0))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        threads = []
        for i in range(no_users):
            threads.append(MyThread("User", i))

        for i in range(no_users):
            threads[i].start()

        for i in range(no_users):
            threads[i].join()
    else:
        # souce: https://stackoverflow.com/questions/11874767/how-do-i-plot-in-real-time-in-a-while-loop
        threads = [MyThread("User", 0)]
        plt.axis([0, 10, 0, 1])

        i = 0
        t = 0
        while i<=max_users:
            threads[i].start()
            i += 1
            threads.append(MyThread("User", i))
            y = i

            plt.scatter(t, y)
            plt.pause(0.05)
            t += 1
        while i!=0:
            threads[i].join()
            threads.pop()

            y = i
            plt.scatter(t, y)
            plt.pause(0.05)
            i -= 1
            t += 1

        plt.show()
