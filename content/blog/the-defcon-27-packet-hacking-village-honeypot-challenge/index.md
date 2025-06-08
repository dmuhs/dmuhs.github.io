---
Title: The DEFCON 27 Packet Hacking Village Honeypot Challenge
Date: 2019-08-15
Category: Challenges
Status: published
---

This year marks the first time I got to attend DEFCON Las Vegas — one of the largest hacker conferences in the world. There are a plethora of things to discover and try out. The talks can be streamed later, but the workshops and spontaneous gatherings? A challenge that caught my eye was the honeypot challenge in the packet hacking village. The setting is simple: You gain access to an SSH honeypot. In there you find challenges to solve and gather the credentials to the next one. The goal was to escalate through five machines and gain the secret passphrase.

### What makes this CTF so special?

I have dealt quite a bit with application and network security. A lot of Capture the Flag (CTF) competitions are aimed at professionals to confront them with corner cases or brainteasers in their area of expertise. DEFCON is a very inclusive conference, however. This particular challenge was aimed at people who only brought along basic knowledge of the Linux command line.So without further ado, let’s check out the challenges of this year and how to solve them!

### Challenge 0: Getting Attention

The first challenge was to find out about the CTF. There were some funny notes left on the toilets of that floor. It just had an IP address and the word "challenge" written on it. Hell yeah, I’m in!

### Challenge 1: Warmup

SSH’ing into the box is easy — any password is accepted. Inside we find a readme file:

```sh
# cat readme.txt
R3JlYXQgam9iISBKdXN0IGdldHRpbmcgd2FybWVkIHVwIHRob3VnaC4uLgoxNzIuMjAuODcuOQpwYXNzd29yZDogbHVsbGFieSA=
```

Checking out the characters, that looks remarkably like base64 encoding. So let’s try that:

```sh
$ echo 'R3JlYXQgam9iISBKdXN0IGdldHRpbmcgd2FybWVkIHVwIHRob3VnaC4uLgoxNzIuMjAuODcuOQpwYXNzd29yZDogbHVsbGFieSA=' | base64 -d
```

Great job! Just getting warmed up though…

```
172.20.87.9
password: lullaby
```

Alright, that only took some seconds. Just getting warmed up, though.

### Challenge 2: Refreshing on Encodings

On to the next challenge:

```sh
ssh root@172.20.87.9
```

We find a single text file in the root directory, nothing else:

> Due to its use in writing Germanic, Romance, and other languages first in Europe and then in other parts of the world,
> and due to its use in Romanizing writing of other languages, it has become widespread (see Latin script). It is also
> used officially in China (separate from its ideographic writing) and has been adopted by Baltic and some Ｓlavic
> states.
>
> The Latin alphabet evolved from the visually similar Cumaean Greek version of the Greek alphabet, which was itself
> descended from the Phoenician abjad, which in turn derived from Egyptian hieroglyphics. The Etruscans, who ruled early
> Rome, adopted the Cumaean Greek alphabet, which was modified over time to become the Etruscan alphabet, which was in
> turn adopted and further modified by the Romans to produce the Latin alphabet.
>
> During the Middle Αges, the Latin alphabet was used (sometimes with modifications) for writing Romance languages,
> which are direct descendants of Latin, as well as Celtic, Germanic, Baltic, and some Slavic languages. With the age of
> colonialism and Christian evangelism, the Latin script spread beyond Europe, coming into use for writing indigenous
> American, Australian, Austronesian, Austroasiatic, and African languages. More recently, linguists have also tended to
> prefer the Latin script or the International Phonetic Alphabet (itself largely based on the Latin script) when
> transcribing or creating written standards for non-European languages, such as the African ｒeference alphabet.

Note the weird spaces in e.g. the last sentence (i.e. the first *r* in *reference*)? These are characters in a different encoding. The text seems to be an hommage to the latin encoding, but the characters standing out are different. Looking at the hexdump of the file, things become more obvious. Non-ASCII characters stand out, because they are not printed by default:

