# Responsável por realizar a conexão com o Twitch e mantar a troca de mensagens necessárias para o serviço

import socket
import time

# Param - nome do canal a se conectar, o nome de usuário do bot e a chave de autenticação da aplicação (provenientes do .ini)
def connect(channel, nick, PASS):
    join = "#" + channel
    while True:
        try:
            sock = socket.socket()
            sock.connect(("irc.twitch.tv",6667))
            sock.send("PASS {}\r\n".format(PASS).encode("utf-8"))
            sock.send("NICK {}\r\n".format(nick).encode("utf-8"))
            sock.send("JOIN {}\r\n".format(join).encode("utf-8"))
            break
        except socket.error:
            print ("Problema de conexão. Tentando novamente.")
            pass
    return sock

# Mantém a conexão e manda cada linha de mensagens para ser interpretada e, se relevante, logada
def listen(channel, nick, PASS, interpret, endFunc=None):
    try:
        sock = connect(channel, nick, PASS)
        sock.settimeout(6)
        while True:
           data = ''
           while True:
               try:
                   data = sock.recv(512).decode("utf-8")
                   break
               except socket.timeout:
                   if endFunc and endFunc():
                       return
                   continue
               except socket.error:
                   print ("Problema de conexão.")
                   time.sleep(5)
                   sock = connect(channel, nick, PASS)
                   sock.settimeout(6)
                   break
           # O Twitch madna um PING e espera um PONG para garantir a conexão
           if data[0:4] == "PING":
              sock.send(data.replace("PING", "PONG").encode("utf-8"))

           # Os dados recebidos são repassados para potencial logging
           for line in data.split('\n'):
               if line != '':
                   interpret(line)
    except (KeyboardInterrupt, SystemExit):
        print ("Interrompido.")
        raise
    return
