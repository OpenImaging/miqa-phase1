FROM node:10.24.1-buster

EXPOSE 8080

# Debian 10/Buster is archived now.
RUN set -eux; \
  printf '%s\n' \
    'deb http://archive.debian.org/debian buster main contrib non-free' \
    'deb http://archive.debian.org/debian-security buster/updates main contrib non-free' \
    'deb http://archive.debian.org/debian buster-updates main contrib non-free' \
    > /etc/apt/sources.list; \
  printf 'Acquire::Check-Valid-Until "false";\n' > /etc/apt/apt.conf.d/99archive; \
  apt-get update; \
  apt-get install -qy --no-install-recommends \
    build-essential \
    gcc \
    git \
    libffi-dev \
    libpython3-dev \
    libsasl2-dev \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel; \
  apt-get clean; \
  rm -rf /var/lib/apt/lists/*

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

# patch install
RUN python3 -m pip install --no-cache-dir --upgrade "pip<24" "setuptools<60" wheel
RUN python3 -m pip install --no-cache-dir \
    setuptools_scm==7.1.0 \
    bcrypt==3.1.0 \
    "pymongo>=3.6,<4"

# Install girder
RUN mkdir /miqa
COPY server/ /miqa/server/
RUN python3 -m pip install --no-cache-dir /miqa/server
RUN girder build

# Install miqa
COPY client /miqa/client
WORKDIR /miqa/client
RUN npm ci --no-audit --no-fund --verbose \
    && npm run build --verbose \
    && mv dist /usr/share/girder/static/miqa

# Add sample data
COPY sample_data /miqa/sample_data
RUN sed -i 's/~//g' /miqa/sample_data/sample.json

RUN git init girder_repo \
    && cd girder_repo \
    && git remote add origin https://github.com/girder/girder.git \
    && git fetch --depth 1 origin ceb7074aa20582c3716ea322cfd5755bf37f0cfb \
    && git checkout FETCH_HEAD \
    && python3 -m pip install --no-cache-dir "ansible~=2.7" \
    && ansible-galaxy install -p /girder_repo/devops/ansible/roles girder.girder
RUN pip3 install girder_client
COPY devops/docker/provision.yml /provision.yml
COPY devops/docker/inventory /etc/ansible/hosts
ENV ANSIBLE_LIBRARY=/girder_repo/devops/ansible/roles/girder.girder/library

COPY devops/docker/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["bash", "/entrypoint.sh"]
