#!/bin/python
import subprocess
import paramiko
import os
from novaclient import client

# Getting controllers ip
os_username = os.environ['OS_USERNAME']
os_password = os.environ['OS_PASSWORD']
os_auth_url = os.environ['OS_AUTH_URL']
os_tenant_name = os.environ['OS_TENANT_NAME']
os_compute_api_version = os.environ['COMPUTE_API_VERSION']
servers_ip = []
nova = client.Client(os_compute_api_version, os_username, os_password, os_tenant_name, os_auth_url)

for instance in nova.servers.list():
    if instance.name.startswith("overcloud-controller"):
        servers_ip.append(instance.networks.values()[0][0])

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Copy the repo file to yum.repos directory, cleaning yum repos and installing brew
subprocess.check_call(["sudo", "cp", "/home/stack/brew.repo", "/etc/yum.repos.d/"])
subprocess.check_call(["sudo", "yum", "clean", "all"])
subprocess.check_call(["sudo", "yum", "install", "-y", "brewkoji"])

# Using brew to locate rpm needed
agent = raw_input("Enter fence-agents or resource-agents:\n")
rpm = raw_input("Name of the rpm:\n")
builds = subprocess.check_output(["brew", "search", "build", str(agent+"*")])

if rpm.lower() in builds.lower().split():
    print "Build found.. downloading"
    subprocess.check_call(["brew", "download-build", "--arch=x86_64", "--arch=noarch", rpm])
    files = subprocess.check_output(["ls"])
    file_count = 1
    file_list = {}

    for entry in files.split():
        if entry.startswith(agent):
            print "\033[92m%d. %s" % (file_count, entry)
            file_list[file_count] = entry
            file_count +=1

    # Asking for the file to be scp to the controllers ans sending it
    while True:
        choose = int(raw_input("Enter the desired rpm number to scp for controllers:\n"))
        if choose in file_list:
            source = file_list[choose]
            destination = str("/home/heat-admin/" + source)

            for server in servers_ip:
                print "\033[1;36mcopy to server %s" % server
                ssh.connect(server, username="heat-admin")
                sftp = ssh.open_sftp()
                sftp.put(source, destination)
                sftp.close()
                ssh.close()

            break
        else:
            print "\033[1;31out of range"

else:
    print "\033[1;31Nothing found.."