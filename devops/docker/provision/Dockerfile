FROM girder/girder@sha256:bf3120735964da3801da2117800579119c7f2a4a271b86a5d91aea36123a32b6

WORKDIR /
# Install ansible girder-client for provisioning
RUN git clone https://github.com/girder/girder.git girder_repo \
    && pip install girder_repo/clients/python/ \
    && pip install ansible \
    && ansible-galaxy install -p /girder_repo/devops/ansible/roles girder.girder
COPY devops/docker/provision/provision.yml /provision.yml
COPY devops/docker/provision/inventory /etc/ansible/hosts
ENV ANSIBLE_LIBRARY=/girder_repo/devops/ansible/roles/girder.girder/library

COPY devops/docker/provision/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["bash", "/entrypoint.sh"]
