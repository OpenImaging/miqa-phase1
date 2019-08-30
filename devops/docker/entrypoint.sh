# Run provisioning in the background
ansible-playbook -v --extra-vars "$2" /provision.yml &
# start girder server
girder serve --host 0.0.0.0 --database mongodb://"$1"/girder
