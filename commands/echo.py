from src.datatypes import Type

def run(self, *args):
	self.commandData.printData() ##DEBUG
	self.socket.sendToChannel(self.commandData.channel, args[0])

config = {
	'name' : 'Echo',
	'command_str' : 'echo',
	'args' : (Type.msg,),
	'auth' : False,
	'help' : "Repeats input back into the origin channel."
}