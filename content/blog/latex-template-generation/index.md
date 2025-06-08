---
Title: Quick Hack: Generating PDFs with Python and XeTeX
Date: 2018-01-10
Category: Software
Status: published
---

A friend of mine is following a PhD in a non-technical field. And his boss is a bully. Work mainly happens with high-level statistical analysis tools. No one knows anything about programming and most problems are solved by hand. While on a positive note this means good chances to get a student job, it also means that progress moves slowly, especially when it comes to working with large datasets.

Due to some kind of disorder related to social dominance, his boss regularly gives him harassing tasks. The ones that would take two students a month to complete - with a deadline set for the day after tomorrow. Obviously, this is impossible to complete if you don't know how to automate the task. That's where I come in - and boy was it satisfying to own his boss.

To maintain his anonymity, I will not show direct samples of the dataset or mention the use-case of it. Just be assured that it took a fuckton of sanitization work to bring it into a decent format that can easily be processed. The main idea here is that we parse the relevant data, render it onto a XeTeX template and save the rendered file on the disk to later render it into a PDF using `xelatex`.

First of all the template:

```latex
\documentclass[a4paper]{article}
\usepackage[margin=0.5in]{geometry}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[justification=centering]{caption}
\usepackage{longtable}
\usepackage{tabu}
\usepackage{microtype}
\usepackage{pdflscape}

\pagenumbering{gobble}
\tabulinesep=3pt

\begin{document}
\begin{landscape}
\begin{table}[h]
\centering
\begin{tabular}{|c|c|c|}
\hline
\textbf{Column 1} & \textbf{Column 2} & \textbf{Column 3} \\ \hline
$table1
\end{tabular}
\end{table}

\section{Table 2}
\begin{table}[h]
\centering
\begin{tabular}{|c|c|c|c|c|}
\hline
\textbf{Column 1} & \textbf{Column 2} & \textbf{Column 3} & \textbf{Column 4} & \textbf{Column 5} \\ \hline
1 & $t2_row1 \\ \hline
2 & $t2_row2 \\ \hline
3 & $t2_row3 \\ \hline
\end{tabular}
\caption{Table 2 caption}
\end{table}

\section{Table 3}
\begin{longtabu} to \textwidth {|X[1,c]|X[5,c]|X[1,c]|X[1,c]|X[1,c]|X[1,c]|} \hline
\multicolumn{1}{|c|}{\textbf{Column 1}} & \multicolumn{1}{|c|}{\textbf{Column 2}} & \multicolumn{1}{|c|}{\textbf{Column 3}} & \multicolumn{1}{|c|}{\textbf{Column 4}} & \multicolumn{1}{|c|}{\textbf{Column 5}} & \multicolumn{1}{|c|}{\textbf{Column 6}} \\ \hline
\endfirsthead

\multicolumn{6}{c}%
{{\bfseries \tablename\ \thetable{} -- continued}} \\
\multicolumn{1}{|c|}{\textbf{Column 1}} & \multicolumn{1}{|c|}{\textbf{Column 2}} & \multicolumn{1}{|c|}{\textbf{Column 3}} & \multicolumn{1}{|c|}{\textbf{Column 4}} & \multicolumn{1}{|c|}{\textbf{Column 5}} & \multicolumn{1}{|c|}{\textbf{Column 6}} \\ \hline
\endhead

\hline \multicolumn{6}{|r|}{{Continue on the next page}} \\ \hline
\endfoot

\endlastfoot

$table3

\caption{Table 3 caption}
\end{longtabu}
\end{landscape}
```

So we will render our data on a landscape A4 page in three tables. With the help of the `longtabu` package we can break tables on page break and continue them on the next page. You will notice some uncommon variables such as `$table1` or `$t2_row1`. These are placeholders for Python's `string.Template` object, which allows you to do simple substitutions in strings. Example:

```python
In [1]: from string import Template

In [2]: t = Template("This is a $tmpl_type template")

In [3]: t.substitute(tmpl_type="sample")
Out[3]: 'This is a sample template'
```

With our substitution variables set, we just have to parse the dataset, sanitize all format fuckups, and bring it into the XeTeX table line format. For that we can easily provide line templates for each of the three tables

```python
T1_LINE = "{col_1} & {col2} & {col_3} \\\\ \\hline"
T2_LINE = "{col_1} & {col_2} & {col_3} & {col_4}"
T3_LINE = "{col_1} & {col_2} & {col_3} & {col_4} & {col_5} & {col_6} \\\\ \\hline"
```

Don't forget to escape the backslashes. Ugly, I know, but XeTeX needs double backslashes for manual line breaks. Now after sanitization, we replace some special table characters, and simply generate our table rows like this:

```python
t3_rows = []
for cat, cat_data in part.data.items():
    text = content[cat.upper()].replace('&', '\\&')
    t3_rows.append(T3_LINE.format(
        col_1=cat.upper(),
        col_2=text,
        col_3=cat_data[0],
        col_4=cat_data[1],
        col_5=cat_data[2],
        col_6=cat_data[3],
    ))
```

All that's left now is to do the substitution on the template file and save it to the output directory:

```python
with open(output_filename, 'w') as outfile:
    output = p_template.substitute(
        table1=table1,
        t2_row1=t2_data[0],
        t2_row2=t2_data[1],
        t2_row3=t2_data[2],
        table3="\n".join(t3_rows)
    )
    outfile.write(output)
```

In my case this resulted in 146 `.tex` files. In the output directory I just had to call `xelatex *.tex`, wait 5 minutes, and done! Due to the dataset's size, this resulted in roughly 500 pages or output. Impossible to do by hand. Said friend went to the office, printed all of the tables (using recycling paper, of course!) and put the stack on the professor's table. Owned. And boy, do those tables look pretty!

A little extra: The shell command I used to determine how many PDF pages were generated in the output directory:

```bash
for file in results/*.pdf; do pdfinfo $file | grep Pages | awk '{print $2}'; done | awk '{s+=$1} END {print s}'
```
