---
Title: The "Pythonic" GOTO
Date: 2015-06-15
Category: Software
Status: published
---

Nope, I'm not going to join the goto war. Even though it's shunned among developers, there are still some situations where it makes sense. A good friend of mine with a background in C recently came to me with a very simple problem that still made him scratch his head when he tried to express it in Python. The problem broke down to comparing three lists to find an element that meets a special criterion. His basic naive concept looked something like this in pseudo-code:

```
match = False
for elem1 in list1 do {
    for elem2 in list2 do {
        for elem3 in list3 do {
            if condition(elem1, elem2, elem3) then {
                match = True
                break
            }
        }
        if match then {
            break
        }
    }
    if match then {
        break
    }
}
```

Of course with his programming background he immediately made the remark that this problem is a good example for using goto in low-level code. You save some comparisons when breaking out of several nested loops. I probably don't have the knowledge to join the debate on this - especially when it comes to embedded programming! But what I know are high-level languages and how to deal with this kind of problem there. It's pretty easy as most languages offer a construct that acts like goto, but just in a certain frame and without the risk of writing spaghetti code. I'm talking about **exceptions**. I think they're highly underrated, because they're not only tools for error-handling and increasing the fault-tolerance of your software. You can also use them to easily modify your regular control flow. A sample implementation of the above pseudo-code in Python using exceptions and sets (to remove duplicates) would look as follows:

```python
class MatchFound(Exception):
    pass

def some_check(list1, list2, list3):
    try:
        for elem1 in set(list1):
            for elem2 in set(list2):
                for elem3 in set(list3):
                    if condition(elem1, elem2, elem3):
                        raise MatchFound()
    except MatchFound:
        return True  # Found something!
    return False  # Nothing here
```

In the particular case of said friend it was even easier. The criterion would just have to be a check that returns `True` if all elements were equal. That's a one-liner in Python. The naive implementation using sets:

```python
bool(set(list1).intersection(list2).intersection(list3))
```

Doesn't look pythonic enough? Alright, let's compress it some more:

```python
bool(set(list1) & set(list2) & set(list3))
```
