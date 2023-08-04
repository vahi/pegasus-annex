# Submitting Jobs to NERSC Perlmutter from SPIN

You can deploy this container in the SPIN cluster at NERSC, and then use it to submit Pegasus Workflows to Perlmutter. Spin is based on the Rancher orchestration system, which is built on Docker and Kubernetes.

## Before You Start

It is strongly recommended that you do the SPIN [New Users Workshop](https://www.nersc.gov/assets/Spin/SpinUp-Workshop-for-New-Users.pdf), as the deployment of this container follows the same principles.

## Accessing SPIN

The Rancher system is available at https://rancher2.spin.nersc.gov/ .

The NERSC container image registry, used in conjunction with Rancher, is available at https://registry.nersc.gov/ .

## Build and Publish Docker Container to NERSC Registry

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
