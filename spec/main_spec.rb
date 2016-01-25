require 'spec_helper'

describe "Elastic Search setup" do
  describe package('oracle-java8-installer') do
    it { should be_installed }
  end

  describe package('elasticsearch') do
    it { should be_installed.with_version(ANSIBLE_VARS.fetch('elasticsearch_version', 'FAIL')) }
  end

  describe service('elasticsearch') do
    it { should be_enabled }
  end

  describe file('/etc/elasticsearch/elasticsearch.yml') do
    it { should be_file }
    if ANSIBLE_VARS.fetch('elasticsearch_cluster_name', false)
      its(:content) { should include("cluster.name: #{ANSIBLE_VARS.fetch('elasticsearch_cluster_name', 'FAIL')}") }
    end
    if ANSIBLE_VARS.fetch('elasticsearch_groovy_sandbox', false)
      its(:content) { should include("script.groovy.sandbox.enabled: true") }
    end
    ANSIBLE_VARS.fetch('elasticsearch_allowed_scripting_actions', []).each do |action|
      its(:content) { should include("script.#{action}: on") }
    end
  end

  describe file('/etc/elasticsearch/logging.yml') do
    it { should be_file }
  end

  describe file('/usr/share/elasticsearch/plugins/') do
    it { should be_directory }
  end

  describe file('/etc/elasticsearch/elasticsearch.yml') do
    its(:content) { should include("cluster.name: #{ANSIBLE_VARS.fetch('elasticsearch_cluster_name', 'FAIL')}") }
  end

  context "AWS plugin vars set", if: ANSIBLE_VARS.fetch('elasticsearch_plugin_aws_version', false) do
    describe file('/usr/share/elasticsearch/plugins/cloud-aws/') do
      it { should be_directory }
    end

    describe file('/etc/elasticsearch/elasticsearch.yml') do
      its(:content) { should include("discovery.type: ec2") }
      its(:content) { should include("cloud.aws.access_key: '#{ANSIBLE_VARS.fetch('elasticsearch_plugin_aws_access_key', 'FAIL')}'") }
      its(:content) { should include("cloud.aws.secret_key: '#{ANSIBLE_VARS.fetch('elasticsearch_plugin_aws_secret_key', 'FAIL')}'") }
    end
  end

  context "No AWS plugin vars set", if: !ANSIBLE_VARS.fetch('elasticsearch_plugin_aws_version', false) do
    describe file('/usr/share/elasticsearch/plugins/cloud-aws/') do
      it { should_not exist }
    end

    describe file('/etc/elasticsearch/elasticsearch.yml') do
      its(:content) { should_not include("discovery.type: ec2") }
    end
  end
end
