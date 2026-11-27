---
title: "py-euvd: The EU Vulnerability Database in Python"
date: 2026-11-27
url: "/2026/11/27/py-euvd/"
---

Hello! Over the last few days, I built something! [py-euvd](https://py-euvd.spoons.fyi) is a Python library for the [EU Vulnerability Database](https://euvd.enisa.europa.eu) (EUVD), the public list of security vulnerabilities run by ENISA, the EU's cybersecurity agency. I tried to keep usage simple:

```python
from pyeuvd import EUVD

vuln = EUVD().get_vulnerability("CVE-2024-3400")
print(vuln.id, vuln.severity, vuln.exploited)  # EUVD-2024-31989 critical True
```

That's it. `pip install py-euvd`, no API key, no sign-up. You hand it a CVE ID and get the EU entry back, with its score, severity, and whether it has been exploited in the wild.

## Why Bother?

For years, almost everyone (including myself) got their vulnerability data from the CVE program, which MITRE runs on US government money. In April 2025, that contract [came within a day of running out](https://www.theregister.com/2025/04/16/cve_program_funding_save/) before it was extended at the last minute. Many people then noticed how fragile the whole setup was.

It has not become any sturdier since. CISA is the US agency that pays for the CVE program, and in February this year it was [reported to be in dire shape](https://techcrunch.com/2026/02/25/us-cybersecurity-agency-cisa-reportedly-in-dire-shape-amid-trump-cuts-and-layoffs/) after the Trump administration's cuts and layoffs. CISA has lost around a third of its staff, which, personally, is an absolute disaster. I Don't want the world's vulnerability data to depend on that one agency alone. We need alternatives.

Europe's alternative is the EUVD, which ENISA [officially launched](https://www.enisa.europa.eu/news/consult-the-european-vulnerability-database-to-enhance-your-digital-security) in May 2025, a month after the funding scare. It is big and alive. Today it holds about 431,000 entries, and roughly a thousand of them get updated every day. But a database is only as useful as it is easy to query, and the Python options I found were thin. So I built the one I wanted.

## Things I Like About It

There are a few neat things I challenged myself to implement. First and foremost, `py-euvd` uses only what ships with Python, so there is nothing else to install, audit, or keep patched. For a security tool, that felt like the right angle. The EUVD REST API uses pagination. My library abstracts that, and you can filter by vendor, product, score, or date and loop over the results. The library fetches the pages as it goes.

You can also use it synchronously or asynchronously with two clients that share the same interface. Every response is a typed Python object with real dates, not a pile of raw JSON, which I hope will make consuming them and reasoning about bugs much easier in the future.

Albeit not super common, I also tried to treat the server as something that could misbehave. So responses have a size limit, redirects are followed with care, and error messages are cleaned up before you see them. Everything is fully tested with 100% test coverage on Linux, Windows, and macOS, plus a weekly check against the real API, so I find out when ENISA sneaks in a breaking change.

Lastly, it's my first project shipped under the Apache 2.0 license. So I hope companies and public bodies can use it without a legal headache.

Searching looks like this:

```python
for vuln in euvd.iter_search(vendor="Cisco", from_score=9, limit=20):
    print(vuln.id, vuln.cve_id, vuln.base_score)
```

## Why Now?

To be frank, this should have shipped way faster. I started developing `py-euvd` in private in June 2025 but quickly got distracted because, well, I needed to earn a living. This week, I picked it back up and finished it within a few days. As always, when development goes this smoothly, I get suspicious about all the bugs I might have missed, but for now I'm happy with where it ended up, and I'll keep maintaining it.

One disclaimer, however: the library is unofficial. I am not affiliated with the ENISA or any other EU entity. I am just a humble citizen of this continent and wanted a good tool for their data.

The docs live at [py-euvd.spoons.fyi](https://py-euvd.spoons.fyi) and the code is on [GitHub](https://github.com/dmuhs/py-euvd). If you run security tooling in Europe, you will likely need this data sooner or later. Give it a try, and if something breaks, please [send me a bug report](https://github.com/dmuhs/py-euvd/issues). If you have other questions or feedback, reach out via the email in the footer of this site.

*Happy Hacking!*
