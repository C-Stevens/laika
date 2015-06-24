from src.argument import *
import src.format

def run(self, **kwargs):
	_helpPrefix = src.format.bold("help | ")
	command = kwargs.get('command')
	for i in self.parent.commandList:
		if command == i.config['command_str']:
			self.socket.notice(self.commandData.nick, _helpPrefix+i.config['name'])
			self.socket.notice(self.commandData.nick, _helpPrefix+i.config['help'])
			self.socket.notice(self.commandData.nick, _helpPrefix+self.createUsage(i))
			return
	self.socket.notice(self.commandData.nick, _helpPrefix+"Help information for "+src.format.bold(command)+" not found.")
	_friendlyCommandList = []
	for i in self.parent.commandList:
		_friendlyCommandList.append(i.config['command_str'])
	_friendlyCommandList = ', '.join(_friendlyCommandList)

	self.socket.notice(self.commandData.nick, _helpPrefix+"Avaliable commands: "+_friendlyCommandList)

config = {
	'name' : 'Help',
	'command_str' : 'help',
	'args' : [Argument(type=Type.msg, optional=False, name="command")],
	'auth' : False,
	'help' : "Reports help and usage information for a command."
}