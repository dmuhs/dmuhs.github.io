---
title: "HackTheBox fs0sciety"
date: 2018-10-20
categories: ["Challenges"]
url: "/2018/10/20/hackthebox-fs0sciety.html"
---

fs0ciety is yet another low-hanging fruit among the HackTheBox challenges. It's great for beginners who want to test their process for cracking password-protected zip files and recognition of various encodings.For that, we will use `fcrackzip `- simply for the reason that it has been around for ages and ships with Kali by default. I have sourced my wordlist from [here](https://github.com/berzerk0/Probable-Wordlists). Let's fire up the program:

![Image](35226399.png)

Unzipping the file with the password `justdoit`: `unzip -P justdoit fsociety.zip`; We find an interesting file containing credentials:

![Image](1448780629.png)

The equals sign at the end is a classic indicator for base64 encoding, so we attempt to decode the text that way:

![Image](756388261.png)

.. which leaves us with something that looks like binary-encoded ASCII characters. Decoding that online gives us the flag:

![Image](716221509.png)
