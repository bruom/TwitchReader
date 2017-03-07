#Lê o .ini para criar um dicionário de configs {string:string}
def getSettings():
    with open('twitch_reader.ini', 'r') as settings:
        settings = list(settings)
        settingsDict = {}
        for setting in settings:
            setting = setting.split('=')
            try:
                settingsDict[setting[0]] = setting[1]
            except (IndexError):
                continue
    return settingsDict
