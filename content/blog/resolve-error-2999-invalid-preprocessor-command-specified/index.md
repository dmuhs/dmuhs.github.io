---
Title: ERROR 2999: Invalid preprocessor command specified
Date: 2016-06-03
Category: Software
Status: published
---

I am quite new to working with [Amazon Elastic MapReduce](https://aws.amazon.com/elasticmapreduce/) clusters. To do some large scale data analysis, I built a Pig script and ran it on a local pig installation to verify its functionality. Works. Neat! Let's push it to the cluster and get some serious results on the large dataset!

Luckily for my bill, it didn't take too long to fail.

```sh
[hadoop@ip-XXX-XXX-XXX-XXX samples]$ pig -x mapreduce -f pig/examples/snort.pig -param pcap=data/sample204.pcap
16/06/03 14:05:13 INFO pig.ExecTypeProvider: Trying ExecType : LOCAL
16/06/03 14:05:13 INFO pig.ExecTypeProvider: Trying ExecType : MAPREDUCE
16/06/03 14:05:13 INFO pig.ExecTypeProvider: Picked MAPREDUCE as the ExecType
94   [main] INFO  org.apache.pig.Main  - Apache Pig version 0.14.0-amzn-0 (r: unknown) compiled Apr 06 2016, 22:40:48
16/06/03 14:05:13 INFO pig.Main: Apache Pig version 0.14.0-amzn-0 (r: unknown) compiled Apr 06 2016, 22:40:48
98   [main] INFO  org.apache.pig.Main  - Logging error messages to: /mnt/var/log/pig/pig_1464962713368.log
16/06/03 14:05:13 INFO pig.Main: Logging error messages to: /mnt/var/log/pig/pig_1464962713368.log
2542 [main] INFO  org.apache.pig.Main  - Final script path: /home/hadoop/packetpig/pig/examples/snort.pig
16/06/03 14:05:15 INFO pig.Main: Final script path: /home/hadoop/packetpig/pig/examples/snort.pig
2563 [main] INFO  org.apache.pig.impl.util.Utils  - Default bootup file /home/hadoop/.pigbootup not found
16/06/03 14:05:15 INFO util.Utils: Default bootup file /home/hadoop/.pigbootup not found
2698 [main] ERROR org.apache.pig.Main  - ERROR 2999: Unexpected internal error. Pig Internal Error. Invalid preprocessor command specified : %DEFAULT
16/06/03 14:05:15 ERROR pig.Main: ERROR 2999: Unexpected internal error. Pig Internal Error. Invalid preprocessor command specified : %DEFAULT
Details at logfile: /mnt/var/log/pig/pig_1464962713368.log
2740 [main] INFO  org.apache.pig.Main  - Pig script completed in 2 seconds and 915 milliseconds (2915 ms)
16/06/03 14:05:16 INFO pig.Main: Pig script completed in 2 seconds and 915 milliseconds (2915 ms)
```

Wait, what? How can this fail? Setting %DEFAULT values for script parameters is a pretty standard thing! Well, turns out, all Amazon EMR components [are running on Pig 0.14.0](https://docs.aws.amazon.com/ElasticMapReduce/latest/ReleaseGuide/emr-release-components.html). A pig version [released in November 2014](https://pig.apache.org/releases.html). The latest version (0.15.0) was released in June 2015! Isn't that enough time to at least provide a newer version to non-legacy customers?

Turns out, there's a [bug](https://issues.apache.org/jira/browse/PIG-4342) in version 0.14.0 that affects the preprocessor parsing. Let's look at the [patch diff](https://issues.apache.org/jira/secure/attachment/12683376/PIG-4342-1.patch):

```java
         final String declareToken = "%declare";
         final String defaultToken = "%default";

-        if (preprocessorCmd.equals(declareToken)) {
+        if (preprocessorCmd.toLowerCase().equals(declareToken)) {
             filter.validate(PigCommandFilter.Command.DECLARE);
-        } else if (preprocessorCmd.equals(defaultToken)) {
+        } else if (preprocessorCmd.toLowerCase().equals(defaultToken)) {
             filter.validate(PigCommandFilter.Command.DEFAULT);
         } else {
             throw new IllegalArgumentException("Pig Internal Error. Invalid preprocessor command specified : "
```

Awesome! So there's just a problem with parsing all-uppercase `DEFAULT` and `DECLARE` instructions. This means we don't actually have to fight with the source code and manually implement the patch. Just change all affected instructions to lowercase and Bob's your uncle!
