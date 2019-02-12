echo "RUNNING PROVISION"
ansible-playbook -v --extra-vars "$@" /provision.yml
