
## ATTEMPT 3: IMPLEMENT CHANGES FROM MEETING 2
## Optional Debug mode, aggregate data, make queue stable, a lot more debug/check features

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

def exdist(i=1):
    return expon.rvs(scale=i)

# Begin simulation

def simulate(num_servers=1,num_jobs=100000):
    num_completions = 0
    EPSILON = 1e-8
    INFINITY = float('inf')
    total_response = 0.0
    time = 0.0
    queue = []
    total_length = 0
    num_arrivals = 0
    total_response_time = 0
    arr_scale = 1.2

    # Are we debugging or flying free?
    debug = input("Press enter to run normally, or enter anything for debug mode")
    debug = True if len(debug)>0 else False

    # Distribution is exponential, use expon.rvs() to make a randon variable
    next_arrival_time = exdist(arr_scale)
    
    # make first job, add to queue
    queue.append(job(next_arrival_time,exdist()))

    # begin the race between next job finishing and next arrival

    next_completion_time = queue[0].rem_size + time
    next_arrival_time = exdist(arr_scale) + time

    while num_completions < num_jobs:
        if debug:
            _ = input("continue? ")

        #Determine how long it takes for an event + what happens
        timestep = min(next_completion_time-time, next_arrival_time-time)
        was_arrival = next_arrival_time < next_completion_time
        
        # Time moves on
        time += timestep
        if debug:
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
            next_arrival_time = time + exdist(arr_scale)
            # This job arrives immediately, because its next arrival time was set before.
            queue.append(job(time,exdist()))
            if debug:
                print(f"Job found at time {time}")

            #### Metrics

            total_length += len(queue)
            num_arrivals += 1

        #Check and remove jobs
        for ii,thing in enumerate(queue):
            if queue:
                if queue[ii].rem_size <= EPSILON:
                    done = queue.pop(ii)
                    num_completions += 1
                    if debug:
                        print(f"Job completed at time {time}")

                    ## Metric: response time
                    total_response_time += time - done.arrival_time


        if queue:
            next_completion_time = time + queue[0].rem_size

    # Return metrics
    mean_queue_length = total_length / num_arrivals
    mean_response_time = total_response_time / num_completions
    print(f"Mean length of queue is {mean_queue_length}")
    print(f"Mean response time for a job is {mean_response_time}")

simulate()
