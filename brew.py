#!/bin/python
import subprocess
import paramiko
import os
from novaclient import client

def pcs_control(state,server):
    """ controlling the state of the cluster"""
    cmd = "sudo pcs cluster {} --all".format(state)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username="heat-admin")
    ssh.exec_command(cmd)
    ssh.close()

# Getting controllers ip from Nova
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

# Setting up paramiko configuration
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Stopping the cluster
print "Stopping the cluster"
pcs_control("stop",servers_ip[1])

# Copy the repo file to yum.repos directory, cleaning yum repos and installing brew
subprocess.check_call(["sudo", "cp", "/home/stack/brew.repo", "/etc/yum.repos.d/"])
subprocess.check_call(["sudo", "yum", "clean", "all"])
#subprocess.check_call(["sudo", "yum", "install", "-y", "brewkoji"])

# Asking for the rpm, using brew to locate rpm needed
while True:
    rpm = raw_input("Name of the rpm:\n")
    if rpm.startswith("fence"):
        agent = "fence-agents"
        break
    elif rpm.startswith("resource"):
        agent = "resource-agents"
        break
    else:
        print "\033[1;31rpm doesn't start with fence or resource\n"

builds = subprocess.check_output(["brew", "search", "build", str(agent+"*")])
if rpm.lower() in builds.lower().split():
    print "Build found.. downloading"
    subprocess.check_call(["brew", "download-build", "--arch=x86_64", "--arch=noarch", rpm])
    files = subprocess.check_output(["ls"])
    file_count = 1
    file_list = {}

    for entry in files.split():
        if entry.startswith(agent):
            print "\033[92m{}. {}".format(file_count, entry)
            file_list[file_count] = entry
            file_count +=1

    # Asking for the file to be scp to the controllers ans sending it
    while True:
        choose = int(raw_input("Enter the desired rpm number to scp for controllers:\n"))
        if choose in file_list:
            source = []
            source.append(file_list[choose])
            # Checking for dependencies for the rpm
            dependency = subprocess.check_output(["rpm", "-qpR", source[0]])
            entry_count = 0
            for entry in dependency.split():
                if entry.startswith(agent):
                    source.append(entry +"-"+dependency.split()[entry_count + 2]+".x86_64.rpm")
                entry_count =+1

            for server in servers_ip:
                print "\033[1;36mcopy to server {}".format(server)
                ssh.connect(server, username="heat-admin")
                sftp = ssh.open_sftp()
                for entry in source:
                    print entry
                    destination = str("/home/heat-admin/" + entry)
                    sftp.put(entry, destination)

                sftp.close()
                ssh.close()

            break
        else:
            print "\033[1;31out of range\n"

else:
    print "\033[1;31Nothing found..\n"

# Starting the cluster
print "Starting the cluster"
pcs_control("start",servers_ip[1])