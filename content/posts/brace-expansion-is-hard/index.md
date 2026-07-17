---
title: "Brace Expansion Is Hard"
date: 2026-07-17
categories: ["Security"]
url: "/2026/07/17/brace-expansion-is-hard"
---

**tl;dr:** If you depend on the `bracex` Python library, and there's a good chance you do but haven't noticed yet, upgrade to version `3.0`.

A few weeks ago, I had a shower thought about supply chain security. More precisely, I wondered which packages in the PyPI ecosystem were common transitive dependencies but often overlooked by security researchers.

Digging around, I stumbled across [bracex](https://github.com/facelessuser/bracex), a Python library for Bash-style brace expansion. You know, the feature that converts `foo{bar,baz}` into `foobar foobaz`. Since that's a fundamental functionality, it's no surprise the package is [downloaded a lot](https://pypistats.org/packages/bracex).

![`bracex` download statistics](bracex-stats.png)

Brace expansion can easily lead to a combinatoric explosion if you're not careful. `bracex==2.6` ships a `limit` parameter, which is supposed to stop a pattern from expanding into an unreasonable number of results. All three bugs below are, in one way or another, a story about it counting the wrong thing.

## CVE-2026-62980

Also [GHSA-88pj-cgpg-492r](https://github.com/facelessuser/bracex/security/advisories/GHSA-88pj-cgpg-492r). `get_literals` walks the input character by character and folds each one into the result with `squash`:

```python
result = iter([''])
...
while c:
 value = [c]
 ...
    # Squash the current set of literals.
 result = self.squash(result, value)
 c = next(i)
```

And `squash` is a generator:

```python
def squash(self, a, b):
    for x in itertools.product(a, b):
        yield ''.join(x) if isinstance(x, tuple) else x
```

Notice that it never consumes `a`. It wraps it. So parsing `"abc"` doesn't build the string `"abc"`. It builds a generator, over a generator, over a generator. Thus, N characters produce N nested generators, which only get unrolled when something finally iterates the outermost one. Every `next()` has to descend through all N stack frames. Stack depth ends up proportional to input length.

Which means this is enough:

```python
bracex.expand("a" * 4000)
```

A string with no braces in it at all, whose only correct output is itself, raises `RecursionError` once its length approaches the recursion limit. The `limit` protection never gets consulted here. For brace-free input, the parser calls `update_count(1)` exactly once at the end, because there is exactly one result. With recursion errors like this, if the application has raised its recursion limit, we can even use this to trigger a segfault and crash the interpreter.

Disclosed on June 27, 2026, and fixed on June 28, 2026, in `bracex==2.7`.

## CVE-2026-62981

Also [GHSA-q3p5-v4g2-85hm](https://github.com/facelessuser/bracex/security/advisories/GHSA-q3p5-v4g2-85hm). Normal slots in `{a,b}` are parsed by `get_literals`, which calls `update_count(1)` for each. However, an empty slot, e.g., from `,,`, a leading `,`, or a trailing `,`, takes a shortcut:

```python
elif c == ',':
    # Must be the first element in the list.
 has_comma = True
    if is_empty:
 result = itertools.chain(result, [''])
    else:
 is_empty = True
```

The empty string gets chained onto the result, and the counter is never touched. The slot exists in the output but not in the accounting. So the limit does not really apply here:

```python
>>> len(bracex.expand("-v{" + ","*5000 + "}", limit=1000))
5001
```

It also compounds, because group sizes are multiplied together:

```python
def update_count_seq(self, count: list[int]) -> None:
    self.count -= sum(count)
 prod = 1
    for c in count:
 prod *= c
    self.update_count(prod)
```

A group consisting only of empty slots reports a size of 0, which zeroes out the product for every group around it. `"x{,,}"*16` is roughly 43 million results, none of which get counted.

Even cooler, every empty slot wraps the result in another `itertools.chain`, so draining it recurses through the C stack, past the point where Python can still raise a `RecursionError`. On my standard testing machine, `"{" + ","*500000 + "}"` segfaulted instantly.

Disclosed on June 27, 2026, and fixed on June 28, 2026, in `bracex==2.7`.

## CVE-2026-63185

Also [GHSA-f5rx-pv38-28f9](https://github.com/facelessuser/bracex/security/advisories/GHSA-f5rx-pv38-28f9). This is my favorite of the three. When `get_literals` meets a `{`, it optimistically asks `get_sequence` for a group. If the string runs out before a matching `}` is observed, `get_sequence` raises `StopIteration` and the parser rewinds:

```python
elif not ignore_brace and c == '{':
    # Try and get the group
 index = i.index
    try:
 current_count = self.count
 seq = self.get_sequence(next(i), i, depth + 1)
 ...
    except StopIteration:
        # Searched to end of string
        # and still didn't find it.
 i.rewind(i.index - index)
```

The rewind puts the cursor back to just after the `{`, and the loop carries on treating it as an ordinary literal. Everything `get_sequence` just scanned gets scanned a second time. And if that remainder contains another `{`, it plays the same trick again.

Each unmatched brace therefore doubles the parse: N braces cost 2^(N-1) calls into `get_sequence`. On 2.6, `"{" * 16` invokes it 32,767 times. About 30 bytes of `{` were enough to effectively halt execution. `limit` does not really help here, because it counts results, and a failed parse does not produce any. The work never gets accounted for.

Disclosed on June 27, 2026, and fixed on June 30, 2026, in `bracex==3.0`.

## Lessons Learned

First and foremost, a big shoutout and thanks to [@facelessuser](https://github.com/facelessuser), the maintainer behind `bracex`. All findings were fixed within three days after disclosure. That deserves a lot of respect.

On a technical level, all three vulnerabilities share a theme. Resource limits were enforced by counting results. So each exploit found a way to burn resources without producing any. A long literal is one result, an empty slot is a result nobody counted, a failed parse is no result at all. The guard rail measured outputs when it should have measured work.

The other half of the theme is generators. `squash` and `itertools.chain` are cheap to stack up and expensive to drain. Code that looks like it's just assembling strings ends up accumulating stack frames. Making code lazy is great, but it comes at a cost.

If you depend on `bracex`, and there's a good chance you do but haven't noticed yet, upgrade to version `3.0`.