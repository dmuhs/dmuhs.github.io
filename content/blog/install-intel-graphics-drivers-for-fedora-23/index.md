---
Title: Install Intel Graphics Drivers for Fedora 23
Date: 2016-06-29
Category: Software
Status: published
---

This is a thing I always forget and have to look up. My Dell XPS 13 (2013) runs on an Intel HD4000 and the drivers are obviously not in the standard repos. This script pulls the (at the time of this writing) most recent driver from the repos of the *Intel Open Source Technology Centre*.

```sh
cd /tmp
wget --no-check-certificate https://download.01.org/gfx/RPM-GPG-KEY-ilg-2
sudo rpm --import RPM-GPG-KEY-ilg-2

# x86_64
wget https://download.01.org/gfx/fedora/23/x86_64/intel-linux-graphics-installer-1.4.0-23.intel20161.x86_64.rpm

sudo dnf install intel-linux-graphics-installer-1.4.0-23.intel20161.x86_64.rpm
sudo dnf upgrade

sudo intel-linux-graphics-installer
```

The installer takes a while to do its work. Just ignore all notifications of GNOME that the program is not responding. In the shell where you did the last call you can see the true progress. After the installation/ update progress a system reboot is required.

![Image]({attach}intel-linux-graphics-installer.png)</a>

Note that the release names may vary and if you get a 404 in the installer RPM, just look [here](https://download.01.org/gfx/repos/repos/repos/fedora/23/x86_64/) for the latest version and replace the link above.