```sh
# xxd latin.txt
00000000: 4475 6520 746f 2069 7473 2075 7365 2069 Due to its use i
00000010: 6e20 7772 6974 696e 6720 4765 726d 616e n writing German
00000020: 6963 2c20 526f 6d61 6e63 652c 2061 6e64 ic, Romance, and
00000030: 206f 7468 6572 206c 616e 6775 6167 6573 other languages
00000040: 2066 6972 7374 2069 6e20 4575 726f 7065 first in Europe
00000050: 2061 6e64 2074 6865 6e20 696e 206f 7468 and then in oth
00000060: 6572 2070 6172 7473 206f 6620 7468 6520 er parts of the
00000070: 776f 726c 642c 2061 6e64 2064 7565 2074 world, and due t
00000080: 6f20 6974 7320 7573 6520 696e 2052 6f6d o its use in Rom
00000090: 616e 697a 696e 6720 7772 6974 696e 6720 anizing writing
000000a0: 6f66 206f 7468 6572 206c 616e 6775 6167 of other languag
000000b0: 6573 2c20 6974 2068 6173 2062 6563 6f6d es, it has becom
000000c0: 6520 7769 6465 7370 7265 6164 2028 7365 e widespread (se
000000d0: 6520 4c61 7469 6e20 7363 7269 7074 292e e Latin script).
000000e0: 2049 7420 6973 2061 6c73 6f20 7573 6564 It is also used
000000f0: 206f 6666 6963 6961 6c6c 7920 696e 2043 officially in C
00000100: 6869 6e61 2028 7365 7061 7261 7465 2066 hina (separate f
00000110: 726f 6d20 6974 7320 6964 656f 6772 6170 rom its ideograp
00000120: 6869 6320 7772 6974 696e 6729 2061 6e64 hic writing) and
00000130: 2068 6173 2062 6565 6e20 6164 6f70 7465 has been adopte
00000140: 6420 6279 2042 616c 7469 6320 616e 6420 d by Baltic and
00000150: 736f 6d65 20ef bcb3 6c61 7669 6320 7374 some …lavic st
00000160: 6174 6573 2e0a 0aef bcb4 6865 204c 6174 ates……he Lat
```

When combining the characters, we get the word "**star**". Trying this as the password for the next IP, `172.20.87.10`, we get in.

### Challenge 3: Image Encoding with a Twist

Logging into the next machine, we find only an image in the root directory. The tools we need are not on the honeypot, so we have to analyze the image locally. Due to a minor issue experienced by the CTF organizers, it turned out that the image could not be downloaded with standard tools like `scp` or `rsync`. No problem! We can exfiltrate the image as text. Just base64-encode it, copy the text to the local machine:

```sh
# base64 rainbow.jpg
/9j/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQECAQEBAQEBAgICAgICAgICAgICAgID
AwMDAwMDAwMDAwMDAwP/2wBDAQEBAQEBAQIBAQIDAgICAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMD
AwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwP/wAARCAPwB38DAREAAhEBAxEB/8QAHwAAAAcBAQEB
AQAAAAAAAAAAAgMEBQYHCAEJAAoL/8QARRAAAgICAgEDBAEEAQMDAAEVAQIDBAUGBxESABMhCBQi
MRUWIzJBURckQgkzYSVScRg0Q2KBkSZTcic1RLE2gqFjotH/xAAeAQABBQEBAQEBAAAAAAAAAAAE
AQIDBQYHAAgJCv/EAE8RAAICAAQEBAMHBAIBAgIAFwECAxEABBIhBTFB8BMiUWEGcYEUMpGhscHR
I0Lh8QcVUiQzYggWckOCFyU0kqIJU7Jjc8ImNYPSVIST8v/aAAwDAQACEQMRAD8A3nKBF4SSCH2B
4gCOWGRPcjV4RYjQErFKyp10wIY9MSB61reg5/Lp2cUl3vgmXxCIskaIviteYoFlH5kSNLAyEF/F
iC/6Ut5H4A7Ed4ksDY4IsyIPlvJ4oXJSuyx/CdiGMCP8VUdntVYdn/5I79Jpvfvv3x4teCJYo+3i
UPCXhcSxzqkjCxITI0qQAE9kFlDeQAYjoHo+k0/l339cMVyTp3N3z/Hv/OCZWYPBNG8oETmvOrFZ
…
```

