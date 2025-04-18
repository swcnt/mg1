import numpy as np
import math

from scipy.stats import expon

class job:
    def __init__(self, arrival_time, original_size):
        self.arrival_time = arrival_time
        self.original_size = original_size
        self.rem_size = original_size

# This will be MG1,FCFS

def FCFS(q_list):
    # Most simple policy, just slap the first entry in the queue into work
    # Working region is only 1
    return 0

def sample():
    return expon.rvs(scale=2)

# Begin simulation

def simulate(num_servers=1,num_jobs=100):
    num_completions = 0
    EPSILON = 1e-8
    INFINITY = float('inf')
    total_response = 0.0
    time = 0.0
    queue = []

    # Are we debugging or flying free?
    debug = input("Press enter to run normally, or enter anything for debug mode")
    debug = True if len(debug)>0 else False

    # Distribution is exponential, use expon.rvs() to make a randon variable
    next_arrival_time = expon.rvs()
    
    # make first job, add to queue
    queue.append(job(next_arrival_time,expon.rvs()))

    # begin the race between next job finishing and next arrival

    next_completion_time = queue[0].rem_size + time
    next_arrival_time = expon.rvs() + time

    while num_completions < num_jobs:
        if debug:
            _ = input("continue? ")

        #Determine how long it takes for an event + what happens
        timestep = min(next_completion_time-time, next_arrival_time-time)
        was_arrival = next_arrival_time < next_completion_time
        
        # Time moves on
        time += timestep
        print(f"Queue length is {len(queue)}")
        # print a list of job sizes
        sizes = [str(item.rem_size) for item in queue]
        for i,size in enumerate(sizes):
            sizes[i] = f"Job {i+1}: " + size

        print(sizes)
        if not queue:
            # with a high NCT, the next rotation will default to a new arrival
            next_completion_time = INFINITY
        else:
            queue[0].rem_size -= timestep

        if was_arrival:
            # If a job got here, get a new next arrival time add it
            next_arrival_time = time + expon.rvs()
            # This job arrives immediately, because its next arrival time was set before.
            queue.append(job(time,expon.rvs()))
            print(f"Job found at time {time}")

        #Check and remove jobs
        for ii,thing in enumerate(queue):
            if queue:
                if queue[ii].rem_size <= EPSILON:
                    queue.pop(ii)
                    num_completions += 1
                    print(f"Job completed at time {time}")

        if queue:
            next_completion_time = time + queue[0].rem_size


simulate()
