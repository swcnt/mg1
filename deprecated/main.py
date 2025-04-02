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



# Begin simulation

def simulate(num_servers=1,num_jobs=20):
    num_completions = 0
    epsilon = 0.00000001
    total_response = 0.0
    time = 0.0
    queue = []
    # Distribution is exponential, use expon.rvs() to make a randon variable
    next_arrival_time = expon.rvs()
    
    # make first job, add to queue
    queue.append(job(next_arrival_time,expon.rvs()))
    time += next_arrival_time


    # begin the race between next job finishing and next arrival

    possible_completion_time = queue[0].rem_size + time
    next_arrival_time = expon.rvs() + time

    while num_completions < num_jobs:
       # Two options: Either another job arrives before the current one finishes,
       # or the job finishes before the next arrives.
       print(len(queue))

       if (next_arrival_time < possible_completion_time) or not queue:
           if queue:
               queue[0].rem_size -= possible_completion_time - next_arrival_time
               possible_completion_time = time + queue[0].rem_size
           queue.append(job(next_arrival_time,expon.rvs()))
           time = queue[-1].arrival_time
           

           #Determine when the next arrival is now that the current is over, then dip
           next_arrival_time = expon.rvs() + time
           print(f"New job found at time {time}")

       elif possible_completion_time < next_arrival_time:
           job_popped = False
           if queue:
               finished_job = queue.pop(0)
               job_popped = True
               time += finished_job.original_size
           
           #Determine when the next possible job completion is!
           if job_popped:
               if queue:
                   possible_completion_time = queue[0].rem_size + time
                   num_completions += 1
               else:
                   possible_completion_time = 999
               #num_completions += 1

               print(f" Job completed at time {time}")


simulate()
    
