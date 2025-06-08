---
Title: Low-level Debugging of Stubborn Docker Containers
Date: 2018-09-16
Category: software
Status: published
---

A few weeks back I have started contributing to the awesome [Mythril](https://github.com/ConsenSys/mythril) project. Mythril is a security scanner for smart contracts that allows everyone to look for vulnerabilities on- and off-chain by being able to analyze raw smart contract code, as well as the actual Solidity code file. To make setting it up more easy, the devs provide a Docker container for easy deployment and use via `docker run` .

Looking for low-hanging fruits to start, I instinctively picked out an issue related to Docker, as there’s little new things about debugging containers. [Issue 479](https://github.com/ConsenSys/mythril/issues/479) described Mythril crashing with a Unicode decode error — but it was only reproducible with the Docker container:

```sh
$ sudo docker run -v $(pwd):/tmp mythril/myth -x /tmp/crash.sol
Traceback (most recent call last):
  File "/usr/local/bin/myth", line 4, in <module>
    __import__('pkg_resources').run_script('mythril==0.18.11', 'myth')
  File "/usr/lib/python3/dist-packages/pkg_resources/__init__.py", line 658, in run_script
    self.require(requires)[0].run_script(script_name, ns)
  File "/usr/lib/python3/dist-packages/pkg_resources/__init__.py", line 1438, in run_script
    exec(code, namespace, namespace)
  File "/usr/local/lib/python3.6/dist-packages/mythril-0.18.11-py3.6.egg/EGG-INFO/scripts/myth", line 9, in <module>
    mythril.interfaces.cli.main()
  File "/usr/local/lib/python3.6/dist-packages/mythril-0.18.11-py3.6.egg/mythril/interfaces/cli.py", line 212, in main
    print(outputs[args.outform])
UnicodeEncodeError: 'ascii' codec can't encode characters in position 439-447: ordinal not in range(128)
...
```

Fair enough. My first approach was to overwrite the entrypoint to `bash` to have a closer look at the file system and play around a little. The container is based on the latest `ubuntu:bionic` container. Usually applications like vi, nano, and the like are not installed. Trying `apt-update` and installing those packages resulted in a file system error. Now, how do you debug something that you can only observe in a closed environment and you have no chance (apart from the regular logging, which didn’t help in this case) to gather extra data? Rebuild the container every time? That feels wrong and takes way too much time. After doing some research I was surprised to find out that no one has written on a solution to this kind of problem, yet. It for sure must have also happened to other developers.

The trick is rather simple: Directly edit the Docker container’s file system from the host system, where the comfy dev environment is already set up. To do that, we have to know the path to the (merged) container file system. So first we run the container with a `bash` entrypoint to keep it open.

```sh
docker run -it --entrypoint bash mythril/myth
```

Then with `docker ps` we fetch the container’s ID, in this case `e70428441068` . Now we need to get to the directory where the Docker storage driver (`overlay2` by default) keeps the file system version the container ends up working on. With Docker inspect we get a ton of output, but what we want essentially boils down to this:

```sh
docker inspect -f '{{.GraphDriver.Data.MergedDir}}' e70428441068
```

Going to that path, preferably in a root shell, you’ll be able to see the container’s root. From there you can use your preferred command line editor (which of course is `vim` ) to edit the files you need. The changes will directly propagate to the running container. Insert some additional debug statements, get a better understanding of what’s going on and fix the bug.

To give some closure to the above-mentioned issue: The decode error was a result the container’s locale not being set to UTF-8, so output defaulted to ASCII. Set the environment variables, try again from bash, works. Make the appropriate changes in the `Dockerfile` , rebuild, test, [works](https://github.com/ConsenSys/mythril/pull/502). Nice.
