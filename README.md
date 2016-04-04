# Brew-rpm-finder

The project come to simplify the following procces:

Update packages from brew
Install “brew” tool from the following repo(can be installed on fedora as well - replace “rhel” to fedora):
[rhpkg]
name=rhpkg for Fedora $releasever
baseurl=http://download.lab.bos.redhat.com/rel-eng/dist-git/rhel/$releasever/
enabled=1
gpgcheck=0
yum install -y brewkoji
brew search build resource-agents*  (grep for the version you are looking for)
brew buildinfo resource-agents-3.9.5-67.el7 <- apply the version here
make sure the Tags: match the current RHEL release we are testing against.
brew download-build --arch=x86_64 --arch=noarch resource-agents-3.9.5-67.el7

NOTE: 
All examples above are based on RHEL7.3 versions of resource-agents. for 7.2.z  you will probably need  3.9.5-54.el7.2_XXX where you should always get the highest XXX

After running the program all need to do is update the rpm:
rpm -qa | grep  resource-agents -> make sure you have the original rpm version
Rpm -Uvh resource-agents-3.9.5-67.el7.x86_64.rpm -y
rpm -qa | grep  resource-agents -> make sure you have the newer rpm version
