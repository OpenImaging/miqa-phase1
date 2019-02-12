FROM girder/girder:latest-py3

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
