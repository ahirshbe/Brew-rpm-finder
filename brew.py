#!/bin/python
import subprocess

# Copy the repo file to yum.repos directory, cleaning yum repos and installing brew
subprocess.check_call(["cp", "/root/untitled3/brew.repo", "/etc/yum.repos.d/"])
subprocess.check_call(["yum", "clean", "all"])
#subprocess.check_call(["yum", "install", "-y", "brewkoji"])

# Using brew to locate rpm needed
agents = raw_input("Enter fence-agents or resource-agents")+"*"
rpm = raw_input("Name of the rpm")
builds = subprocess.check_output(["brew", "search", "build", agents])
if rpm.lower() in builds.lower().split():
    print "Build found.. downloading"
    subprocess.check_call(["brew", "download-build", "--arch=x86_64", "--arch=noarch", rpm])
else:
    print "Nothing found.."