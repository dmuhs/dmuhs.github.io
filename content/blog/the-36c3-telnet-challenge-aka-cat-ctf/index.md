---
Title: 36C3 Telnet Challenge (Cat CTF)
Date: 2020-01-18
Category: Challenges
Status: published
---

This is a write-up from the 36th Chaos Communication Congress, 2019. It has been my fourth Congress. Timed shortly after Christmas, it feels like meeting a second kind of family after the holidays. Hackers from all over the world gather in Leipzig to celebrate the weirdness of our community, break technology, learn new things, and have caffeine-fuelled fun.On my initial recon walk with friends we stumbled across the following poster.

![Image]({attach}2019-12-27-11.24.14.jpg){: .image-process-article-image}

Let's find out where this is.

![Image]({attach}2019-12-27-12.52.05.jpg){: .image-process-article-image}

I walked by the Telnet booth and checked out the challenge. Some people were already gathered around a hot wire. The cat was in a glass box next to them - not waving. It was fairly easy to notice that the blinking cat eyes were transmitting Morse code. I quickly got into a chat with a great guy and together we decoded the message. It was talking about RFID and begged to help it wave again. One of the booth members was nice enough to provide us with an RFID card whose code didn't change with every transaction. That's where the journey begins.

## Step 1: Authenticating

We noticed a small RFID sensor next to the hot wire. Holding the card onto it the display started to read "RFID". The challenge: Solve the hot wire without any errors in under 60 seconds and you get the next hint. It took a couple of tries, but we ended up with a thermal printout:

![Image]({attach}2019-12-28-11.05.20.jpg){: .image-process-article-image}

The barcode encoded our username - the tag of our RFID card. The QR code points to a help page with a cryptic image:

![Image]({attach}help.png){: .image-process-article-image}

Checking on the domain, no website was being served. So `nmap` it is:

```sh
# nmap -sS -sV telnet.klartext-reden.net
Starting Nmap 7.60 ( https://nmap.org ) at 2019-12-27 14:22 CET
Nmap scan report for telnet.klartext-reden.net (151.217.79.34)
Host is up (0.0055s latency).
Other addresses for telnet.klartext-reden.net (not scanned): 2001:67c:20a1:1079:baca:3aff:fe76:9b93
Not shown: 997 filtered ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
23/tcp open  telnet  Linux telnetd
79/tcp open  finger  OpenBSD fingerd (ported to Linux)
Service Info: Host: telnet.fritz.box; OSs: Linux, Linux 4.15.0-72-generic; CPE: cpe:/o:linux:linux_kernel, cpe:/o:linux:linux_kernel:4.15.0-72-generic
```

## Step 2: Fingering

Finger. My CTF senses are tingling! It's a fairly unusual protocol which I have only come across in other competitions. Listing the users, we get the following:

```sh
# finger -l u0x046ED96A@telnet.klartext-reden.net

Welcome to Linux version 4.15.0-72-generic at telnet.fritz.box !

 14:24:05 up 20:17,  1 user,  load average: 0,05, 0,03, 0,00

Login: u0x046ED96A              Name:
Directory: /home/u0x046ED96A            Shell: /usr/local/challenge/bin/set-user-stage.py
Never logged in.
No mail.
Plan:
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,B8D5085BC87F91A3D1C351F9EFBF8420

+j7CIT5f0DF7TlGri2j4QenGnG+xtbbLV3mujc/KCUFEV7cAtA+xEriWIIvO2oqL
YbZVPtwh5BYxMKOwlFpbqnKvsB+0ldS2jkYerMqi4hAQvbApOO5bjSRYedWuASKb
lZcYMnorD <...>
-----END RSA PRIVATE KEY-----
```

The above help mentions a passphrase. It's fairly long, so brute force will not get us anywhere. But we have the charset from the help page, and sneakily another thermal printout arrived.

![Image]({attach}2019-12-28-11.05.15.jpg){: .image-process-article-image}

Charset and pattern now drastically reduced our cracking time.

## Step 3: Cracking

We fired up John and configured it to perform a mask attack on the encrypted SSH key.

```sh
# ./JohnTheRipper/run/ssh2john.py id.rsa > id.hash
# ./JohnTheRipper/run/john --mask=?1?1?1?1?1?1?1?1?1-36C3 -1=[ABCFGOo0] id.hash
Note: This format may emit false positives, so it will keep trying even after finding a
possible candidate.
Using default input encoding: UTF-8
Loaded 1 password hash (SSH [RSA/DSA/EC/OPENSSH (SSH private keys) 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 0 for all loaded hashes
Cost 2 (iteration count) is 1 for all loaded hashes
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
oABAFOC0G-36C3   (id.rsa)
1g 0:00:00:30 DONE (2019-12-27 15:31) 0.03264g/s 4380Kp/s 4380Kc/s 4380KC/s AA0000000-36C3..000000000-36C3
Session completed
```

