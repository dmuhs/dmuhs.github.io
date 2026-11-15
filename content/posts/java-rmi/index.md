---
title: "Java RMI and RCE"
date: 2026-11-15
categories: ["Security"]
url: "/2026/11/15/java-rmi"
---

Recently, I have learned about an interesting pattern in network-facing Java code. Like when you learn about a new word and start hearing it everywhere, this one keeps popping into my view. Java's RMI (Remote Method Invocation) is a breeding ground for remote code execution (RCE) vulnerabilities and exploiting it is less about what the target's business logic does but rather about what the JVM does on the developer's behalf, before a single line of their own code even runs.

Quick refresher. RMI lets one JVM call methods on an object living in another JVM as if it were local. A server exports an object and binds a stub into an RMI registry. A client looks that stub up and calls methods on it. The registry is just a tiny naming service, usually on a TCP port the process picks at startup. The important detail: **the registry lookup is not authenticated.** Anyone who can reach the port can enumerate the bound names and grab a working stub.

An exported interface can look as harmless as this:

```java
public interface Receiver extends Remote {
    void receive(byte[] message) throws RemoteException;
}
```

Looks remarkably unremarkable. The usual plan for `receive` is to parse those bytes in application code: validate a header, check a session, reject anything weird. The problem is that this validation lives inside the method body, and by the time the method body runs, it's already too late.

When a client invokes a remote method, the arguments travel over the wire as a Java serialized stream. The RMI runtime deserializes them with `ObjectInputStream.readObject()` and rebuilds the object graph *before* it passes the arguments to the method. So the sequence is something like this:

1. Attacker connects to the port (no auth).
2. Attacker looks up the stub (no auth).
3. Attacker calls `receive` with a payload of their choosing.
4. **The JVM deserializes that payload**, running constructors, `readObject` hooks, `hashCode`, and whatever else the object graph implies.
5. Then, if execution ever gets that far, the method body runs.

Any access check in the method happens in step 5, but The attacker's payload executed in step 4. Because deserialization happens earlier in the transport layer, no amount of validation inside `receive` can ever mitigate this.

## Exploitation

So exploitation happens in the context of step 4. From there, an attacker can, at the very least, take the service down. Java serialization can be forced to rebuild an object graph that is extremely expensive to reconstruct. The classic example is a nest of `HashSet`s that each contain the next:

```java
Set<Object> root = new HashSet<>();
Set<Object> s = root;
for (int i = 0; i < 100; i++) {
    Set<Object> a = new HashSet<>();
    Set<Object> b = new HashSet<>();
    s.add(a);
    s.add(b);
    s = a;  // keep descending down one branch
}
```

Serializing that is cheap. Deserializing it is not. Rebuilding each `HashSet` recomputes hash codes recursively, and the work doubles at every level, so a hundred levels comes out at roughly 2^100 `hashCode()` calls. A payload of a few hundred bytes keeps a CPU core at 100% more or less forever. A handful of them take the service down without it ever receiving a single valid message.

But wait, there's more! Deserialization of untrusted input has its own CWE entry (CWE-502) for a reason. If the target's classpath happens to include the wrong library, we can escalate from a simple denial of service vector to remote code execution. An example I found repeatedly was an old version of Apache Commons Collections. Tools like [ysoserial](https://github.com/frohoff/ysoserial) are also really good for automating this work. They build gadget chains out of classes that are already on the classpath, linking their `readObject` side effects until the last one starts a process. The mechanism is easier to see with a generated payload. The command below produces a serialized object that, when deserialized, runs `touch /tmp/pwned` on the target:

```bash
java -jar ysoserial.jar CommonsCollections6 'touch /tmp/pwned' > payload.bin
```

The object inside `payload.bin` is not a command object. It is an ordinary-looking `Map` whose entries wire up a chain of library classes. Deserializing it walks that chain, and the final link reduces to something like this:

```java
Runtime.getRuntime().exec(command);  // command comes from the payload
```

Feeding `payload.bin` to the `receive` method from earlier is enough. The bytes never reach the method body, because the chain fires in step 4, during deserialization.

It's important to note that while all of that is going on, the transport neither knows nor cares about any of it. It happily deserializes whatever it receives. Whether the result is a denial of service or a shell depends on what else is loaded, which is not a comforting thing to rely on.

The fix is old and well understood, which is the frustrating part. **Untrusted input should not go through native Java serialization at all.** Where that can't be avoided, JEP 290 added `ObjectInputFilter` (Java 9+, backported to 8u121). With it, a service can allow-list exactly the classes it expects, cap graph depth and size, and reject everything else before it is instantiated. The peer should be authenticated before anything is read from it, and the service should bind to a specific network interface instead of all of them. Any "just a `byte[]`" method on a remote object is really an open invitation to run code, addressed to the whole network.

The takeaway is that this isn't a bug in anyone's parsing logic. Funnily enough, the parsing logic never even got a chance to be wrong. The root cause is about when deserialization happens compared to when the application gets to reject the payload. For anything that exports RMI objects, the code that matters most is the code that runs before the method does.
