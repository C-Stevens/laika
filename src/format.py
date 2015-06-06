formatting = {
	'bold'		:	'\x02',
	'italic'	:	'\x1D',
	'underline'	:	'\x1F',
	'colorText'	:	'\x03',
	'invert'	:	'\x16',
	'RESET'		:	'\x0F'
}

colors = {
	'white'		:	'00',
	'black'		:	'01',
	'blue'		:	'02',
	'green'		:	'03',
	'red'		:	'04',
	'brown'		:	'05',
	'purple'	:	'06',
	'orange'	:	'07',
	'yellow'	:	'08',
	'light-green'	:	'09',
	'teal'		:	'10',
	'cyan'		:	'11',
	'light-blue'	:	'12',
	'pink'		:	'13',
	'grey'		:	'14',
	'light-grey'	:	'15'
}

def bold(string):
	'''Returns input string as bold text.'''
	return formatting["bold"] + string + formatting["RESET"]

def italic(string):
	'''Returns input string as italic text.'''
	return formatting["italic"] + string + formatting["RESET"]

def underline(string):
	'''Returns input string as underline text.'''
	return formatting["underline"] + string + formatting["RESET"]

def invert(string):
	'''Returns input string with reverse formatting.'''
	return formatting["invert"] + string + formatting["RESET"]

def color(string, color="black", background=None):
	'''Returns input string with requesed color formatting.'''
	try:
		if background is None:
			return formatting["colorText"] + colors[color] + string + formatting["RESET"]
		else:
			return formatting["colorText"] + colors[color] + "," + colors[background] + string + formatting["RESET"]
	except: # Catch invalid color names raising dict errors
		return string