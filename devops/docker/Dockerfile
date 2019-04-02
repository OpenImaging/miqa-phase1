FROM girder/girder@sha256:bf3120735964da3801da2117800579119c7f2a4a271b86a5d91aea36123a32b6

# Install girder
RUN mkdir /miqa
COPY server /miqa/server
RUN pip install /miqa/server \
    && girder build

# This should be combined with above command when girder 3 fix plugin client build
RUN pip install /girder/plugins/autojoin

# Install miqa
COPY client /miqa/client
WORKDIR /miqa/client
RUN npm install \
    && npm run build \
    && mv dist /usr/share/girder/static/miqa
