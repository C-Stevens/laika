def run(line_info, socket):
	line_info.printData() ##DEBUG
	channels = []
	if line_info.args:
		for i in line_info.args:
			channels.append(i)
		socket.joinChannels(channels)

config = {
	'name' : 'Join',
	'command_str' : 'join',
	'auth' : True,
	'help' : "Has the bot join a channel or a set of channels."
}