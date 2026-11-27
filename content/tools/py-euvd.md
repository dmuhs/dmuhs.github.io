---
title: "py-euvd"
host: "py-euvd.spoons.fyi"
description: "Queries the EU's vulnerability database from Python, no API key needed."
weight: 5
---

py-euvd is a Python library for the EU Vulnerability Database, the public list of security vulnerabilities run by ENISA. It looks up an entry by its EUVD or CVE ID, searches by vendor, product, score, or date, and downloads the list of known exploited vulnerabilities. It comes with a sync and an async client, returns typed objects with real dates, and uses only the Python standard library. The database needs no API key. The library is unofficial, not affiliated with ENISA, and free to use under the Apache 2.0 license.
