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
  end

  describe file('/etc/elasticsearch/logging.yml') do
    it { should be_file }
  end

  describe file('/usr/share/elasticsearch/plugins/') do
    it { should be_directory }
  end

  describe file('/etc/elasticsearch/elasticsearch.yml') do
    it { should contain "cluster.name: #{ANSIBLE_VARS.fetch('elasticsearch_cluster_name', 'FAIL')}" }
  end

  context "AWS plugin vars set", if: ANSIBLE_VARS.fetch('elasticsearch_plugin_aws_version', false) do
    describe file('/usr/share/elasticsearch/plugins/cloud-aws/') do
      it { should be_directory }
    end

    describe file('/etc/elasticsearch/elasticsearch.yml') do
      it { should contain "discovery.type: ec2" }
      it { should contain "cloud.aws.access_key: '#{ANSIBLE_VARS.fetch('elasticsearch_plugin_aws_access_key', 'FAIL')}'" }
      it { should contain "cloud.aws.secret_key: '#{ANSIBLE_VARS.fetch('elasticsearch_plugin_aws_secret_key', 'FAIL')}'" }
    end
  end

  context "No AWS plugin vars set", if: !ANSIBLE_VARS.fetch('elasticsearch_plugin_aws_version', false) do
    describe file('/usr/share/elasticsearch/plugins/cloud-aws/') do
      it { should_not exist }
    end

    describe file('/etc/elasticsearch/elasticsearch.yml') do
      it { should_not contain "discovery.type: ec2" }
    end
  end
end
