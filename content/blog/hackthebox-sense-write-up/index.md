---
Title: HackTheBox Sense
Date: 2018-03-01
Category: Challenges
Status: published
---

Sense was a HackTheBox machine that really tested my patience during the enumeration phase. It is a box designed around the popular [pfSense](https://www.pfsense.org/) firewall. Let's dive in! Firstly, we start our usual standard nmap scan:

```sh
Starting Nmap 7.60 ( https://nmap.org ) at 2018-02-27 19:44 CET
Nmap scan report for 10.10.10.60
Host is up (0.034s latency).
Not shown: 998 filtered ports
PORT    STATE SERVICE
80/tcp  open  http
443/tcp open  https

Nmap done: 1 IP address (1 host up) scanned in 7.09 seconds
```

Checking out port 80 with the browser automatically redirects us to HTTPS on port 443. We also have an information leak about the server technology in the responses, but that information does not lead us to a viable exploit.

![Image]({attach}839386424.png){: .image-process-article-image}

Checking out port 443 in the browser (and skipping the security warning), we are greeted by the pfSense login panel:

![Image]({attach}1399367803.png){: .image-process-article-image}

A quick Google search confirms that pfSense is a rather popular open-source firewall solution, and its Github repository seems to be almost entirely written in PHP. This is valuable information already. The default credentials for pfSense are admin:pfsense, but that does not lead us anywhere. There are also no robots.txt or .htaccess files on the server. The login page's source code contains some interesting-looking Javascript code around CSRF token generation. Still, we chose not to follow that lead as the box is isolated, and CSRF seemed a bit over the top. This leads us to conclude that we should try some directory enumeration using dirbuster. Using a standard wordlist for files, we almost immediately get some hits, among them an XML-RPC endpoint:

![Image]({attach}1555399102.png){: .image-process-article-image}

XML-RPC is interesting because it can allow us to trigger commands on the server that can cause it to leak credentials or other helpful information. We can use the following payload to list all methods:

```xml
<methodCall>
  <methodName>system.listMethods</methodName>
  <params></params>
</methodCall>
```

![Image]({attach}85609701.png){: .image-process-article-image}

We can get even broader descriptions for each method using the `system.methodHelp` call. For that, I wrote a little enumeration script to get a good overview:

```python
import xmlrpc.client
import xml
import ssl


s = xmlrpc.client.ServerProxy(
    "https://10.10.10.60/xmlrpc.php",
    context=ssl._create_unverified_context(),
    verbose=False
)

rpc_methods = s.system.listMethods()

print("Available methods are:")
for method in rpc_methods:
    print(method)
    print("-"*len(method))

    # get method signature
    try:
        signature = s.system.methodSignature(method)
    except xml.parsers.expat.ExpatError:
        signature = "Parsing Error"
    print(signature, "\n")

    # get method docstring if exists
    try:
        docstring = s.system.methodHelp(method)
    except xml.parsers.expat.ExpatError:
        docstring = "Parsing error"
    print(docstring, "\n")
```

The total output is quite long, but the most exciting methods that were returned along with their explanations deal with remote code execution:

```
pfsense.exec_shell
------------------
[['boolean', 'string', 'string']]
XMLRPC wrapper for mwexec(). This method must be called with two parameters: a string containing the local system\'s password followed by an shell command to execute.

pfsense.exec_php
----------------
[['boolean', 'string', 'string']]
XMLRPC wrapper for eval(). This method must be called with two parameters: a string containing the local system\'s password followed by the PHP code to evaluate.
```

Now the bummer: Playing around with these RPC calls turns out to be a dead-end. Both methods are password-protected, so we're back to square one.

![Image]({attach}300989342.png){: .image-process-article-image}

I wanted to include this tangent here because, especially for beginners tackling more demanding challenges, it is essential to realize that diving into rabbit holes with nothing to show after a few hours is a natural part of CTFs. Just keep on trying! And so will we here.Going through some more dirbuster results, we stumble across the `changelog.txt` file.

![Image]({attach}2008781597.png){: .image-process-article-image}

Instead of the standard pfSense changelog we may have expected to see, we find a notice left behind by the server administrators. This proves that some non-standard files are present on the server, and we need to look harder for the next clue. After changing the wordlist and poking around, even more, we find the `system-users.txt` file.

![Image]({attach}1765722213.png){: .image-process-article-image}

As it turns out, *company defaults* refer to the default pfSense password - as we have already read earlier from the deployment guide. So finally, with `rohit:pfsense` we can gain access.

![Image]({attach}1225847803.png){: .image-process-article-image}

From here, we look around the dashboard and find that there is the option to customize our feed with widgets. Nothing seems to work when playing around with their user input fields, especially the file uploads. One thing we can now determine precisely, however, is the software version: `pfSense 2.1.3`.I am unsure whether I followed the challenge creator's intention here, but my frustration with enumeration drove me to search for a shortcut in Metasploit.So a search in Metasploit shows a small selection of exploits, one of them being a remote code execution for pfSense `<= 2.3.1_1`:

```
Description:
  pfSense, a free BSD based open source firewall distribution, version
  <= 2.3.1_1 contains a remote command execution vulnerability post
  authentication in the system_groupmanager.php page. Verified against
  2.2.6 and 2.3.
```

We can now easily pop a Meterpreter session on the server by filling out all relevant parameters. pfSense is running as
root, so we have immediately landed at our goal. From here, we can get the user and root flags.

![Image]({attach}1150353223.png){: .image-process-article-image}
