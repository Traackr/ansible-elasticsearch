require 'serverspec'
require 'yaml'

set :backend, :exec
#set :pre_command, 'sudo -s'

# Identifier for specs being run from inside this role
# and not from a playbook repo/location that doesn't know
# internal role params
INSIDE_ROLE=true

# Getting the ansible variables from included vars_files and
# playbook vars to be usable in the tests
vars_files = ["defaults/main.yml", "vars/main.yml"]
playbook_vars = YAML.load_file("tests/test.yml").first["vars"]

if vars_files
  ansible_vars = {}
  vars_files.each do |file|
    tmp_vars = YAML.load_file(file)
    tmp_vars.each do |k, v|
      next unless v.is_a?(String)
      v.gsub!(/{{(.+)}}/, "#{tmp_vars[$1]}")
    end
    ansible_vars.merge!(tmp_vars)
  end
  ansible_vars.merge!(playbook_vars)
end

ANSIBLE_VARS = ansible_vars
