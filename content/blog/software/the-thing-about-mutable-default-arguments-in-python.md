---
Title: The Thing about Mutable Default Arguments in Python
Date: 2018-10-10
Category: Software
Status: published
---

Yesterday I stumbled across some code like this...

```python
def search_children(statespace, node, start_index=0, depth=0, results=[]):
    if depth < MAX_SEARCH_DEPTH:
        n_states = len(node.states)
        if n_states > start_index:
            for j in range(start_index, n_states):
                if node.states[j].get_current_instruction()['opcode'] == 'SSTORE':
                  results.append(node.states[j].get_current_instruction()['address'])
    ...
```

The semantics of the code don’t really matter here. Still spot the bug? It’s a very common Python gotcha that even experienced developers overlook from time to time. Look at the function header. The result list. Maybe a small example playing around will help here:

```python
In [9]: def append_to_list(value, l=[]):
   ...:     l.append(value)
   ...:     return l
   ...:

In [10]: append_to_list(42)
Out[10]: [42]

In [11]: append_to_list(1337)
Out[11]: [42, 1337]
```

Setting the default argument you would normally expect to have an empty list every time you enter the function. However, as StackOverflow user [skyking](https://stackoverflow.com/questions/32326777/python-default-arguments-evaluation) points out, this is not the case. Default arguments in Python are evaluated once, when the function is declared.

This means that when interpreting the `def` statement, a new list is created and exactly *that* list is then passed to the function every time it is called. Basically we’re always working on the same list pointer. This also applies to objects:

```python
In [3]: class Foo(object):
   ...:     def __init__(self, default_list=[]):
   ...:         self.my_list = default_list
   ...:     def append(self, v):
   ...:         self.my_list.append(v)
   ...:
In [4]: f = Foo()

In [5]: f.append(42)

In [6]: f.my_list
Out[6]: [42]

In [7]: f2 = Foo()

In [8]: f2.append(1337)

In [9]: f2.my_list
Out[9]: [42, 1337]
```

This fact can introduce some subtle bugs where lists contain elements that don’t belong in them as global usage of functions or objects work on the same data structure.

#### Reasons for that Behaviour

Think about it from the standpoint of a Python core developer. You could of course save a chunk of code for evaluating the default parameters. However, that code would be run with every function call if no argument is passed to it. Furthermore, someone has to manage the memory. If you evaluate your default arguments once, you can already allocate the necessary RAM they will use. Otherwise, you would also have to manage that with every default call.

You can even decide when your parameter variable is bound. An early binding (evaluated on the definition of the function/method) is the default. In scenarios where you want a late binding, simply evaluate the parameter in the function body.  If it wasn’t like that, but parameters would always be evaluated when the function is called, you would be forced to stick with that behaviour— at the cost of flexibility and performance.

The only trade-off is that users have to be conscious about this kind of power the language gives them. For sure some programmers who are used to other languages may find it unintuitive when seeing it for the first time.

#### Valid Uses

Ages ago Fredrik Lundh [wrote a decent article on this](http://effbot.org/zone/default-values.htm) where some valid uses are explained — still using some old Python syntax. Personally I find those uses lacking in readability and hard to maintain. If you need a cache, just explicitly write one and don’t use the implicit evaluation behaviour of Python. Still, it’s good knowledge! And it also mentions a pattern that is still valid today and the fix for our above-mentioned code snippet...

```python
def search_children(statespace, node, start_index=0, depth=0, results=None):
    if results is None:
        results = []
    if depth < MAX_SEARCH_DEPTH:
        n_states = len(node.states)
        if n_states > start_index:
            for j in range(start_index, n_states):
                if node.states[j].get_current_instruction()['opcode'] == 'SSTORE':
                  results.append(node.states[j].get_current_instruction()['address'])
    ...
```

Just evaluate the default parameter value in the function body. Late binding. :)
