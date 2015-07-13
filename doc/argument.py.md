# `argument.py` Documentation

### Introduction
This file holds the objects and methods responsible for powering Laika's custom argument type functionality. 

### Regex matches
* Channel matching (*Type.channel*): `[#|&]+[^, ]{1,200}`
* Nickname matching (*Type.nick*): `[\\]\\[{}^a-zA-Z][-\\]\\[\\\\{}^\\w]*?`
* Generic message matching (*Type.msg*): `.*`
* User mode matching (*Type.usermode*): `(?:[+-][iwso]+)+`
* Channel mode matching (*Type.channelmode*): `(?:[+-][opsitnbv]+)+`
* Integer matching (*Type.int*): `\d+`
* Negative integer matching (*Type.negint*): `-?\d+`
* Float matching (*Type.float*): `\d+(?:\.\d+)?`
* Negative float matching (*Type.negfloat*): `\d+(?:\.\d+)?`

### Objects
#### Type objects
This object is inherited from `enum.Enum` and acts as Laika's method for storing custom argument types. These objects not only hold their argument type, but also can be queried for the type's regex matching string.

*class* argument.**Type**(enum.Enum)

* Type.**`__str__`**(*self*)<br>
Returns `self.name` to provide a method for accessing the Type's name through `str` casting.


* Type.**validRegex**(*self*)<br>
Returns the regex match for the object's type.  



#### Argument objects
This object is what is created by the commands themselves and how the command author interacts with the regex matching methods in `command.py`. 

This object takes three arguments: *type* (an `argument.Type` enum), *optional* (a boolean), and *name* (a string).

*class* argument.**Argument**()

* Argument.**baseRegex**(*self*)<br>
Returns the base regex match for this argument only by forming a regex matching group with *name* as the match group's name. The regex for itself is obtained by querying *type* for the `type.validRegex()` method. 


* Argument.**describe**(*self*)<br>
Returns simple formatting around an explicit string representation of *type*, surrounded with square brackets (`[]`) if optional, or otherwise surrounded with less than and greater than symbols (`<>`). This function is used for generating usage help for commands.

##### Using Argument objects
`argument.Argument()` objects are used by commands to specify a regex match under a certain match group name. For example, `commands/echo.py`'s argument list is: `[Argument(type=Type.channel, optional=True, name="channel"), Argument(type=Type.msg, optional=False, name="msg")]`.

In this example, the first Argument will return a regex match to `command.py` of "`(?P<channel>)[#|&]+[^, ]{1,200}`"

The second Argument will return a regex match to `command.py` of "`(?P<msg>.*)`"

The *optional* boolean is not dealt with or applied to the regex inside the Argument object. It is instead used by `command.py` while formulating the complete regex match for the command.