---
Title: Parsing KMZ Track Data in Python
Date: 2018-09-14
Category: Software
Status: published
---

A few days back I stumbled across an interesting problem. I was asked to develop a solution that was doing some analysis work on geolocation data stored in KMZ format. Existing solutions like [fastkml (64KB)](https://pypi.python.org/pypi/fastkml/0.11) and [pykml (42KB)](https://pypi.python.org/pypi/pykml/0.1.3) seemed nice at the first glance, proved to be unnecessary overhead, however. They're mostly meant to manipulate and write data into KML format. I just needed to read the data for my later calculations. So I decided to build a solution using the Python Standard Library.

The first trick is that a KMZ file is nothing else but a zip-compressed KML file. Inside you'll find a file called `doc.kml`. So let's open and extract:

```python
from zipfile import ZipFile

kmz = ZipFile(filename, 'r')
kml = kmz.open('doc.kml', 'r').read()
```
The KML data's juicy part looks something like this:
```xml
<Folder>
	<name>11112222-XXYYZ-TESTTRACK</name>
	<Document>
		<name>11112222XXYYZTESTTRACK-track-20161214T105653+0100.kmz</name>
		<Placemark>
			<name>1111XXYYZ-track-20161214T105653+0100</name>
			<gx:Track>
				<when>2016-12-13T13:16:01.709+02:00</when>
				<when>2016-12-13T13:18:02.709+02:00</when>
				<when>2016-12-13T13:23:21.709+02:00</when>
				<when>2016-12-13T13:24:23.709+02:00</when>
				<!-- more timestamps -->
				<gx:coord>13.7111482XXXXXXX 51.0335960XXXXXXX 0</gx:coord>
				<gx:coord>13.7111577XXXXXXX 51.0337028XXXXXXX 0</gx:coord>
				<gx:coord>13.7113847XXXXXXX 51.0339241XXXXXXX 0</gx:coord>
				<gx:coord>13.7115764XXXXXXX 51.0341949XXXXXXX 0</gx:coord>
				<!-- more coordinates -->
			    <ExtendedData>
				</ExtendedData>
			</gx:Track>
		</Placemark>
		<Placemark>
			<name>Reference Point #1</name>
			<Point>
				<coordinates>13.72467XXXXXXXXX,51.07873XXXXXXXXX,0</coordinates>
			</Point>
		</Placemark>
		<!-- more Placemarks -->
	</Document>
</Folder>
```

Now we can parse the resulting string using `lxml`.

```python
from lxml import html

doc = html.fromstring(kml)
for pm in doc.cssselect('Folder Document Placemark'):
    tmp = pm.cssselect('track')
    name = pm.cssselect('name')[0].text_content()
    if len(tmp):
        # Track Placemark
        tmp = tmp[0]  # always one element by definition
        for desc in tmp.iterdescendants():
            content = desc.text_content()
            if desc.tag == 'when':
                do_timestamp_stuff(content)
            elif desc.tag == 'coord':
                do_coordinate_stuff(content)
            else:
                print("Skipping empty tag %s" % desc.tag)
    else:
        # Reference point Placemark
        coord = pm.cssselect('Point coordinates')[0].text_content()
        do_reference_stuff(coord)
```

Alright. Let's see what's going on here: First we regard the document as HTML and parse it using `lxml.html`. Then we iterate over all Placemarks in `Folder > Document > Placemark`. If a Placemark has a child `track`, it's holding our timestamps and coordinate data. Otherwise it's considered a reference point just holding some location data. With `cssselect` we can get the respective data and do stuff with it. Just keep in mind it returns a list, so you always have to access the first element. Then we call `text_content()`l to convert the tag content to a string for further manipulation and logging.

It's also worth mentioning that `lxml` and by extension `cssselect` **do not support the necessary pseudo elements for KML**. So you won't be able to address anything like `gx:Track`. It's not a big deal here if you know that you can still address the element with `cssselect('track')`. For more info [look it up in the docs](http://lxml.de/2.3/cssselect.html).

I'm lazy, so I use `cssselect`. You might have to install this as a dependency with `pip3 install cssselect`. You can also use the selecting mechanism lxml provides, but previous experience has shown that it's very tedious and hard to debug for such a quick and dirty hack.

The rest is just string magic, really. Just split the content you get, convert it to a float and insert it into your data structure of choice to continue working with it later.

Some info that helped me get a grip on the KML format:

- [KMZ Documentation by Google](https://developers.google.com/kml/documentation/kmzarchives)
- [KML Placemark Reference and Samples by Google](https://developers.google.com/kml/documentation/kml_tut#placemarks)
- [KML on Wikipedia](https://en.wikipedia.org/wiki/Keyhole_Markup_Language)

