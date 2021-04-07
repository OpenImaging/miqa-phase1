FROM node:10.24.0-buster

EXPOSE 8080

RUN apt-get update && apt-get install -qy \
    gcc \
    libpython3-dev \
    python3-pip \
    git \
    libsasl2-dev && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

# See http://click.pocoo.org/5/python3/#python-3-surrogate-handling for more detail on
# why this is necessary.
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# above is largely duplicated from https://github.com/girder/girder/blob/master/Dockerfile.py3

ARG GIRDER_API_ROOT=/api/v1
ARG GIRDER_STATIC_PUBLIC_PATH=/static

RUN echo "[server]\n\
api_root = \"${GIRDER_API_ROOT}\"\n\
static_public_path = \"${GIRDER_STATIC_PUBLIC_PATH}\"\n"\
>> /etc/girder.cfg

# Install girder
RUN mkdir /miqa
COPY server/ /miqa/server/
RUN pip3 install /miqa/server
RUN girder build

# Install miqa
COPY client /miqa/client
WORKDIR /miqa/client
RUN npm install \
    && npm run build \
    && mv dist /usr/share/girder/static/miqa

# Add sample data
COPY sample_data /miqa/sample_data
RUN sed -i 's/~//g' /miqa/sample_data/sample.json

RUN git clone https://github.com/girder/girder.git girder_repo \
    && pip3 install ansible \
    && ansible-galaxy install -p /girder_repo/devops/ansible/roles girder.girder
RUN pip3 install girder_client
COPY devops/docker/provision.yml /provision.yml
COPY devops/docker/inventory /etc/ansible/hosts
ENV ANSIBLE_LIBRARY=/girder_repo/devops/ansible/roles/girder.girder/library

COPY devops/docker/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["bash", "/entrypoint.sh"]