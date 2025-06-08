---
Title: HackTheBox fs0sciety
Date: 2018-10-20
Category: Challenges
Status: published
---

fs0ciety is yet another low-hanging fruit among the HackTheBox challenges. It's great for beginners who want to test their process for cracking password-protected zip files and recognition of various encodings.For that, we will use `fcrackzip `- simply for the reason that it has been around for ages and ships with Kali by default. I have sourced my wordlist from [here](https://github.com/berzerk0/Probable-Wordlists). Let's fire up the program:

![Image]({attach}35226399.png){: .image-process-article-image}

Unzipping the file with the password `justdoit`: `unzip -P justdoit fsociety.zip`; We find an interesting file containing credentials:

![Image]({attach}1448780629.png){: .image-process-article-image}

The equals sign at the end is a classic indicator for base64 encoding, so we attempt to decode the text that way:

![Image]({attach}756388261.png){: .image-process-article-image}

.. which leaves us with something that looks like binary-encoded ASCII characters. Decoding that online gives us the flag:

![Image]({attach}716221509.png){: .image-process-article-image}
