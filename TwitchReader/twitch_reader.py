# Responsável por realizar a captura das mensagens

import os
import sys
import time
import string
import datetime
import threading
from urllib.request import urlopen
import urllib.error
import json
import re
from chat_listener import listen
from read_settings import getSettings

#Busac configs do .ini
settingsDict = getSettings()

def boolFromStr(str):
    return str.lower().strip() == "true"

#Carrega as settings
try:
    nick = (settingsDict['user'])
    print("Usuario: " + nick.strip())
    auth = (settingsDict['pass'])
    verbose = boolFromStr(settingsDict['verbose'])
    if(verbose):
        print("Print de mensagens em console habilitado.")
    debug = boolFromStr(settingsDict['debug'])
    if(debug):
        print("Modo de debug ativado.")
except KeyError as e:
    print ("Config não encontradas no .ini:", e)
    raise

#O canal pode ser passado como argumento ou inserido durante a execução
if len(sys.argv) == 1:
    channel = input("Chat a conectar: ")
else:
    channel = sys.argv[1]


#Cria ou acessa um diretório correspondente ao canal e a data/hora da captura de mensagens
dt = datetime.datetime.now()
d = dt.strftime('%b-%d-%Y')
t = dt.strftime('%H_%M')
dt = dt.strftime('%Y-%m-%d-%I%p')
directory = "logs/" + channel + '/' + dt
if not os.path.exists(directory) and not debug:
    os.makedirs(directory)
print ()
print ("Gravando em " + directory)

def open_file(kind, extension='txt'):
    filename = ""
    filename += kind+'.'+extension
    file_path = os.path.relpath(directory + '/' + filename)
    return open(file_path, 'w')


#Determina wuais arquivos serão criados e preenchidos
files = []
if not debug:
    #Arquivo que contém os nomes de usuários que postam mensagens, separados por quebra de linha
    authors = open_file('usuarios')
    #Arquivo que contém o conteúdo de todas as mensagens, separadas por quebra de linha
    messages = open_file('mensagens')
    files = [authors, messages]

#Valida dados recebidos como sendo mensagens
prog = re.compile('^.*[a-z0-9_.-]+\.tmi\.twitch\.tv PRIVMSG #')
def isMessage(data):
    return prog.match(data) != None

def formatMessage(message):
    return message.strip().split('\n')[0].split('\r')[0]

num_messages = 0

#Operação de log que registra as mensagens capturadas. No momento, escreve em arquivo.
def log(author, message):
    global num_messages
    global done
    num_messages += 1
    if debug:
        return
    message = formatMessage(message)

    if done:
        return
    else:
        try:
            authors.write(author + '\n')
            messages.write(message + '\n')
        except (ValueError):
            print ("Erro ao salvar dados.")
            pass

def get(URL):
    val = None
    while True:
        try:
            val = urlopen(URL)
            break
        except urllib.error.URLError:
            print ("Erro de conexão. Tentando reestabelecer.")
            time.sleep(5)
            pass
    return val


done = False

def endProgram():
    global done
    global dt
    global stopper
    for f in files:
        f.close()
    input('Pressione qualquer tecla para encerrar.')
    sys.exit()

#Função executada em thread separada para captar input de teclado; utilizada para recebe comando de parada de execução
def logEvent(x):
    global done
    try:
        s = input(x)
        if s == '!q':
            print ("Finalizando...")
            done = True
            #stopper.set()
            return

    except (EOFError, KeyboardInterrupt):
        print ()
        print ()
        print ("Finalização forçada.")
        endProgram()
        pass
    #if not done:
        #start_new_thread(logEvent, (x,))
        #threading.Thread(target=logEvent,args=(x,)).start()
    #else:
        #return
    return

#Valida dados recebidos como sendo uma mensagem; remove caracteres problemáticos
def interpret(data):
    global done
    if isMessage(data):
        if done:
            return
        try:
            try:
                author = data.split('@')[1].split('.tmi.twitch.tv',1)[0]
            except (IndexError):
                author = data.split('.tmi.twitch.tv',1)[0]
            s = channel + ' :'
            message = s.join(data.split(s)[1:])
            message = list(filter(lambda x: x in string.printable, message))
            j = ""

            #É aqui a chamada para a escrita dos dados
            log(author, j.join(message))

            #Print em console das mensagens
            if verbose:
                print ((author + ' - ' + j.join(message)).strip())
        except (IndexError):
            print()
            print ('Dados ininteligíveis - ' + data)
            print()
            return


def endFunc():
    global done
    return done

print ()
print ("Iniciando!")
print ("Digite '!q' para encerrar.")
#Lançamento da thread que cuida de captar input
threading.Thread(target=logEvent,args=("Listening!",)).start()
try:
    listen(channel, nick, auth, interpret, endFunc)
except (SystemExit):
    print ("")
    raise
print ("Finalizando!")
endProgram()
