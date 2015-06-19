from src.datatypes import Type

def run(self, *args):
	print("Can I see my parent?",self.parent)
	print("\t",args)
	print("CHANNEL:",args[0])
	print("MSG:",args[1])
	print("NICK:",args[2])
	self.commandData.printData() ##DEBUG
	self.socket.sendToChannel(args[0], args[1])

config = {
	'name' : 'Echo',
	'command_str' : 'echo',
	'args' : (Type.channel, Type.msg, Type.nick),
	'auth' : False,
	'help' : "Repeats input back into the origin channel."
}