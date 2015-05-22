def run_check(line_info):
	'''Checks if the command is being called. Returns 0 if it's being called, 1 if not.'''
	if line_info.command == config['command_str']:
		return 0
	else:
		return 1

def run(line_info, socket):
	line_info.printData() ##DEBUG
	if line_info.args:
		message = " ".join(line_info.args)
		socket.sendToChannel(line_info.channel, message)

config = {
	'name' : 'echo',
	'command_str' : 'echo',
	'auth' : False,
	'help' : "Repeats input back into the origin channel."
}