def run(line_info, socket):
	line_info.printData() ##DEBUG
	if len(line_info.args) >= 2:
		channel = line_info.args[0]
		actionMsg = " ".join(line_info.args[1:])
		print("\t[!] Action msg:",actionMsg)
		socket.action(channel, actionMsg)

config = {
	'name' : 'Action',
	'command_str' : 'action',
	'auth' : False,
	'help' : "Performs a /me action in the specified channel.",
}