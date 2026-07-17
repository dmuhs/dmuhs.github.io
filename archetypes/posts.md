---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ dateFormat "2006-01-02" .Date }}
categories: ["Software"]
url: "/{{ dateFormat "2006/01/02" .Date }}/{{ .File.ContentBaseName }}"
---
