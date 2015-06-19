from src.datatypes import Type

def run(self, *args):
	self.socket.action(args[0], args[1])

config = {
	'name' : 'Action',
	'command_str' : 'action',
	'args' : (Type.channel, Type.msg),
	'auth' : False,
	'help' : "Performs a /me action in the specified channel.",
}