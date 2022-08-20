apt-get update
apt-get install -y apt-transport-https ca-certificates curl software-properties-common
apt-get install -y htop
apt-get install -y curl
#curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
#add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu/ $(lsb_release -cs) stable"
  add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu/ focal stable"
apt-get update
apt-get install -y docker-ce
usermod -aG docker robin
apt-get install -y docker-compose
systemctl restart docker.service
apt-get install -y python-dev   # for python2.x installs
apt-get install -y python3-dev  # for python3.x installs
#systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

reboot