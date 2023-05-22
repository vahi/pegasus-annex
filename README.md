# pegasus-annex

This is a containerized setup for a workflow submit host with Pegasus + HTCondor that allows you to setup pilot jobs for your workflows using `htcondor annex` against supported HPC clusters. This workflow submit host is setup to submit jobs to a remote cluster, and does not run any compute jobs itself.

This container should be deployed on a host, where the compute nodes of the cluster to which you are submiting the jobs to can connect back to. Such a host, can be a host with a public IP or a host within the science DMZ of the HPC cluster. For example, this container can be deployed onto the Spin Cluster at NERSC to submit jobs to Perlmutter.

## Setup and Configuration

By default, this setup runs HTCondor collector daemon on port 9618 in the container, and it should bind to the same port on the HOST. The recommended way to bring up the container is using docker-compose.

 ```
 docker-compose up -d
 ```
 
 Before running the above command, make sure to set the following environmet variables
 
 * HOST_IP: the IP address of the host on which the container is running. This IP address should be accessible to the pilots.
 * COLLECTOR_PORT:  the port on which you want HTCondor collector to bind to. That is the port to which the pilots connect back to when they start on a compute node in the HPC cluster


## Example Workflow

The container is setup with a `pegasus` user, that has an examples folder in it's home directory.
