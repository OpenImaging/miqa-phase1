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

# Install girder
RUN mkdir /miqa
COPY server /miqa/server
RUN pip install /miqa/server
RUN girder build --static-root /static

# Install miqa
COPY client /miqa/client
WORKDIR /miqa/client
RUN npm install \
    && npm run build \
    && mv dist /usr/share/girder/static/miqa

ENTRYPOINT ["girder", "serve"]