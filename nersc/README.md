# Submitting Jobs to NERSC Perlmutter from SPIN

You can deploy this container in the SPIN cluster at NERSC, and then use it to submit Pegasus Workflows to Perlmutter. Spin is based on the Rancher orchestration system, which is built on Docker and Kubernetes.

## Before You Start

It is strongly recommended that you do the SPIN [New Users Workshop](https://www.nersc.gov/assets/Spin/SpinUp-Workshop-for-New-Users.pdf), as the deployment of this container follows the same principles.

## Accessing SPIN

The Rancher system is available at https://rancher2.spin.nersc.gov/ .

The NERSC container image registry, used in conjunction with Rancher, is available at https://registry.nersc.gov/ .

## Step 1. Build and Publish Docker Container to NERSC Registry

Login to  https://registry.nersc.gov/  with your NERSC credentials, and make sure you see your NERSC project in there.
If you don't see it, contact NERSC user support at nersc@servicenowservices.com

You also need to login on the command line to be able to push your container to the registry.
Provide your nesrc username and password. Note: OTP is not required for the NERSC registry.
```
docker login registry.nersc.gov
```

To build the docker containe, you need to follow the following naming convention for building the image

registry.nersc.gov/\<myproject\>/\<myimage\>:\<mytag\>

where myproject is your NERSC project number e.g. m4144.
Replace m4144 with your nersc project in commands below

```
$ cd ..
$ docker build --tag registry.nersc.gov/m4144/pegasus-annex . 
[+] Building 149.5s (14/14) FINISHED                                                                                                                ....                                     
 => naming to naming to registry.nersc.gov/m4144/pegasus-annex 
```

Push the image out to NERSC registry
```
$ docker push registry.nersc.gov/m4144/pegasus-annex
Using default tag: latest
The push refers to repository [registry.nersc.gov/m4144/pegasus-annex]
...
```
Now if you goto your web browser and login to https://registry.nersc.gov/ you will be able to see the container in the repositories tab under your project name

![NERSC Repositories Listing by Project](./images/nersc-harbor-repos.png)

## Step 2. Deploy the container into Rancher

In your webbrowser go to https://rancher2.spin.nersc.gov/dashboard/auth/login and login with your NERSC username and password.

Login to the development cluster. Recommended for testing. You can also choose to deploy it in the production cluster.
The Spin user guide has useful screenshots to help navigate the Rancher UI

### Create a namespace

In the top left menu, click on Cluster and under it click on Projects/Namespaces. 
Then click on the button, Create Namespace on the right.
In the form that comes up, give the \<nersc-username\>-pegasus-workflows as the name to the namespace.
Replace the <nersc-username> with your nersc username.

![Create Pegasus Workflows namespace](./images/rancher-create-namespace.png)

Once the namespace is created, you will see \<nersc-username\>-pegasus-workflows in your created namespaces. Click on it.

### Create a deployment
Then in the top left menu, click on Workload and under it click on Deployments.
Then click on the blue button, Create on the top right


The screenshot below lists the values to put

Note: You need to replace m4144 with your project number below.

![Create Deployment](./images/rancher-create-deployment.png)
The following is specified in the UI

**Name**

Set it to pegasus-annex . The workspace selected should be the one you just created e.g. <nersc-username>-pegasus-workflows

**Containers**

* Container Name - Set to *submithost*
* Container Image - Set to *registry.nersc.gov/m4144/pegasus-annex*
* Pull Policy - Set to *always*
* Pull Secrets - Set to *registry-nersc*

**Ports**

Now we need to create the Load Balancer controller. This allows the worker nodes on Perlmutter to connect back to our submit host container on port 3306 where we will be running the HTCondor Collector. We opt for 3306 as it is one of the default ports that NERSC allows users to expose.

* Service Type - Set to *Load Balancer*
* Name - Set to *condor*
* Private Container Port - Set to *3306*
* Protocol - Set to *TCP*
* Listening Port - Set to *3306*

**Command**

Leave the default values. No need to change anything

**Environment Variables**

We add 2 environment variables

* COLLECTOR_PORT - Set to *3306*
* HOST_IP - Set to *pegasus-annex-loadbalancer.\<nersc-username\>-pegasus-workflows.development.svc.spin.nersc.org*

**NOTE**: Replace the <nersc-username> with your nersc username.

**Service Account Name**

Set Service Account Name to default

#### Security Context

Now you need to add the security context to your submithost container
To do that Click on Security Context Under General in the submithost container menu

You add the following capabilities to your container
* CHOWN
* DAC_OVERRIDE
* FOWNER
* SETGID
* SETUID

Under Drop Capabilities, select
* ALL

The screenshot below illustrates that
![Security-Context](./images/rancher-create-deployment-security-context.png)

Now click the Blue Create button to create your deployment.

## Step 3. Login to your POD and check setup

### Check HTCondor version and see if daemons are up
Once your pod is up and running, it is worthwhile to login to your running pod. The easiest way to do that in the web-browser is to execute a shell in your pod as shown in the screenshot below.

![Execute shell into your pod](./images/rancher-pod-shell.png)

In the shell we run the following commands to check the status of your condor install

Check HTCondor Version

```
[root@pegasus-annex-58c9d46864-kd7z5 /]# su pegasus
[pegasus@pegasus-annex-58c9d46864-kd7z5 /]$ 
[pegasus@pegasus-annex-58c9d46864-kd7z5 /]$ condor_version
$CondorVersion: 10.3.1 2023-03-06 BuildID: 632991 PackageID: 10.3.1-1 $
$CondorPlatform: x86_64_AlmaLinux8 $
```

Check HTCondor Collector is running
```
[pegasus@pegasus-annex-58c9d46864-kd7z5 /]$ condor_status -collector -l | grep MyAddress
MyAddress = "<128.55.212.177:3306?addrs=128.55.212.177-3306&alias=pegasus-annex-58c9d46864-kd7z5&noUDP&sock=collector>"
```

Check if the collector is bound to the right IP. It is the IP that we set as an environment variable in the POD setup of the format ***pegasus-annex-loadbalancer.\<nersc-username\>-pegasus-workflows.development.svc.spin.nersc.org***

```
[pegasus@pegasus-annex-58c9d46864-kd7z5 /]$ condor_config_val TCP_FORWARDING_HOST
pegasus-annex-loadbalancer.vahi-pegasus-workflows.development.svc.spin.nersc.org
[pegasus@pegasus-annex-58c9d46864-kd7z5 /]$ telnet pegasus-annex-loadbalancer.vahi-pegasus-workflows.development.svc.spin.nersc.org 3306
Trying 128.55.212.177...
Connected to pegasus-annex-loadbalancer.vahi-pegasus-workflows.development.svc.spin.nersc.org.
Escape character is '^]'.
^CConnection closed by foreign host.
```
### Check connection from Perlmutter back to your POD on the load balancer IP

In this test, we logon to the perlmutter head node, and run the same telnet command as in previous step

```
corbusier:~ vahi$ ssh perlmutter.nersc.gov
...
################################################################################
                 _                 _   _
                | |               | | | |
 _ __   ___ _ __| |_ __ ___  _   _| |_| |_ ___ _ __
| '_ \ / _ \ '__| | '_ ` _ \| | | | __| __/ _ \ '__|
| |_) |  __/ |  | | | | | | | |_| | |_| ||  __/ |
| .__/ \___|_|  |_|_| |_| |_|\__,_|\__|\__\___|_|
| |
|_|
 
Welcome to perlmutter!
################################################################################
 
For all planned outages, see: https://www.nersc.gov/live-status/motd/
 
For past outages, see: https://my.nersc.gov/outagelog-cs.php/
vahi@perlmutter:login37:~> telnet pegasus-annex-loadbalancer.vahi-pegasus-workflows.development.svc.spin.nersc.org 3306
Trying 128.55.212.177...
Connected to pegasus-annex-loadbalancer.vahi-pegasus-workflows.development.svc.spin.nersc.org.
Escape character is '^]'.
^CConnection closed by foreign host.
vahi@perlmutter:login37:~> 

```

## Step 4. Run Sample Workflows

You can now switch to the main [README](../../README.md) to submit sample workflows.
