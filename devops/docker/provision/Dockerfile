FROM node:10.15.3-stretch

EXPOSE 8080

RUN apt-get update && apt-get install -qy \
    gcc \
    libpython3-dev \
    git \
    libsasl2-dev && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py

# See http://click.pocoo.org/5/python3/#python-3-surrogate-handling for more detail on
# why this is necessary.
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# above is largely duplicated from https://github.com/girder/girder/blob/master/Dockerfile.py3


# Install ansible girder-client for provisioning
RUN git clone https://github.com/girder/girder.git girder_repo \
    && pip install ansible \
    && ansible-galaxy install -p /girder_repo/devops/ansible/roles girder.girder
RUN pip install girder_client
COPY devops/docker/provision/provision.yml /provision.yml
COPY devops/docker/provision/inventory /etc/ansible/hosts
ENV ANSIBLE_LIBRARY=/girder_repo/devops/ansible/roles/girder.girder/library

COPY devops/docker/provision/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["bash", "/entrypoint.sh"]