... and locally decode it again:

```sh
echo '/9j/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB…' | base64 -d
```

Looking at the meta data in the image viewer of our choice, we find nothing of interest. But there’s a commonly used catch in CTFs when it comes to images: **Steganography**! With `steghide` we can detect stego-encoded data:

```sh
$ steghide info rainbow.jpg
"8Rm7xlH.jpg":
 format: jpeg
 capacity: 127.4 KB
Try to get information about embedded data ? (y/n) y
Enter passphrase:
 embedded file "steganopayload24853.txt":
 size: 34.0 Byte
 encrypted: rijndael-128, cbc
 compressed: yes
```

Bingo! Assuming the encryption key is weak, we can launch a dictionary attack to find the keys. For this, I’ll use `stregcracker` and a very common wordlist:

```sh
$ stegcracker rainbow.jpg WordLists/rockyou.txt
```

As soon as we found the key, we can find the contents in the same directory as `rainbow.jpg.out`:

```sh
$ cat rainbow.jpg.out
172.20.87.11
Password: LemonDrops
```

On to the next one!

### Challenge 4: A Morse Brainteaser

In server #4 we find two kinds of directories, `_sheep`, `.sheep` (easily to be overseen), and a `readme.txt`:

```sh
# cat readme.txt
I   herd   you control the sheep

A ._
B _...
C _._.
D _..
E .
F .._.
G __.
H ....
I ..
J .___
K _._
L ._..
M __
N _.
O ___
P .__.
Q __._
R ._.
S ...
T _
U .._
V ..._
W .__
X _.._
Y _.__
Z __..
```

Punny. This took me a while to figure out, especially because `find` or `grep` are not available on the server. Both `sheep` directories have further nested directories, with `readme` files sporadically popping up. Enumerating all by hand would take far too much time. Bash scripting is not an option, because the server prevents us from using that, too. The path to the solution (literally) becomes obvious when you try to morse-encode the most obvious word in the first readme:

```sh
HERD = .... . ._. _..
```

Following the path, respectively entering `_sheep` for *da’s*, and `.sheep` for *dit’s*, we find a readme with the solution:

```sh
$ cat ~/.sheep/.sheep/.sheep/.sheep/.sheep/.sheep/_sheep/.sheep/_sheep/.sheep/.sheep/readme.txt
172.20.87.12
Password: ChimneyTops
```

### Challenge 5: Weird Custom Encryption

In the fifth and last server, we find a single text file again:

```sh
# cat roundrobin.txt
tlChuoeln lgbarlbauyte ubslitaratdris o lnaesrm,eo nya o dugr’rovopeus p p crohofiv memnnee dyyi outumor-psssei lzbfel dua,e wmbooirsrttdhlsyy lciuhnlasllealcbetyni gvseotrra orau nsld e omsroo nlo vmdenrdio vptoshr eoc uhfsii mfbntiehry d rsto ouipnnsd !tb
hlYeuo euo rrb diferirdn sao lfl ucPllalusaesb eyir sis:nt ea"srb lilunee m tobhnie r ddgrseo"np
usNs o cwSh iigamoln ietayo ottfoh pets h Weba lltukhetr hubrsiohru dgfsha mlWiuollrylk as(bhTyou prssdt iasdrta aelf)ef.m otBnal budlerebo ipirsnd sct hhaierm enp eaoycn kete otop fsh atbchlkeui enf geb wiv ritdlhslr aulgsuehl l(gaiebfny e yrsoatu a’irrn e l tenhmoeot n A tmdhereroripecs a ascl.hr ieTmahndeeyyy) htaaonvpdes nbballmuueee , t bhoiarrt d bssl oulneug l!
```

Checking out the character distribution, all looks like normal plain English:

