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