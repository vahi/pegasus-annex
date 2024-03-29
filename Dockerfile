FROM htcondor/mini:10.3.1-el8

#### Update Packages ####
RUN yum -y install emacs-nox telnet

#### Install Pegasus ####
RUN curl -o /etc/yum.repos.d/pegasus.repo http://download.pegasus.isi.edu/wms/download/rhel/8/pegasus.repo \
    && yum -y install pegasus

#### Set Locale ####
#ENV LC_ALL "en_US.utf-8"
ENV LANG "en_US.utf-8"

#### Add pegasus user ####
RUN useradd -s /bin/bash -m pegasus && \
    mkdir /home/pegasus/.hpc-annex && \
    chown -R pegasus:pegasus /home/pegasus 

### Copy worklfow examples ###
COPY --chown=pegasus:pegasus examples /home/pegasus/examples

#### Copy Annex Config ####
COPY config/11-annex.conf /etc/condor/config.d/11-annex.conf
COPY config/condor_config.local /etc/condor/condor_config.local


#### Create the entrypoint ####
RUN echo "#!/bin/bash" > /opt/entrypoint.sh && \
    echo "sed -i \"s/use ROLE: Execute/#use ROLE: Execute/\" /etc/condor/config.d/00-minicondor" >> /opt/entrypoint.sh && \
    echo "sed -i \"s/@CONDOR_HOST@/CONDOR_HOST = \$HOSTNAME/\" /etc/condor/condor_config.local" >> /opt/entrypoint.sh && \
    echo "sed -i \"s/@FULL_HOSTNAME@/FULL_HOSTNAME = \$HOSTNAME/\" /etc/condor/condor_config.local" >> /opt/entrypoint.sh && \
    echo "IP_ADDR=\$(ifconfig | grep inet | grep -v 127.0.0.1 | awk '{ print \$2 }')"  >> /opt/entrypoint.sh && \
    echo "sed -i \"s/@NETWORK_INTERFACE@/NETWORK_INTERFACE = \$IP_ADDR/\" /etc/condor/condor_config.local" >> /opt/entrypoint.sh && \
    echo "sed -i \"s/@TCP_FORWARDING_HOST@/TCP_FORWARDING_HOST = \$HOST_IP/\" /etc/condor/condor_config.local" >> /opt/entrypoint.sh && \
    echo 'PORT="${COLLECTOR_PORT:-9618}"' >> /opt/entrypoint.sh && \
    echo "sed -i \"s/@COLLECTOR_PORT@/COLLECTOR_PORT = \$PORT/\" /etc/condor/condor_config.local" >> /opt/entrypoint.sh && \
    echo "/usr/sbin/condor_master" >> /opt/entrypoint.sh && \
    echo "/bin/sleep 10" >> /opt/entrypoint.sh && \
    echo "cp /etc/condor/passwords.d/POOL /etc/condor/passwords.d/hpcannex-key" >> /opt/entrypoint.sh && \
    echo "while true; do sleep 60; done" >> /opt/entrypoint.sh && \
    chmod 755 /opt/entrypoint.sh 

ENTRYPOINT [ "/opt/entrypoint.sh" ]

#### Switch to pegasus user ####
#USER pegasus

#ENV HOME "/home/pegasus"
#WORKDIR /home/pegasus