We tried to login with the provided key and received an error that only connections from localhost are allowed to pass. Tunnelling can help here:

```sh
# ssh -i id.rsa -NfT -L 23000:127.0.0.1:23 u0x046ED96A@telnet.klartext-reden.net
```

Here we got stuck. There was no interactive shell. We moved on a stage as everyone could see on the leaderboard. In fact, we were rank 1. The pressure was on.

## Step 4: Get Moving!

Staring at the help page and a few chats for fresh ideas brought the part in the lower left to my attention. That looks quite familiar..

![Image]({attach}2019-12-27-11.23.21.jpg){: .image-process-article-image}

It's a depiction of the centre column in Hall 2! This took me longer to figure out than I'm willing to admit here. I grabbed my things and went to the described location. Nothing. I walked around the area a bit and quickly fell back to using the magic of the Congress: Everyone wants to help. I talked to people at the centre column and asked them whether they saw an unusual poster at the column. When they got up, I saw it! A small sticker at the bottom of the column.

![Image]({attach}2019-12-27-18.52.46-1.jpg){: .image-process-article-image}

This isn't the end, apparently. I opened my trusty c3nav app and headed NNW, looking at every booth in the process. Finally, I stumbled across another Telnet booth. On top of it, the next (beautifully hand-drawn) hint was taped.

![Image]({attach}2019-12-27-18.57.08-1.jpg){: .image-process-article-image}

## Step 5: Back to Work!

Staring at the hint for a while, I started to experiment in Python:

```python
In [26]: suffix = "-36C3"
In [27]: uname = "u0x046ED96A"
In [28]: m = hashlib.sha256()
In [29]: m.update(uname.lower().encode() + suffix.lower().encode())
In [30]: m.hexdigest()
Out[30]: 'e7f9e16e3836559474f6ccbd2680558a050dbb3c349333bbc113fd4226991e4e'
```

And according to the drawing, the first eight characters should be the password. Trying that:

```sh
$ telnet 127.0.0.1 23000
Trying 127.0.0.1...
Connected to 127.0.0.1.
Escape character is '^]'.
Ubuntu 18.04.3 LTS
Username: u0x046ED96A
Password:
f(Telnet, secure) = 27000f1b1711
f(Klartext, usSaUfYy) =
```

We move up another stage on the leaderboard (still leading!). But we are greeted with another cryptographic challenge that changes every time we try to authenticate. And it's time locked. Obviously we have to automate things here.A hunch and a bit of trial and error showed that it is a simple XOR on both strings. Now I needed to automatically get the result into the active session. I read up on how to automatically interact with Telnet sessions in Python and hacked up a little script.

```python
#!/usr/bin/env python3

import hashlib
import telnetlib
import re

suffix = "-36C3"
uname = "u0x046ED96A"
m = hashlib.sha256()
m.update(uname.lower().encode() + suffix.lower().encode())
pw = m.hexdigest()[:8]
challenge_regex = re.compile(r"f\(Klartext, (\w+)\)")

tn = telnetlib.Telnet("localhost", port=23000)
tn.read_until(b"Username: ")
tn.write(uname.encode('ascii') + b"\n")
tn.read_until(b"Password: ")
tn.write(pw.encode("ascii") + b"\n")
tn.read_until(b"f(Telnet, secure) = 27000f1b1711")

challenge = tn.read_until(b"=").decode("ascii")
challenge_str = challenge_regex.findall(challenge)[0]
response = "".join(["{:02x}".format(ord(a) ^ ord(b)) for a,b in zip("Klartext", challenge_str)])
tn.write(response.encode("ascii") + b"\n")
print(tn.read_all())
```

The output told me to scan my RFID badge at the hot wire station where we started. I waited for my companion to finish his Angel shift (because he was one of the awesome volunteers), and with him present I scanned the RFID card. Another thermal printout came in.

![Image]({attach}2019-12-28-11.02.46.jpg){: .image-process-article-image}

And, in under eight hours, team `OMA` solved the Telnet challenge - ranked first. The applause started with the Telnet team and quickly spread throughout the whole conference hall. We picked our shirts, and left with the satisfaction of what turned out to be a well-invested work day's time.Huge thanks go out to the [Telnet people](https://klartext-reden.net/) for organising such a fun and challenging experience, and `movatica` for being such a great partner in crime.Until next year, dear Congress! I hope all of your keys stay safe and your Tschunk doesn't run out.
