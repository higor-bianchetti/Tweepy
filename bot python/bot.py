# coding: utf-8

import re
import time
import tweepy
import settings
import urllib2
import json
import traceback
from redis import Redis

TWR = []

class BotAPI():
   

    def __init__(self):
        self.RODAR = True

        self.redis = Redis()
        self.redis.set('CONSUMER_KEY', settings.CONSUMER_KEY)
        self.redis.set('CONSUMER_SECRET', settings.CONSUMER_SECRET)
        self.redis.set('OAUTH_TOKEN', settings.OAUTH_TOKEN)
        self.redis.set('OAUTH_TOKEN_SECRET', settings.OAUTH_TOKEN_SECRET)

        auth = tweepy.OAuthHandler(self.redis.get('CONSUMER_KEY'), self.redis.get('CONSUMER_SECRET'), self.redis.get('OAUTH_TOKEN'))
        auth.set_access_token(self.redis.get('OAUTH_TOKEN'), self.redis.get('OAUTH_TOKEN_SECRET'))
        self.api = tweepy.API(auth)

    def carrega_api(self):

        auth = tweepy.OAuthHandler(self.redis.get('CONSUMER_KEY'), self.redis.get('CONSUMER_SECRET'), self.redis.get('OAUTH_TOKEN'))
        auth.set_access_token(self.redis.get('OAUTH_TOKEN'), self.redis.get('OAUTH_TOKEN_SECRET'))
        self.api = tweepy.API(auth)

        if self.get_meu_nome() == None:
            return False
        else:
            return True

    def get_meu_nome(self):
        try:
            return self.api.me().name
        except:
            return None
        
    def get_meu_status(self):
        return self.api.get_status(self.api.me().id).text

    def get_meus_tweets(self):
        return tweepy.Cursor(self.api.user_timeline).items()

    def get_amigos_tweets(self):
        return self.api.friends_timeline()

    def seguir_usuario(self, usuario):
        try:
            self.api.get_user(usuario).follow()
            return 'comecou a seguir {0}'.format(usuario)
        except:
            return 'nao conseguiu seguir {0}'.format(usuario)

    def verifica_tweet(self, tweet, condicao):
        usuario = re.findall(r'{0}'.format(condicao), tweet.text)
        if (len(usuario) > 0):
            return [usuario[0], tweet.created_at]
        return None

    def get_seguidores(self):
        seguidores = tweepy.Cursor(self.api.followers, id = self.api.me().id)
        lista = []
        for seguidor in seguidores.items():
            lista.append(seguidor.screen_name)
        return lista

    def send_mensagem(self, usuario, mensagem):
        self.api.send_direct_message(user_id = usuario, text = mensagem)

    def atualizar_status(self, mensagem):
        try:
            self.api.update_status(mensagem)
        except:
            pass

    def responder_Tweets(self):
	auth = tweepy.OAuthHandler(self.redis.get('CONSUMER_KEY'), self.redis.get('CONSUMER_SECRET'), self.redis.get('OAUTH_TOKEN'))
        auth.set_access_token(self.redis.get('OAUTH_TOKEN'), self.redis.get('OAUTH_TOKEN_SECRET'))
        self.api = tweepy.API(auth)
	meu_nome = '@TemperaturaB '
	twts = self.api.search(q=meu_nome)
	url = 'http://api.openweathermap.org/data/2.5/weather?q='
	for s in twts:
		if s.id not in TWR:
			try:
				usuario = s.user.screen_name
				msg = s.text
				msg = msg.replace("@TemperaturaB ", "")
				cidade = msg.replace(" ", "-")
				TWR.append(s.id)				
				url = url+cidade
				retorno = urllib2.urlopen(url).read()
				
				dados = json.loads(retorno)
				d = dados['main']
				t = d['temp']
				t = int(t)
				t = t - 272
				self.atualizar_status(mensagem  = '@'+unicode(usuario).encode('utf-8')+': a temperatura atual em '+unicode(msg).encode('utf-8')+' é de '+unicode(t).encode('utf-8')+'ºC.')
				print 'Status Atualizado! Mensagem enviada para o usuario: '+unicode(usuario).encode('utf-8')+', cidade: '+unicode(msg).encode('utf-8')+', temperatura de '+unicode(t).encode('utf-8')+'ºC.'
				twts = None
			except:
				self.atualizar_status(mensagem  = 'Olá @'+unicode(usuario).encode('utf-8')+'! Envie @TemperaturaB cidade para obter a temperatura de sua cidade!')
				continue


    def seguir_de_volta(self):
	auth = tweepy.OAuthHandler(self.redis.get('CONSUMER_KEY'), self.redis.get('CONSUMER_SECRET'), self.redis.get('OAUTH_TOKEN'))
        auth.set_access_token(self.redis.get('OAUTH_TOKEN'), self.redis.get('OAUTH_TOKEN_SECRET'))
        self.api = tweepy.API(auth)
	meu_nome = '@TemperaturaB'
	listaDeSeguidores =  self.api.followers_ids()
	listaDeAmigos =  self.api.friends_ids()
	
	for id in listaDeSeguidores:
		if id not in listaDeAmigos:
			try:
				print id
				user = self.api.get_user(user_id=id)
				seguidor = user.screen_name
				self.api.create_friendship(screen_name = seguidor)
				print 'Começando a seguir: '+unicode(seguidor).encode('utf-8')
				self.atualizar_status(mensagem  = 'Obrigado por seguir, @'+unicode(seguidor).encode('utf-8')+'! Envie @TemperaturaB cidade para obter a temperatura de sua cidade!')
	
			except:
				traceback.print_exc()
			




# ------ Main ------------

bot = BotAPI()

if bot.carrega_api() == True:

	
	while bot.RODAR:

		try:
			bot.responder_Tweets()
			time.sleep(30) # Deve esperar um tempo porque o Twitter pode bloquear o acesso á sua API. O Recomendado é dormir por 60 segundos.
			bot.seguir_de_volta()
			time.sleep(30) 
			

		except:
			print 'Exception'
			traceback.print_exc()
			break
                    	#pass
else:
	print 'Saindo do Bot Twitter!'



