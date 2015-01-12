def hello():
	print("derp")

class bot:
        def __init__(self, configFile):
                self.configFile = configFile
        def printData(self):
                print(self.configFile.config)
