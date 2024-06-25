---
Title: Dear Medium,
Date: 2019-11-11
Category: Personal
Status: published
---

My blogging journey has taken me far. I started writing articles about six years ago. Things got serious after I started studying Computer Science. Among the students of my class there was a lot of chatter. The tendency was that who was unable to communicate would soon start failing exams and eventually quit. In this setting, I started writing technical articles, first on an intranet website. Later GitHub gists. Finally I made the step to host my own blog.

### Humble beginnings

The journey begins with a hosted WordPress blog. The hosting company failed to update its instances properly, almost all features were blocked for plans I could affort, and after a year I went on (and they bankrupt).

Continuing, I started hosting a static blog on GitHub pages. Using [Pelican](https://blog.getpelican.com/) and Python as the weapons of my choice, I had a blast! Need a new theme? Get them all for [free](https://github.com/getpelican/pelican) or build your own [like I did](https://github.com/dmuhs/hebe). Need more specific features tailored to your use case? The [plugin repo](https://github.com/getpelican/pelican-plugins) is enormous and gives plenty inspiration to build your own! To this day my old blog is [open-source](https://github.com/dmuhs/dmuhs.github.io/), including posts I never published anywhere else. After three beautiful years full of on-off hacking and publishing, I found it hard to "get back into the flow". Eventually I stopped maintaining the blog due to time constraints. By that time I was already working and other things were clearly more important.

## A New Hope

And along came [Medium](https://github.com/dmuhs/dmuhs.github.io/). As I started to deal more and more with blockchain technology, I started to notice that a lot of publications lived there. Registration was free, so why not give it a shot? My first impression was great. So I decided to dive in head-first and went on to copy-paste all my posts - previously written in Markdown - to their new home, converting links, embeds, etc. along the way.

Life continued. Soon I found solutions that I wanted to share with people in the software engineering community. After all, if you don't find what you're looking for online and end up doing it yourself, you should publish your approach and help out people just like yourself. Let's get writing then.

### Syntax highlighting

Quickly I realized that code snippet syntax highlighting was not natively supported. The recommended solution by the Medium team? [Embed Gists](https://help.medium.com/hc/en-us/articles/215194537-Format-text). Having implemented custom syntax highlighting logic in Pelican with both [Pygments](https://pygments.org/) and [Prism](https://prismjs.com/) in an afternoon hacking session, it boggled my mind that such a basic feature was missing.

![Image]({static}/images/screenshot-from-2019-11-11-19-24-56-1.png){: .image-process-article-image}

Because I already migrated my other content, I stuck with copy-pasting (yet again!) my previous code samples into Gists. Every. Single. One. It was frustrating but after a year of using Medium I got used to it. The feature was apparently not coming any time soon, and I got numb to the repetitive work after a while.

### The metered paywall

One day I wanted to publish yet another article when a new element caught my eye.

![Image]({static}/images/screenshot-from-2019-11-11-20-16-16.png){: .image-process-article-image}

Alright, I guess I'll activate that option. I want people to find my content after all. Even though I can't help but feel blackmailed - and I'm the author! I won't dive too much into the issue of the fruitless work of writing a blog. There are plenty approaches trying to solve this problem, each of them sufficiently complex to justify its own article on the pro and contra. But come on, Medium, there has to be a better way than this!

### My reader's experience

I do not do this for a living. My articles are fairly specific, and definitely do not have the quality of a professional writer. That said, it still fills me with joy whenever someone finds my articles helpful. It is a giving and taking, a harmony of exchanging knowledge and appreciation, enriching everyone involved in the process. Of course I care about maintaining this state, and so of course I care about how people consume my articles. Most use their mobile phone, an article found on [HackerNews](https://news.ycombinator.com/), a casual morning read on their way to work. I don't have to explain much about why I am worried about how my readers experience the things I publish. A screenshot says more than a thousand words.

![Image]({static}/images/medium-website.png){: .image-process-article-image}

"But Dominik", I hear you say, "Medium just wants you to use their app! Just use the app; things will improve!"

![Image]({static}/images/medium-app.png){: .image-process-article-image}

Dear Medium, if I actually wanted to publish my articles in the format above, I would write them on stamps. The missing features are okay, and I wholeheartedly agree that creative work and publishing should get rewarded with money. Mutilating my content and annoying my users is not a solution - it is going to drive people away from your platform and my publication alike. The key difference is that I can just move my content to greener pastures any time.

### Back to the roots

A few weeks back I started looking at other blog platforms, managed and self-hosted. [Wix](https://www.wix.com/), [Squarespace](https://www.squarespace.com/), [Ghost](https://ghost.org/), WordPress, static site generators for GitHub pages such as [Jekyll](https://jekyllrb.com/), [Hugo](https://gohugo.io/), my trusty [Pelican](https://blog.getpelican.com/), and plenty more.

Having compared the pricing/server costs and maintenance overhead, a hosted solution on WordPress was the best solution. And checking it out now, things have drastically improved over the past years! I would still never, ever, ever host WordPress myself, or even touch the [slightest piece of PHP in it](https://github.com/WordPress/WordPress), but dealing with the [hosted service](https://wordpress.com/) you will encounter neither of these issues.

So I yet again migrated my posts, configured a nice theme, made myself at home. Let's see where this chapter of my blogging journey leads me! The platforms may change, but the writing never stops.
