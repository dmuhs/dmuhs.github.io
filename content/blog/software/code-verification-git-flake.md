---
Title: Code Verification with Git Hooks and Flake8
Date: 2015-05-02
Category: Software
Status: published
---

We all have that special someone in our life. Someone who dares to commit and push something like this into the master-branch:

```python
import math, os, sys

def test_function(one, two,
    three, four, five):
    from test.utils import *
    print x; print y
    if two==three and (four!=five or one!=three) and (sqrt(four)==two or sqrt(two)==one):
        return math.ldexp( one, two )
    else:
        return None
```

This code would be accepted by the Python interpreter without hesitation and it will "work". However, there are many direct conflicts with the [PEP8 guidelines](https://www.python.org/dev/peps/pep-0008/). But not only that! Correcting the code with the `pep8` tool won't make it completely nice and clean. For example, PEP8 doesn't care for unused imports, variables or too complex functions. That's what you then use so-called linters for. They analyze your code and look for parts that could potentially or will cause errors.

Now, you can't really expect people who write code like this to also use style-checking tools and linters to validate their code. They'll forget anyways. There should be something sitting in their neck giving them a slight pinch every time they are about to push something bad that would stain my beautiful repository. And that's where [Git Hooks](http://git-scm.com/book/be/v2/Customizing-Git-Git-Hooks) come into play. So off we go!


#### What is it?

Git offers a plethora of hooks. Those are the files located in your `.git/hooks/` directory. They are executed every time a certain action is issued. Their usage scenarios are easily understood by their file names. They can contain any kind of code as long as they have a valid [shebang](http://en.wikipedia.org/wiki/Shebang_(Unix)) and your system knows how to deal with it. Here, we're going to focus on the *pre-commit* hook to prevent messy code from being committed. If there are any mistakes, the commit-process should be aborted and the user should be presented with an output showing the mistakes and their respective line numbers.

#### Adding functionality

For this example - to validate Python code - we'll use the [flake8](https://pypi.python.org/pypi/flake8) package, which combines the pep8 checker, [PyFlakes](https://pypi.python.org/pypi/pyflakes) (an awesome linter) and [Ned's McCabe script](https://pypi.python.org/pypi/mccabe) to calculate a complexity index. For our validation, we'll first open up `.git/hooks/pre-commit` and enter:

```bash
#!/bin/sh
flake8 .
```

Now we just have to make our hook executable and try to commit some ugly code.

```bash
chmod +x .git/hooks/pre-commit
git commit test.py -m "This should fail right away"
```

*Aaaaand...* that's it. Seriously. The output for a file that still needs correction at commit (in this example our code above) should look something like this:

```
/test.py:1:1: F401 'os' imported but unused
/test.py:1:1: F401 'sys' imported but unused
/test.py:1:12: E401 multiple imports on one line
/test.py:3:1: E302 expected 2 blank lines, found 1
/test.py:4:5: F403 'from test.utils import *' used; unable to detect undefined names
/test.py:5:12: E702 multiple statements on one line (semicolon)
/test.py:6:11: E225 missing whitespace around operator
/test.py:6:28: E225 missing whitespace around operator
/test.py:6:41: E225 missing whitespace around operator
/test.py:6:65: E225 missing whitespace around operator
/test.py:6:80: E501 line too long (89 > 79 characters)
/test.py:6:83: E225 missing whitespace around operator
/test.py:7:27: E201 whitespace after '('
/test.py:7:36: E202 whitespace before ')'
```

But not only the mistakes are shown. The commit is also prevented because flake8 creates an output and makes the hook fail, thus making the whole commit fail.

#### Portability

For future use, it should be as easy as possible for other developers to adapt this hook. The best way is to deliver it with the repository and give them a handful of commands (or an automated setup script) doing the work for them. That's why it's a good idea to deliver some kind of `pre-commit.sh` file in your repo and ask the user to force-symlink it to his default hook:

```bash
ln -sf ../../pre-commit.sh .git/hooks/pre-commit
```

The `-f` option will ignore the fact that a pre-commit hook already exists in `.git/hooks/` and delete its old contents. That's no huge loss, because by default the file is empty. When symlinking it is important to keep in mind that the first path has to be relative to the second one. That's why we're walking back two directories in our first path. Afterwards, the developer just has to make the shellscript executable again (in case it hasn't already been done) and the basic setup is good to go!

#### Further thoughts

Pre-commit hooks especially seem useful when a project grows. You could enforce unittests, style-policies and even automatically deploy once all tests have passed. Also, the hook can look for vulnerable parts in your code, e.g. a file starting with `import pdb` should probably be checked a second time before it goes into production.

#### Exceptions

Let's say you have modeled some bugs with unittests. You fixed one and want to commit your progress, because that one test is passing. But the other one prevents you from doing so, because it makes the whole hook fail every time you want to commit! No worries, just do the following:

```bash
git commit -a --no-verify -m "not completely verified"
```

The `--no-verify` flag [skips the pre-commit hook](https://www.kernel.org/pub/software/scm/git/docs/git-commit.html). But you should only tell your messy coworker once he asks you about it. Otherwise he'll only skip verification once he faces a wall of style mistakes.

#### Other hooks

But wait, there's more! This short [overview](https://www.kernel.org/pub/software/scm/git/docs/githooks.html) shows what hooks Git offers. There is huge potential in them, as they can also interact with each other and execute different checks. And the fact that they can also hold Python code means that your project could theoretically also manipulate its own hooks. That's where it gets pretty *meta*. For my student job I just started toying around with hook functionality. It's going to be interesting to see, which problems can be solved by them as the project grows and more developers jump on board.
