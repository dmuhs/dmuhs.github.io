---
Title: Field Guide Tryhard
Date: 2024-09-13
Category: Security
Status: draft
---

Long story short, I got disillusioned with my previous work and the context it happened in. I started my own project, the [Smart Contract Security Field Guide (SCSFG)](https://scsfg.io/) to cope with it. Here's some nice features:

- New code samples instead of the same-old code you see everyone steal over and over
- The section for hackers is focused on code reviewers to give inspiration on what's possible and explain attacks
- No tracking, 

### Dwelling on the Past

Two years ago I wrote an article called ["Honest Attempts to Secure an Ecosystem"](./honest-attempts-to-secure-an-ecosystem.md). I wrote this blog post for two reasons. First, I wanted to hold myself accountable to improving the smart contract security best practices. Second, and more importantly, I wanted to create a memory, some kind of written artefact, of my previous work. Something to come back to one day and feel proud, or at least learn something from it. End of last year, on December 31st, 2023, I quit my job at Consensys. Nine months have passed since then and it's time to reflect on what I have done.

My first contributions to the security best practices were in January 2022. I mostly reviewed and merged other people's pull requests. Some were cool content additions with new information. Most of the contributions fixed a single typo, added their own tools (often of dubious quality) to a list, or otherwise made trivial changes to get into the contributor list. Maybe for an easy reputation boost, I'm not sure.

At that point, my fellow auditors were happy someone took on this work. The best practices had gone quite stale since then and when I proposed that I revamp it all, people were very supportive - and happy it wasn't them who had to go through the mess that had accumulated until then. I gave the site a new theme, split up content into smaller sections and created a long todo list containing each section, missing content, and mistakes to fix. Along the way I improved the site's loading performance, simplified navigation, and removed a lot of stale packages and redundant features that had accumulated. That felt really nice, like a spring cleaning.

This work was chugging along for almost a year, until November 2022. There, my public contributions end. The reason is that Consensys made the decision to increase tracking on the website, as well as a large banner ad in the security tools section.

![]({static}/images/best-practices-ad.png)

This was not my choice. The best practices website had been very popular at that point, despite its outdated content. People outside of the Diligence team noticed, saw an opportunity to upsell Consensys products, and went for it. A technical writer was hired behind the scenes to write a "Security Tooling Guide" with trivial bits of information. A form was set up to gather people's information in exchange for this guide. Classic lead generation 101 stuff.

![]({static}/images/best-practices-form.png)

Again, this was not my choice. I was asked to implement these things out of the blue. I refused with the reason that this goes against my ethics. To be clear, I am not against marketing per se, or upselling services and products. I am however against turning an educational resource into a commercial one without warning and exploiting people's trust in the process. When I brought up these points to the responsible person in a 1:1 meeting, they shrugged it off. "The decision has already been made, there is nothing I can change about it". They sent me on a wild goose chase, from one person to the next, where everyone told me they are not responsible.

Of course, I was still doing my actual job, security code reviews, during the day. The whole process stretched over weeks, then months, and was incredibly draining. Not only that, I felt genuinely hurt. The users' needs did not matter, my concerns did not matter. The most important thing was monitoring the traffic and form conversion rates. Yet another channel for yet another person to justify their salary with. At that time, I realized that I didn't own the content I produced. No one really cared about its correctness, quality, accessibility, or whether it violated the users' privacy. For the months after, I simply gave up.

One June evening in 2023, while having some wine, the best practices came to my mind. Along with that, all the ideas I had put on hold. The sections I wanted to revamp and the mistakes that remained unfixed. After downing the whole bottle, I became convinced I could do a better job. So I set up a private repo, `mkdocs` with `mkdocs-material`, and a few other things. I started writing an outline with different items, then bullet points, then full sentences. At the end of the night, five articles were written.













- mention prev post, since quit job
- corporate influence
- aim to create staight-to-the-point resource
- meant to use search, look things up
- or get new inspiration when working with particular piece of code
- furthermore developer section with more general tips around productive work with smart contracts
- also includes best practices, docs, monitoring, etc.

I have used my off-time from audits in the past months to write more about security. Especially in a nascent ecosystem like Ethereum still is, the most considerable impact can be delivered by educating people. Education has to happen in different modes of complexity, depending on the target audience:

- Developers must be educated on how previous hacks happened and how to avoid making similar mistakes in the code they
  produce.
- Business leads must be educated about the general (in-)securities of smart contracts and what can and cannot be
  expected of them.
- General users must be educated on spotting and avoiding scams while repeatedly preached to not invest any money they
  can't afford to lose. Ever.

My own contribution to the above is the [Ethereum Smart Contract Best Practices](https://consensys.github.io/smart-contract-best-practices/). When I joined [ConsenSys Diligence](https://consensys.net/diligence/), the repository already existed, and people enjoyed the content. In the rollercoaster of auditing smart contracts as the main business, little time was left to properly maintain code samples, keep best practices up to date, and polish the overall site. I intend to change that.This is a note for everyone who enjoys my technical posts to follow along as I develop the best practices. Occasionally, I also tweet about the sections I have revised previously. Contact me if you have suggestions on attacks, best practices, or helpful tooling to add. *After all, this is about educating a community so it can make educated decisions!*
