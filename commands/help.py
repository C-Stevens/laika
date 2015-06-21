from src.datatypes import Type
import src.format

def run(self, *args, **kwargs):
	_helpPrefix = src.format.bold("help | ")
	for i in self.parent.commandList:
		if args[0] == i.config['command_str']:
			self.socket.notice(self.commandData.nick, _helpPrefix+i.config['name'])
			self.socket.notice(self.commandData.nick, _helpPrefix+i.config['help'])
			self.socket.notice(self.commandData.nick, _helpPrefix+self.createUsage(i))
			if i.config['op_args']:
				self.socket.notice(self.commandData.nick, _helpPrefix+"Optional Arguments:\t"+self.argList(i.config['op_args']))
			return
	self.socket.notice(self.commandData.nick, _helpPrefix+"Help information for "+src.format.bold(args[0])+" not found.")
	_friendlyCommandList = []
	for i in self.parent.commandList:
		_friendlyCommandList.append(i.config['command_str'])
	_friendlyCommandList = ', '.join(_friendlyCommandList)

	self.socket.notice(self.commandData.nick, _helpPrefix+"Avaliable commands: "+_friendlyCommandList)

config = {
	'name' : 'Help',
	'command_str' : 'help',
	'args' : (Type.msg,),
	'op_args' : False,
	'auth' : False,
	'help' : "Reports help and usage information for a command."
}