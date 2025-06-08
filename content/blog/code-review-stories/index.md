---
Title: A Code Review Story
Date: 2019-07-28
Category: Software
Status: published
---

This is the first post of a sporadic series where we will dive into the weeds of more complex Python code review samples. I will take (slightly modified) real-world code samples, explain some common mistakes that have been made, and how we can improve things. Let’s jump right in!

In this scenario, we have a component that is supposed to handle artifacts containing log messages. It is structured as an object implementing a pipeline of various sanitization and postprocessing tasks. Among a ton of other things, there is the `groom_logs` method, which is static, and fulfills the task of validating and deduplicating the log list of a given artifact.

```python
class MyLogHandler:
    ...
    @staticmethod
    def groom_logs(my_artifact):
        log_list = my_artifact.get("logs")
        if log_list is None:
            return

        def is_valid(log_entry):
            if log_entry.get("level") not in ("info", "warning", "error"):
                return False
            if "message" not in log_entry.keys():
                return False
            return True

        def remove_duplicates(log_list: List[Dict[Any, Any]]):
            # taken from https://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python
            seen = set()
            new_l = []
            for d in log_list:
                t = tuple(d.items())
                if t not in seen:
                    seen.add(t)
                    new_l.append(d)

            return new_l

        logs = remove_duplicates(logs)
        logs = [entry for entry in logs if is_valid(entry)]
        return logs
```

### A few good things first

The encapsulation for log message sanitization was nice in the overall program's context. The methods were separated nicely, code from external resources was marked and things worked all in all. Let's not forget to tailor some nice things into the review text. That keeps up morale and maintains a constructive atmosphere where good engineering is not taken for granted and possibly overlooked!

### Nested function definitions

The functions `is_valid` and `remove_duplicates` exist inside the `groom_logs` method. It is clear that the developer noticed, that these definitions are only needed inside the method, so it was a natural decision to include them in exactly that scope. The advantage is, that this avoids cluttering the overall namespace. This decision sacrifices two other properties however: Readability and testability.

*Reading* the method code for the first time, you start out in line 5. We get the data, we check for emptiness, so far so good. In line 9 we have to switch the context to a helper method, validating the message dictionary itself. Continuing to line 16, we switch context to how duplicate dictionaries are removed from a list (while preserving the order). In line 28, we finally are back to our main log grooming method, where we make use of the previously defined functions.

*Testing* the method code can be easy in integration tests. However, how would we unit test `is_valid` or `remove_duplicates` ? There is no easy way to reach these functions, so testing them as smallest possible units is not feasible. We’re bound to testing the overall log grooming method, which is rather complex. This increases the chance of us missing an edge case in our test scenarios and not finding a bug.

An easy fix here is to simply pull the functions out of the class. This has the advantage that the overall `MyLogHandler` object only contains methods that are relevant to its main business logic. Otherwise, with many static method definitions inside, it might be hard to distinguish between helper methods and actual processing entry points. If the number of module-level helper functions becomes too large, there might be an opportunity to create a helper submodule. This was out of scope here, however, so here is version two:

```python
def is_valid_log_entry(log_entry):
    if log_entry.get("level") not in ("info", "warning", "error"):
        return False
    if "message" not in log_entry.keys():
        return False
    return Truedef remove_duplicate_logs(log_list: List[Dict[Any, Any]]):
    # taken from https://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python
    seen = set()
    new_l = []
    for d in log_list:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_l.append(d)

    return new_lclass MyLogHandler:
    @staticmethod
    def groom_logs(my_artifact):
        log_list = my_artifact.get("logs")
        if log_list is None:
            return

        logs = remove_duplicates(logs)
        logs = [entry for entry in logs if is_valid(entry)]
        return logs
```

### The minor things

Now for the nitpicking. It’s the timeless classics that never get old in code reviews (and regularly are committed by myself as well):

1. Inconsistent type hints
2. Missing docstrings
3. The validation function can be made more concise

These don’t require a lot of explanation, so I’ll leave you just with the slightly nicer validation function:

```python
def is_valid_log_entry(entry):
    level_valid = entry.get("level") in ("info", "warning", "error")
    message_valid = type(entry.get("message")) == str
    return all((level_valid, message_valid))
```

This has the advantage that it’s easier to add new conditions. And we actually fixed a bug, because the type of `message` was not checked before. Yay!
