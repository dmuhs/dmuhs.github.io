---
Title: HackTheBox Nibbles
Date: 2018-02-26
Category: Challenges
Status: published
---

Nibbles was one of the first machines I broke on HTB. It is a relatively simple machine that requires a little bit of reconnaissance and leads you to a (hopefully) easy win by letting you poke around the website. Let's dive in!First, we run a quick port scan: `nmap -sS 10.10.10.75 -oX htb-nibbles.xml`, which gives us the following result:

```
Starting Nmap 7.60 ( https://nmap.org ) at 2018-02-26 18:58 CET
Nmap scan report for 10.10.10.75
Host is up (0.056s latency).
Not shown: 998 closed ports
PORT STATE SERVICE
22/tcp open ssh
80/tcp open http

Nmap done: 1 IP address (1 host up) scanned in 0.80 seconds
```

Access on port 80 gives us the following view:

![Image]({static}/images/1806645511.png){: .image-process-article-image}

Making sure that there is nothing hidden in the background, I also check the site's source code:

![Image]({static}/images/1037093379.png){: .image-process-article-image}

Frequently dependencies such as JS files, images, or even artifacts such as comments and weird spacing can give hints about the underlying server technology, template engine, or plain interesting paths. Latter is the case here.

![Image]({static}/images/580770439.png){: .image-process-article-image}

Looking at the source, the category section looks as follows:

```html
<section id="sidebar">
  <div class="plugin-box plugin_categories">
    <h3 class="plugin-title">Categories</h3>
    <ul>
      <li class="category"><a href="/nibbleblog/index.php?controller=blog&amp;action=view&amp;category=uncategorised">Uncategorised</a></li>
      <li class="category"><a href="/nibbleblog/index.php?controller=blog&amp;action=view&amp;category=music">Music</a></li>
      <li class="category"><a href="/nibbleblog/index.php?controller=blog&amp;action=view&amp;category=videos">Videos</a></li>
    </ul>



  <div class="plugin-box plugin_hello_world">
    <h3 class="plugin-title">Hello world</h3>
    <p>Hello world</p>



  <div class="plugin-box plugin_latest_posts">
    <h3 class="plugin-title">Latest posts</h3>
    <ul></ul>



  <div class="plugin-box plugin_my_image">
    <h3 class="plugin-title">shell</h3>
    <ul>
      <li><img alt="" src="/nibbleblog/content/private/plugins/my_image/image.jpg" /></li>
    </ul>



  <div class="plugin-box plugin_pages">
    <h3 class="plugin-title">Pages</h3>
    <ul>
      <li><a href="/nibbleblog/">Home</a></li>
    </ul>



</section>
```

Immediately catching the eye here are the `index.php` parameters. Trying some common and invalid values for the `controller `and `action `parameters does not yield any interesting errors, though. Another interesting area of the sidebar is the `shell` section, which contains an image that cannot be loaded. The path gives us valuable information on other locations on the server, so we navigate to `http://10.10.10.75/nibbleblog/content/`.

![Image]({static}/images/1938176137.png){: .image-process-article-image}

Under the public uploads, we find Nibbles here!

![Image]({static}/images/1294528947.png){: .image-process-article-image}

Not to get distracted, we look into the `private` directory:

![Image]({static}/images/1674765847.png){: .image-process-article-image}

Some interesting PHP and XML files live in this directory. Most notably, `users.xml` is in here, which contains useful credentials:

```xml
<users>
    <user username="admin">
        <id type="integer">0</id>
        <session_fail_count type="integer">0</session_fail_count>
        <session_date type="integer">1519673845</session_date>
    </user>
    <blacklist type="string" ip="10.10.10.1">
        <date type="integer">1512964659</date>
        <fail_count type="integer">1</fail_count>
    </blacklist>
    ...
</users>
```

We now know that there is a user admin. We also learned that a blocklist is used, which apparently prevents brute-force attacks on the login panel. Other XML files deliver exciting data such as author names and mail addresses, but none of this data can be used to escalate our privileges in the system at hand. The data gets noted down (for later use in case we get desperate), and we continue. After some trial and error, we stumble on another interesting directory: `/admin/`.

![Image]({static}/images/1992171821.png){: .image-process-article-image}

Looking through the code, we try to keep an eye out for anything regarding authentication, because our immediate goal is gaining access to the backend. In the login controller, we find the following code:

```php
<a href="'.HTML_PATH_ROOT.'admin.php?controller=user&action=send_forgot">'.$_LANG['FORGOT_PASSWORD'].'</a>');
```

This leads us to the `admin.php` file.

![Image]({static}/images/1174725683.png){: .image-process-article-image}

Great! From the `users.xml` file we already know that there is a user called admin. Bruteforce is out of the question because of the apparent blocklist, but surprise surprise, our first password guess, `nibbles`, Lets us into the backend.

![Image]({static}/images/817327426.png){: .image-process-article-image}

We can also see the futile login attempts of other users on this instance. Browsing around, a notable plugin is the file upload in the image module.

![Image]({static}/images/1935705407.png){: .image-process-article-image}

The direct line of thought is to upload a webshell and gain server-level privileges on the target. To try out this hypothesis, we use one of Kali's default webshells located under `/usr/share/webshells/php/`. Specifically, we want a reverse connection if any other HTB user manages to get server access and decides to be funny and delete our files.

![Image]({static}/images/297254721.png){: .image-process-article-image}

The upload works nicely, and apparently, there are no file header or even basic extension checks in place. This means we can start our listener with `nc -vlnp 49387` and navigate to `http://10.10.10.75/nibbleblog/content/private/plugins/my_image/image.php` to trigger our reverse shell. This gives us server-level privileges as the `nibbler` user on the host machine:

![Image]({static}/images/1713163671.png){: .image-process-article-image}

From here, we can already grab the user flag:

![Image]({static}/images/1112613588.png){: .image-process-article-image}

In the user's home directory, we find an exciting archive as well:

![Image]({static}/images/1529892635.png){: .image-process-article-image}

Of course, the monitor script is of interest here. It contains some commands surfacing system information:

![Image]({static}/images/1726806268.png){: .image-process-article-image}

A quick check with `sudo -l` shows that the exact path the extracted script is under has generic sudo permissions. Checking the permissions on the monitor.sh file shows that we can write to it! This effectively gives us the ability to execute arbitrary commands as the root user, and quickly append `cat /root/root.txt` to the end of the file and run it with `sudo personal/stuff/monitor.sh` provides us with the root flag.
