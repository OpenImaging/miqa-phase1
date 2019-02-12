FROM girder/girder:latest-py3

# Install girder
RUN mkdir /miqa
COPY miqa_server /miqa/miqa_server
RUN pip install /miqa/miqa_server \
    && girder build

# Install miqa
COPY client /miqa/client
WORKDIR /miqa/client
RUN npm install \
    && npm run build \
    && mv dist /usr/share/girder/static/miqa
