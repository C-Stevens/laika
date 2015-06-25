import enum

channelRegex = r'[#|&]+[^, ]{1,200}'
nickRegex = '^[\\]\\[{}^a-zA-Z][-\\]\\[\\\\{}^\\w]*?$'
msgRegex = r'.*'
umodeRegex = r'(?:[+-][iwso]+)+'
cmodeRegex = r'(?:[+-][opsitnbv]+)+'
intRegex = r'\d+'
negintRegex = r'-?\d+'
floatRegex = r'\d+(?:\.\d+)?'
negfloatRegex = r'\d+(?:\.\d+)?'

class Type(enum.Enum):
	channel = 0
	nick = 1
	msg = 2
	usermode = 3
	channelmode = 4
	int = 5
	negint = 6
	float = 7
	negfloat = 8

	def __str__(self):
		'''Provides a way to access enum name through str.'''
		return self.name
	def validRegex(self):
		'''Returns the regex match for itself.'''
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
		elif self is Type.negint:
			return negintRegex
		elif self is Type.float:
			return floatRegex
		elif self is Type.negfloat:
			return negfloatRegex

class Argument:
	def __init__(self, type, optional, name):
		self.type = type
		self.optional = optional
		self.name = name
	def baseRegex(self):
		'''Returns base regex from argument's type.'''
		return "(?P<%s>%s)"%(self.name,self.type.validRegex())
	def describe(self):
		'''Returns argument's type name formatted for use in usage calls.'''
		if self.optional:
			return "[%s]"%(str(self.type))
		else:
			return "<%s>"%(str(self.type))