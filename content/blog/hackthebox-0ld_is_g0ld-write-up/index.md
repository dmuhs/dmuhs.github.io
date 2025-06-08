---
Title: HackTheBox 0ld_is_g0ld
Date: 2018-10-13
Category: Challenges
Status: published
---

0ld_is_g0ld is a HackTheBox challenge and a great way for beginners to familiarize themselves with PDF password cracking. If you have used Hashcat before, it's an easy win. Verifying we indeed are targeting the correct file format:

```
$ file 0ld\ is\ g0ld.pdf
0ld is g0ld.pdf: PDF document, version 1.6
```

We can extract the hash using the [pdf2hashcat.py](https://github.com/stricture/hashstack-server-plugin-hashcat/blob/12fc138d2864026765f55bb33e3d7b859eb2b48a/scrapers/pdf2hashcat.py) util script:

```
./pdf2hashcat.py 0ld\ is\ g0ld.pdf > hash.txt
```

Now all that's left is run hashcat with a (large) wordlist against the hash file and with a little bit of luck we get a
hit:

```sh
$ hashcat --force -a 0 -m 10500 hash.txt ~/Downloads/rockyou.txt
$pdf$4*4*128*-1060*1*16*5c8f37d2a45eb64e9dbbf71ca3e86861*32*9cba5cfb1c536f1384bba7458aae3f8100000000000000000000000000000000*32*702cc7ced92b595274b7918dcb6dc74bedef6ef851b4b4b5b8c88732ba4dac0c:jumanji69

Session..........: hashcat
Status...........: Cracked
Hash.Type........: PDF 1.4 - 1.6 (Acrobat 5 - 8)
Hash.Target......: $pdf$4*4*128*-1060*1*16*5c8f37d2a45eb64e9dbbf71ca3e...4dac0c
Time.Started.....: Fri Oct 12 18:39:19 2018 (1 min, 12 secs)
Time.Estimated...: Fri Oct 12 18:40:31 2018 (0 secs)
Guess.Base.......: File (/home/spoons/Downloads/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.Dev.#1.....:    94514 H/s (8.25ms)
Recovered........: 1/1 (100.00%) Digests, 1/1 (100.00%) Salts
Progress.........: 6820961/14344384 (47.55%)
Rejected.........: 1121/6820961 (0.02%)
Restore.Point....: 6816865/14344384 (47.52%)
Candidates.#1....: june261999 -> jumane
HWMon.Dev.#1.....: N/A

Started: Fri Oct 12 18:39:16 2018
Stopped: Fri Oct 12 18:40:32 2018
```

This leaves us with `jumanji69` as the password. Nice. We decrypt the PDF using the password and are presented with this:

![Image]({attach}1099778526.png){: .image-process-article-image}

Note the tiny morse code at the bottom of the page:

```
.-. .---- .--. ... .- -- ..- ...-- .-.. -- ----- .-. ... ...--
```

Decoding this with any old online tool gives us `R1PSAMU3LM0RS3`, which is the flag for this challenge.
