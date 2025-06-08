---
Title: N-wise Iteration in Python
Date: 2017-04-17
Category: Software
Status: published
---

A few hours back I stumbled into a problem where I had to perform a lookahead of n elements in a list to do some calculations. The first thought: Just take the current index and get all elements until i+n. I started writing..

```python
for i in range(len(iterable)):
---- SNAP ----
```

Stop. This is awfully unpythonic. There has to be a better way! Browsing the [itertools recipes](https://docs.python.org/3/library/itertools.html#itertools-recipes) I found the `pairwise` function:

```python
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
```

Perfect! Now I just have to adjust it to work with n iterators where the first iterator is at i, the second at i+1, etc.

```python
def nwise(iterable, n=1):
    iterators = tee(iterable, n)
    for i in range(n):
        for _ in range(i):
            next(iterators[i], None)
    return zip(*iterators)
```

There we go. Even though it works on multiple levels of the iterable, it's still memory-efficient, because [generators are awesome](http://pybit.es/generators.html). This will provide you with an output like this:

```python
In [4]: l = [1,2,3,4,5,6]

In [5]: list(nwise(l, n=3))
Out[5]: [(1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6)]
```
Note that the list call was just used to empty the generator for printing. Here's a quick one-liner that counts the times a fixed-length (*42*) sequence in a list sums up to a certain value (*1337*):

```python
sum([1 for seq in nwise(l, n=42) if sum(seq) == 1337])
```
