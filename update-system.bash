
apt-get clean
apt-get update -y
apt-get upgrade -y
apt-get dist-upgrade -y
apt autoremove -y

echo
cat /var/run/reboot-required

