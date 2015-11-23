#!/usr/bin/env bash
export PYTHONUNBUFFERED=1
export ANSIBLE_FORCE_COLOR=1

if [ $(dpkg-query -W -f='${Status}' ansible 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
    echo "Add APT repositories"
    export DEBIAN_FRONTEND=noninteractive
    apt-get install -qq software-properties-common &> /dev/null || exit 1
    apt-add-repository ppa:ansible/ansible &> /dev/null || exit 1

    apt-get update -qq

    echo "Installing Ansible"
    apt-get install -qq ansible &> /dev/null || exit 1
    echo "Ansible installed"
fi

cd /vagrant/provisioning
#move ansible inventory hosts file into  default location
cp localhost.ini /etc/ansible/hosts
#undo executable bits on synced files since ansible gets grumpy
chmod -X /etc/ansible/hosts
ansible-playbook playbook.yml -vv