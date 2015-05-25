def run(line_info, socket):
	line_info.printData() ##DEBUG
	if line_info.args:
		quitMessage = " ".join(line_info.args)
		socket.quit(quitMessage)
	else:
		socket.quit()

config = {
	'name' : 'quit',
	'command_str' : 'quit',
	'auth' : True,
	'help' : "Has the bot disconnect from the server with optional message."
}