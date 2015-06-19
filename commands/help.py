from src.datatypes import Type
import src.format

def run(self, *args):
	_helpPrefix = src.format.bold("help | ")
	for i in self.parent.commandList:
		if args[0] == i.config['command_str']:
			self.socket.notice(self.commandData.nick, _helpPrefix+i.config['name'])
			self.socket.notice(self.commandData.nick, _helpPrefix+i.config['help'])

			_argList = list(i.config['args'])
			for j, arg in enumerate(_argList):
				_argList[j] = '<'+repr(arg).split(':')[0][1:]+'>'
			_argList = ' '.join(_argList)
			self.socket.notice(self.commandData.nick, _helpPrefix+"Usage: %s%s %s"%(self.commandData.highlightChar,i.config['command_str'],_argList))
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
	'auth' : False,
	'help' : "Reports help and usage information for a command."
}