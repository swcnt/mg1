
## ATTEMPT 3: IMPLEMENT CHANGES FROM MEETING 2
## Optional Debug mode, aggregate data, make queue stable, a lot more debug/check features

import numpy as np
import math

from scipy.stats import expon, erlang, norm, lognorm, gamma, weibull_min

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

def erlangdist(i=1):
    return erlang.rvs(scale=i)

def test(arrival_scale,size_scale):
    lam = 1/arrival_scale # LAMBDA, frequency of arrivals
    mu = 1/size_scale # MU, service time rate parameter
    # try to calculate from base formula
    ES = 1/mu # Mean service time
    ES2 = 2/(mu**2) 
    rho = lam * ES
    EofT = (lam * ES2)/(2*(1-rho)) + ES # Same as 1/(mu - lambda) in exponential
    EofN = EofT * lam
    return EofN, EofT
# Begin simulation, arrival_rate = lambda, service_parameter = mu

def simulate(num_servers=1,num_jobs=100000,arrival_rate = 0.8, service_parameter = 1,size_dist = "exponential"):
    num_completions = 0
    EPSILON = 1e-8
    INFINITY = float('inf')
    total_response = 0.0
    time = 0.0
    queue = []
    total_length = 0
    num_arrivals = 0
    total_response_time = 0
    arr_scale = 1/arrival_rate
    size_scale = 1/service_parameter

    ## Determine how to sample service times. in MG1, arrivals are exponential
    def arrival(s, distr):
        if distr == "erlang":
            return erlang.rvs(scale=s)
        elif distr == "uniform":
            return s
        elif distr == "normal":
            return abs(norm.rvs(scale=s))
        elif distr == "lognormal":
            return lognorm.rvs(scale=s,s=1) #s is shape parameter
        elif distr == "gamma":
            return gamma.rvs(scale=s,s=2)
        elif distr == "weibull":
            return weibull_min.rvs(scale=s,c=2)
        else:
            return expon.rvs(scale=s)


    # Are we debugging or flying free?
    debug = input("Press enter to run normally, or enter anything for debug mode")
    debug = True if len(debug)>0 else False

    # Distribution is exponential, use expon.rvs() to make a randon variable
    next_arrival_time = exdist(arr_scale)
    
    # 3/13/2025: important - need to update time here because a job is "arriving"
    time += next_arrival_time


    # make first job, add to queue
    queue.append(job(next_arrival_time,arrival(s=size_scale,distr=size_dist)))

    # begin the race between next job finishing and next arrival

    next_completion_time = queue[0].rem_size + time
    next_arrival_time = exdist(arr_scale) + time
    if debug:
        print(f"First job should complete at {next_completion_time}, arrived at {queue[0].arrival_time} with size {queue[0].rem_size}")

    while num_completions < num_jobs:
        if debug:
            _ = input("continue? ")

        #Determine how long it takes for an event + what happens
        timestep = min(next_completion_time-time, next_arrival_time-time)
        was_arrival = next_arrival_time < next_completion_time
        
        # Time moves on
        time += timestep
        if debug:
            print(f"Time is {time}.")
        
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
            #### Metrics

            total_length += len(queue)
            num_arrivals += 1

            # If a job got here, get a new next arrival time add it
            next_arrival_time = time + exdist(arr_scale)
            # This job arrives immediately, because its next arrival time was set before.
            queue.append(job(time,arrival(s=size_scale,distr=size_dist)))
            if debug:
                print(f"Job found at time {time} with size {queue[-1].rem_size}")
        #Check and remove jobs
        for ii,thing in enumerate(queue):
            if queue:
                if queue[ii].rem_size <= EPSILON:
                    done = queue.pop(ii)
                    num_completions += 1
                    if debug:
                        print(f"Job completed at time {time}, arrival time was {done.arrival_time}")

                    ## Metric: response time
                    if not time >= done.arrival_time:
                        print(f"ERROR: time is {time} arrival was {done.arrival_time}")
                    assert(time >= done.arrival_time)
                    total_response_time += time - done.arrival_time
                    if debug:
                        print(f"Adding {total_response_time} to total, job started at {done.arrival_time}")


        if queue:
            next_completion_time = time + queue[0].rem_size

    # Return metrics
    mean_queue_length = total_length / num_arrivals
    mean_response_time = total_response_time / num_completions
    #Run tests

    
    if size_dist == "exponential":
        expected_mql , expected_mrt = test(arr_scale, size_scale)
        print(f"Mean length of queue is {mean_queue_length}, should be {expected_mql}")
        print(f"Mean response time for a job is {mean_response_time}, should be {expected_mrt}")


    else:
        print(f"Mean length of queue is {mean_queue_length}.")
        print(f"Mean response time for a job is {mean_response_time}.")

simulate(size_dist="weibull")
