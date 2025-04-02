use noisy_float::prelude::*;
use rand::prelude::*;
use rand_distr::Exp;
use rand_distr::Gamma;
use std::f64::INFINITY;
/*
// statrs has mean and sampling formulas, not needed for now?
use statrs::distribution::Exp as aExp;
use statrs::distribution::Continuous as aCon;
use statrs::distribution::Gamma as aGammma;
*/

const EPSILON: f64 = 1e-8;

fn main() {
    println!("Hello, world!");
    let job_size_mu = 0.8;
    let job_size_shape = 0.5;
    let dist = Dist::Hyperexp(0.2,job_size_mu,0.5);
    let num_servers = 1;
    let num_jobs = 1000000;
    let arr_mu = 0.8;
    let seed = 2;
    let check = simulate(num_servers, num_jobs, dist, arr_mu, seed);
    println!("Metric: {}",check);
}

#[derive(Debug)]
struct Job {
    arrival_time: f64,
    original_size: f64,
    rem_size: f64,
}

// Make a distribution enum

#[derive(Debug)]
enum Dist {
    Expon(f64),
    // i know hyperexp with prob_low = 0 is just an exponential, but i wanna try this :>
    Hyperexp(f64, f64, f64),
    Gamma(f64, f64),
}

impl Dist {
    fn sample<R: Rng>(&self, rng: &mut R) -> f64 {
        match self {
            Dist::Hyperexp(low_mu, high_mu, prob_low) => {
                let mu = if *prob_low == 1.0 {
                    low_mu
                } else if rng.r#gen::<f64>() < *prob_low {
                    low_mu
                } else {
                    high_mu
                };
                Exp::new(*mu).unwrap().sample(rng)
            },
            Dist::Expon(lambda) => Exp::new(*lambda).unwrap().sample(rng),

            Dist::Gamma(k,lambda) => { 
                Gamma::new(*k, *lambda).unwrap().sample(rng)
            }
        }
    }
    fn mean(&self) -> f64 {
        use Dist::*;
        match self {
            Hyperexp(low_mu, high_mu, prob_low) => prob_low / low_mu + (1.0 - prob_low) / high_mu,
            Expon(lambda) => 1.0 / lambda,

            Gamma(k, lambda) => k / lambda,
        }
    }

    fn meansquare(&self) -> f64 {
        use Dist::*;
        match self {
            Hyperexp(low_mu, high_mu, prob_low) => (2.0/(low_mu.powf(2.0)) * prob_low) + (2.0/(high_mu.powf(2.0)) * (1.0 - prob_low)),
            Expon(lambda) => 2.0 / lambda.powf(2.0),
            Gamma(k, lambda) => (k/lambda.powf(2.0)) + (k/lambda).powf(2.0),
        }
    }
}

enum Policy {
    FCFS,
    PLCFS,
    SRPT,
}

impl Policy {
    // return whichever criterion jobs get sorted by.
    // not super used right now
    fn index(&self, job: &Job) -> f64 {
        match self {
            Policy::FCFS => job.arrival_time,
            Policy::PLCFS => -job.arrival_time,
            Policy::SRPT => job.rem_size,
        }
    }
}

fn fcfstest(arr_lambda: f64, size_dist: &Dist) {
    let avg_size = size_dist.mean();
    
    // average arrival interval
    let avg_int = 1.0 / arr_lambda;
    
    // rho -- must be less than 1 
    let rho = arr_lambda * avg_size;

    let esquare = size_dist.meansquare();

    // we have everything needed to find E[T] and E[N]
    let ET = (arr_lambda * esquare)/(2.0 * (1.0 - rho)) + avg_size;
    let EN = ET * arr_lambda;

    println!("Mean Response time is: {}, Mean Queue Length is {}",ET, EN);

}

fn simulate(num_servers: usize, num_jobs: u64, dist: Dist, arr_lambda: f64, seed: u64) -> f64 {
    let mut num_completions = 0;
    let mut queue: Vec<Job> = vec![];
    let mut total_response = 0.0;
    let mut time = 0.0;
    let mut rng = StdRng::seed_from_u64(seed);
    let arrival_dist = Exp::new(arr_lambda).unwrap();
    let mut total_work = 0.0;
    let mut num_arrivals = 0;

    // predict what outcome should be (if fcfs, i'll make it proper later):
    if true {
        fcfstest(arr_lambda, &dist);
    }

    // initialize a first job arrival
    let mut next_arrival_time = arrival_dist.sample(&mut rng);
    let mut next_completion = INFINITY;

    while num_completions < num_jobs {
        // queue.sort_by_key(|job| n64(policy.index(job)));
        // i'll test policies later once FCFS metrics are confirmed
        if false {
            println!(
                "Time is {}: | Queue: {:?} | Load: {}",
                time,
                queue,
                queue.iter().map(|job| job.rem_size).sum::<f64>()
            );
            std::io::stdin()
                .read_line(&mut String::new())
                .expect("whatever");
            // find next event (arrival or completion)
            // next_completion is NOT a time, it is a duration
        }
        let next_completion = queue
            .first()
            .map(|job| job.rem_size as f64)
            .unwrap_or(INFINITY);
        let timestep = next_completion.min(next_arrival_time - time);
        let was_arrival = timestep < next_completion;

        // time moves forward
        time += timestep;

        // a job gets worked on
        queue
            .iter_mut()
            .take(num_servers) // or just 1 for now
            .for_each(|job| job.rem_size -= timestep as f64);

        // Remove jobs that may have finished (only the first num_servers) jobs
        // in the queue need to be checked.
        // this is so smart izzy what
        // i dont know why they reverse here though

        for i in (0..num_servers.min(queue.len())).rev() {
            if queue[i].rem_size < EPSILON {
                let job = queue.remove(i);
                total_response += time - job.arrival_time;
                num_completions += 1;
            }
        }
        // if the job was an arrival, tick up the total work in the queue (sum of rem_sizes)
        // and add a new job to the queue.

        if was_arrival {
            total_work += queue.iter().map(|job| job.rem_size).sum::<f64>();
            num_arrivals += 1;
            let new_job_size = dist.sample(&mut rng);
            let new_job = Job {
                rem_size: new_job_size,
                original_size: new_job_size,
                arrival_time: time,
            };
            queue.push(new_job);
            next_arrival_time = time + arrival_dist.sample(&mut rng);
        }
    }

    // report mean queue load
    //total_work / num_arrivals as f64
    //OR report mean response time
    total_response / num_arrivals as f64
}
