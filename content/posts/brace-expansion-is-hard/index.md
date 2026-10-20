---
title: "Brace Expansion Is Hard"
date: 2026-07-17
categories: ["Security"]
url: "/2026/07/17/brace-expansion-is-hard"
---

**tl;dr:** If you depend on the `bracex` Python library, and there's a good chance you do but haven't noticed yet, upgrade to version `3.0`.

This writeup has moved. The full disclosure of three denial-of-service vulnerabilities in [bracex](https://github.com/facelessuser/bracex) (CVE-2026-62980, CVE-2026-62981, and CVE-2026-63185) now lives on the Kauz Security Services research site:

**[Multiple DoS Vulnerabilities in bracex](https://kauz.gmbh/research/bracex/)**

It covers how `bracex==2.6`'s `limit` parameter counted results instead of work, and how each of the three bugs exploited that gap in a different way: a long literal with no braces, a run of empty slots, and a chain of unmatched braces. All three were fixed by the maintainer within three days of disclosure.
