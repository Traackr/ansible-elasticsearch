# -*- mode: ruby -*-
# vi: set ft=ruby :
$script = <<SCRIPT
cd /vagrant
ansible-playbook -i vagrant-inventory.ini vagrant-main.yml -vv
SCRIPT
# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "ubuntu/trusty64"
  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.cpus = 2
  end

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network :private_network, ip: "192.168.33.10"
  config.vm.network :private_network, ip: "192.168.111.10"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"
  config.vm.synced_folder '.', '/vagrant', mount_options: ["dmode=777,fmode=666"]

  config.vm.provision :shell,
    :keep_color => true,
    :path => "setup.sh"
  

  config.vm.provision :shell,
   :keep_color => true,
   :inline =>  $script
  
end