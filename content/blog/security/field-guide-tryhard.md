---
Title: Field Guide Tryhard
Date: 2024-09-13
Category: Security
Status: published
---

Long story short, I got disillusioned with my previous work and its context. I started my project, the [Smart Contract Security Field Guide (SCSFG)](https://scsfg.io/) to cope with it. Here are some nice features:

- New code samples instead of the same-old code you see everyone steal over and over
- A section for hackers to give inspiration when stuck and explanations where the attack vector is clear
- A section for developers with general security guidelines, from audit preparation to running a bug bounty program
- No trackers, no ads, no shilling products, no bullshit. Just information.

In my day-to-day work, I interact with the field guide mainly through the search box, just to see whether I have written something about a certain keyword. The development recommendations are great to send to clients' dev teams if there is general uncertainty around a topic. 

I want to end this post in the same manner as the last one on the subject:

> Contact me if you have suggestions on attacks, best practices, or helpful tooling to add. After all, this is about educating a community so it can make educated decisions!

## Notes on Previous Contributions

Two years ago I wrote an article called ["Honest Attempts to Secure an Ecosystem"](./honest-attempts-to-secure-an-ecosystem.md). I wrote this blog post for two reasons. First, I wanted to hold myself accountable for improving the smart contract security best practices. Second, and more importantly, I wanted to create a memory, some kind of written artifact, of my previous work. Something to come back to one day and feel proud of, or at least learn something from. End of last year, on December 31st, 2023, I quit my job at Consensys. Nine months have passed since then, and it's time to reflect on what I have done.

My first contribution to the security best practices was in January 2022. I mainly reviewed and merged other people's pull requests. Some were excellent content additions with new information. Most of the contributions fixed a single typo, added their tools (often of dubious quality) to a list, or made trivial changes to get into the contributor list. Maybe for an easy reputation boost, I'm not sure.

At that point, my fellow auditors were happy someone took on this work. The best practices had gone quite stale since then, and when I proposed that I revamp it all, people were very supportive - and happy it wasn't them who had to go through the mess that had accumulated until then. I gave the site a new theme, split content into smaller sections, and created a long to-do list containing each section, missing content, and mistakes to fix. Along the way, I improved the site's loading performance, simplified navigation, and removed a lot of stale packages and redundant features that had accumulated. That felt nice, like a spring cleaning.

This work was chugging along for almost a year until November 2022. There, my public contributions ended. Consensys decided to increase tracking on the website and place a large banner ad in the security tools section.

![Security best practices banner ad]({static}/images/best-practices-ad.png)

This was not my choice. The best practices website had been very popular at that point despite its outdated content. People outside of the Diligence team noticed, saw an opportunity to upsell Consensys products, and went for it. A technical writer was hired behind the scenes to write a "Security Tooling Guide" with trivial bits of information. Marketing created a form to gather people's information in exchange for this guide - classic lead generation 101 stuff.

![Security best practices lead form]({static}/images/best-practices-form.png)

Again, this was not my choice. I was asked to implement these things out of the blue. I refused because this went against my ethics. To be clear, I am not against marketing per se or upselling services and products. I am, however, against turning an educational resource into a commercial one without warning and exploiting people's trust in the process. When I mentioned these points to the responsible person in a 1:1 meeting, they shrugged it off. "The decision has already been made, there is nothing I can change about it." They sent me on a wild goose chase, from one person to the next, where everyone told me they were not responsible.

Of course, I was still doing my job, security code reviews, during the day. The process stretched over weeks, then months, and was incredibly draining. Not only that, I felt genuinely hurt. The users' needs did not matter; my concerns did not matter. The most important thing was monitoring the traffic and form conversion rates. Yet another channel for yet another person to justify their salary with. At that time, I realized I didn't own the content I produced. No one cared about its correctness, quality, accessibility, or whether it violated the users' privacy. For the months after, I gave up.

One June evening in 2023, the best practices came to my mind while having some wine. Along with that, all the ideas I had put on hold. The sections I wanted to revamp and the mistakes that remained unfixed. After downing the whole bottle, I became convinced I could do a better job. So I set up a private repo, `mkdocs` with `mkdocs-material`, and basic CI. I started writing an outline with different items, then bullet points, then complete sentences. At the end of the night, the first few articles were finished.
