def run(line_info, socket):
	line_info.printData() ##DEBUG
	channel = line_info.args[0]
	quitMessage = " ".join(line_info.args[1:])
	socket.partChannels(channel, quitMessage)

config = {
	'name' : 'Part',
	'command_str' : 'part',
	'auth' : True,
	'help' : "Has the bot leave one channel with optional message."
}