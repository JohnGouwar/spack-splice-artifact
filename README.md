# Supporting Artifact for "Bridging the Gap Between Binary and Source Based Package Management in Spack"
## Requirements 
### Software
- `make`
- `git`
- `python>=3.13.2`

### Python packages 
Running `pip -r requirements.txt` will install all necessary python dependencies. 

### Hardware and OS 
This artifact has been tested on `x86_64` Intel CPUs running Ubuntu 22.04 and
Fedora 41. It _should_ work in other configurations, since Spack is cross-platform, 
but is untested on other platforms. 

## Running the artifact 
From a clean clone of this repository, running `make all` will do the following 
things: 
1. Clone the relevant versions of Spack for comparison (`make spacks`)
2. Create a mock buildcache of the RADIUSS software stack (`make buildcache`)
3. Gather the configurations that do not yet have output, run the experiments on
the pre-extension version of Spack, and then run the experiments on the version
of Spack with our extension (`make experiments`).
4. Recreate figures 5, 6, and 7 (`make plots`).

## Tuning the running time
There are 2 variables in `launch.sh` that can change the running time of the 
experiments `NPROCS` and `NRUNS`
- `NPROCS`: This controls the number of processes that are used to run the
experiments. In general, this has a negative linear correlation with runtime.
- `NRUNS`: This controls the number of times an experiment is ran for timing
stability.  In general, this has a positive linear correlation with the runtime. 

The original experiments from the paper were run on a 96 core machine with 
`NPROCS=72` and `NRUNS=30`. This took approximately 5 hours. 
