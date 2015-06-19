from src.datatypes import Type

def run(self, *args):
	self.socket.joinChannels(args[0])

config = {
	'name' : 'Join',
	'command_str' : 'join',
	'args' : (Type.channel,),
	'auth' : True,
	'help' : "Has the bot join a channel or a set of channels."
}