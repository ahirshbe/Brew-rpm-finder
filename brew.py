#!/bin/python
import subprocess
import paramiko
#  fence-agents-4.0.11-17.el7 , password="qum5net"

# SSH parameters
server = "192.0.2.13"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Copy the repo file to yum.repos directory, cleaning yum repos and installing brew
subprocess.check_call(["sudo", "cp", "/home/stack/brew.repo", "/etc/yum.repos.d/"])
subprocess.check_call(["sudo", "yum", "clean", "all"])
#subprocess.check_call(["sudo", "yum", "install", "-y", "brewkoji"])

# Using brew to locate rpm needed
agent = raw_input("Enter fence-agents or resource-agents")
rpm = raw_input("Name of the rpm")
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
        choose = int(raw_input("Enter the desired rpm number to scp for controllers"))
        if choose in file_list:
            source = file_list[choose]
            destination = str("/home/heat-admin/" + source)
            print "this is the source:  %s" % source
            ssh.connect(server, username="heat-admin")
            sftp = ssh.open_sftp()
            sftp.put(source, destination)
            sftp.close()
            ssh.close()
            break
        else:
            print "out of range"

else:
    print "Nothing found.."