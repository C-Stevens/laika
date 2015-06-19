import enum

channelRegex = '[#|&]+[^, ]{1,200}'
nickRegex = '[^0-9\-#]{1}([0-9a-zA-z\-\{\}\^\[\]\\\][^#])+'
msgRegex = '.*'
umodeRegex = '[+-]{1}[iwso]{1,4}'
cmodeRegex = '[+-]{1}[opsitnbv]{1,8}'
intRegex = '[0-9].*'

class Type(enum.Enum):
	channel = 0
	nick = 1
	msg = 2
	usermode = 3
	channelmode = 4
	int = 5

	def validRegex(self):
		if self is Type.channel:
			return channelRegex
		elif self is Type.nick:
			return nickRegex
		elif self is Type.msg:
			return msgRegex
		elif self is Type.usermode:
			return umodeRegex
		elif self is Type.channelmode:
			return cmodeRegex
		elif self is Type.int:
			return intRegex