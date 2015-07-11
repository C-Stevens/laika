# `format.py` Documentation

### Introduction
This file holds dictionaries that hold IRC-specific formatting codes for manipulating text sent to the server, as well as methods for safe application of these codes.

The methods found in this file can be safely nested, to apply several different formatting options to your desired text string.

### Functions

* format.**bold**(*string*)<br>
Returns *string* prefixed with IRC bold control character `\x02` and suffixed with IRC reset character `\x0F`.


* format.**italic**(*string*)<br>
Returns *string* prefixed with IRC italic control character `\x1D` and suffixed with IRC reset character `\x0F`.


* format.**underline**(*string*)<br>
Returns *string* prefixed with IRC underline control character `\x1F` and suffixed with IRC reset character `\x0F`.


* format.**invert**(*string*)<br>
Returns *string* prefixed with IRC reverse format control character `\x16` and suffixed with IRC reset character `\x0F`.


* format.**color**(*string*[, *color*[, *background*]])<br>
Returns string with colored formatting. If *color* and *background* unspecified, *string* will be returned as explicitly black (`\x0301`).<br>
If *color* is specified, returns *string* prefixed with IRC color text control character `\x03`, the specified color key's dictionary value, and suffixed with IRC reset character `\x0F`.<br>
If *background* is specified, returns *string* prefixed with IRC color text control character `\x03`, the specified color key's dictionary value (if *color* not specified, it defaults to `'black'`), a comma `','`, the specified background color key's dictionary value, and suffixed with IRC reset character `\x0F`.<br>
If an a key match cannot be made with the string given to *color* or *background* and a `KeyError` is raised, *string* will be returned with no formatting applied.

### Valid color keys

* `'white'`
* `'black'`
* `'blue'`
* `'green'`
* `'red'`
* `'brown'`
* `'purple'`
* `'orange'`
* `'yellow'`
* `'light-green'`
* `'teal'`
* `'cyan'`
* `'light-blue'`
* `'pink'`
* `'grey'`
* `'light-grey'`

### Examples
The following examples employ examples of more complicated nesting and usage for `format.py`'s functions. The output is more-or-less indicative of how the text will appear in user's IRC clients.

Due to GitHub's strict HTML filtering, the below representations are provided in image form. Equivalent HTML representations are accompanied as alt-text and can be viewed in the raw markdown file.

```python
src.format.bold(src.format.italic(src.format.underline("foo")))
```
Yeilds:

![<span style="font-weight: bold; text-decoration: underline; font-style: italic">foo</span>](img/bold-italic-underline.png "Bold, italic, and underlined text")

```python
src.format.underline(src.format.color(src.format.italic("foo"),'light-green'))
```
Yeilds:

![<span style="text-decoration: underline; font-style: italic; color: light-green">foo</span>](img/underline-lightgreen_text-italic.png "Underlined, italic, and light-green text")

```python
src.format.invert(src.format.color("foo", background='white')
```
Yeilds:

![<span style="color: white; background-color: black">foo</span>](img/inverse-white_background.png "Inverse white background text")

```python
src.format.italic(src.format.invert(src.format.color(src.format.bold("foo"),'cyan','pink')))
```
Yeilds:

![<span style="color: white; background-color: black; font-style: italic; font-weight: bold">foo</span>](img/italic-inverse-cyan_text-pink_background-bold.png "Italic, inverse, bold cyan text with a pink background")

```python
src.format.italic(src.format.color(src.format.bold("foo"),'cyan','pink'))
```
Yeilds:

![<span style="font-style: italic; font-weight: bold; color: cyan; background-color: pink">foo</span>](img/italic-cyan_text-pink_background-bold.png "Italic, bold, cyan text with a pink background")
