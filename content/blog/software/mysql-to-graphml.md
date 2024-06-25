---
Title: Converting MySQL Table Data to a Graphml File
Date: 2017-06-03
Category: Software
Status: published
---

I recently found myself in the situation where I was given access to a huge MySQL database that contained network traffic flows and IDS signature match data. As I work a lot with graph-based approaches, I needed to convert the table's flow data into a graphml file for later visualization and analysis with scripts I have already written. Now without further ado here's the code:

```python
import pymysql.cursors
import pymysql
import networkx as nx
import sys


# Connect to the database
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='my-secret-pw',
    db='flowdata',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.SSCursor
)

graph = nx.DiGraph()

cursor = conn.cursor()
cursor.execute('SELECT src_ip, dst_ip FROM flows')
for i, row in enumerate(cursor):
    sys.stdout.write("\rReading line %s" % i)
    sys.stdout.flush()
    graph.add_edge(row[0], row[1])

nx.write_graphml(graph, "trente-flowgraph.graphml")
```

It's obvious to see that I only need the data from the first two columns as they contain source and destination IP. The trick here is to use `pymysql.cursors.SSCursor`. This will prevent `pymysql` from loading the whole result set from the `SELECT * ...` query into RAM. Another catch is that `pymysql` apparently is not available for Python 3 yet. SQLAlchemy is a good workaround for bigger projects (such as my [Pastebin Scraper](https://github.com/dmuhs/pastebin-scraper)) but in this case it's complete overkill. Just run the script with `python2.7` and you're good.