```sh
E 61× 9.81%
O 50× 8.04%
R 48× 7.72%
L 47× 7.56%
S 45× 7.23%
T 41× 6.59%
A 40× 6.43%
I 37× 5.95%
N 35× 5.63%
U 33× 5.31%
H 29× 4.66%
B 26× 4.18%
D 25× 4.02%
Y 19× 3.05%
M 17× 2.73%
P 15× 2.41%
F 13× 2.09%
C 13× 2.09%
G 10× 1.61%
V 7× 1.13%
W 5× 0.8%
K 4× 0.64%
X 1× 0.16%
Z 1× 0.16%
```

Trying out all rotation cyphers, we don’t have any success. Maybe it’s Vigenère. We can find out with the Kasiski test:

```
Repeated sequences:
AES IRS EUO UOE
```

Analysing repeated length:

```sh
2 letter:3
4 letter:2
3 letter:1
5 letter:1
8 letter:1
10 letter:1
11 letter:1
```

This also does not look very promising. The last thing in my repository of knowledge about classical cryptography is permutation ciphers. Playing around with the ciphertext under certain assumtions (in this case I assumed that the word *Congratulations* is in there, based on the capital C we see in the first line), we can assemble the word with offsets 3, 6, 9, 12, …Got it. It’s a permutation with even offsets, probably wrapping around the text. I wrote a little Python script to do that for me:

```python
ciphertext = """tlChuoeln lgbarlbauyte ubslitaratdris o lnaesrm,eo nya o dugr'rovopeus p p crohofiv memnnee dyyi outumor-psssei lzbfel dua,e wmbooirsrttdhlsyy lciuhnlasllealcbetyni gvseotrra orau nsld e omsroo nlo vmdenrdio vptoshr eoc uhfsii mfbntiehry d rsto ouipnnsd !tb
hlYeuo euo rrb diferirdn sao lfl ucPllalusaesb eyir sis:nt ea"srb lilunee m tobhnie r ddgrseo"np
usNs o cwSh iigamoln ietayo ottfoh pets h Weba lltukhetr hubrsiohru dgfsha mlWiuollrylk as(bhTyou prssdt iasdrta aelf)ef.m otBnal budlerebo ipirsnd sct hhaierm enp eaoycn kete otop fsh atbchlkeui enf geb wiv ritdlhslr aulgsuehl l(gaiebfny e yrsoatu a'irrn e l tenhmoeot n A tmdhereroripecs a ascl.hr ieTmahndeeyyy) htaaonvpdes nbballmuueee , t bhoiarrt d bssl oulneug l!"""

i = 0
res = ""

while True:
 res += ciphertext[i % len(ciphertext)]
 if len(res) == len(ciphertext):
 break
 i += 3

print(res)
```

It’s not the prettiest, but gets the job done. The decoded ciphertext:

```
the bluebirds are a group of medium-sized, mostly insectivorous or omnivorous birds in the order of Passerines in the genus Sialia of the thrush family (Turdidae). Bluebirds are one of the few thrush genera in the Americas. They have blue, or blue
Congratulations, you’ve proven yourself a worthy challenger and solved the fifth round!
Your final clue is: "blue birds"
Now go to the Walkthrough Workshops staff table in the packet hacking village (if you’re not there already) and name that song!lullaby star lemon drops chimney tops blue birds lullaby star lemon drops chimney tops blue birds lullaby star lemon drops chimney tops blue birds lullaby star lemon drops chimney tops blue birds lullaby star lemon drops chimney tops blue birds lul
```

The song we’re searching for here is of course the timeless classic "Over the Rainbow" by Judy Garland. Now it becomes
apparent that the previous passwords all were related to that song as well. Nice work!

### In a Nutshell

People who have already done some simpler CTFs wouldn’t be stunned by these challenges. However, the breadth of the possible audience is what makes these challenges so nice. Anyone could crack these challenges by using their brain and Google for the basic cryptographic challenges. Personally, each server gave me a nice brainteaser to keep my mind busy with while I was exploring DEFCON, meeting awesome people, and hacking with colleagues.A lot of thanks goes to [Ryan Mitchell](https://medium.com/u/bebb98d5c168) for coming up with the cool challenges and exchanging new ideas after the contest. Keep up the great work!
