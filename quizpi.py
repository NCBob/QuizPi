import pygame
import sys
from pygame.locals import *
import RPi.GPIO as GPIO
import urllib.request
from datetime import datetime
import json
from random import randint
from pprint import pprint
import time
import pickle
import collections
import os
from operator import itemgetter, attrgetter, methodcaller

#variables del juego
playing = True
looping = True
time_stamp_btn = time.time()
btnPressed = -1
strPlayerName = ''

sound_intro = "./Sounds/intro.mp3"
sound_applause = "./Sounds/applause.mp3" 
sound_error = "./Sounds/buzzer.mp3"
sound_drumroll = "./Sounds/drumroll.mp3"
sound_tada = "./Sounds/tada.mp3"
sound_click = "./Sounds/click.mp3"

#Game Phases
f_INTRO = 0
f_MENU = 1
f_REGISTRATION = 2
f_QUESTIONS = 3
f_RESULTS = 4
f_HIGHSCORES = 5
f_ABOUT = 6

currentPhase = f_INTRO

# Definimos los botones
btnRed = 31 		# boton RED
btnYellow = 33 	# boton YELLOW
btnGreen = 35 		# boton GREEN
btnBlue = 37 		# boton BLUE
 
# Definimos algunos colores
cWHITE   = (255, 255, 255)
cBLACK    = (  0,   0,   0)
cORANGE  = (255, 138,   0)
cRED     = (255,   0,   0)
cYELLOW = (255, 191,   0)
cGREEN    = ( 72, 183,   5)
cBLUE     = (  0,   0, 255) 

# Inicializamos los GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(btnRed, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btnYellow, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btnGreen, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btnBlue, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#os.putenv ("SDL_FBDEV" , "/dev/fb1")
#os.putenv ("SDL_MOUSEDRV" , "TSLIB")
#os.putenv ("SDL_MOUSEDEV" , "/dev/input/event0")

# Definimos las funciones de los botones
def btnPush(channel):
	global time_stamp_btn
	global btnPressed
	time_now = time.time()
	if (time_now - time_stamp_btn >= 0.3):
			btnPressed = channel
	time_stamp_btn = time_now

# Asociamos un evento a los botones
# Example: GPIO.add_event_detect(BUTTON_1, GPIO.BOTH, bouncetime=1000)
GPIO.add_event_detect(btnRed, GPIO.BOTH, callback=btnPush)
GPIO.add_event_detect(btnYellow, GPIO.BOTH, callback=btnPush)
GPIO.add_event_detect(btnGreen, GPIO.BOTH, callback=btnPush)
GPIO.add_event_detect(btnBlue, GPIO.BOTH, callback=btnPush)

#Inicializamos pygame
pygame.mixer.pre_init(44100, -16, 1, 1024*3) #PreInit Music, plays faster
pygame.init()

# initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
myfont = pygame.font.SysFont("monospace", 15)

# Ocultamos el puntero del raton
pygame.mouse.set_visible(False) #hide the mouse cursor
  
# Establecemos el largo y ancho de la pantalla.
dimensiones = [480,320]
pantalla = pygame.display.set_mode(dimensiones, pygame.FULLSCREEN)
posicion_base = [0,0]
 
# Usado para gestionar cuán rápido se actualiza la pantalla
reloj = pygame.time.Clock()
 
def generaPreguntaSumas1Cifra():
	arg1 = randint(0, 9)
	arg2 = randint(0, 9)
	arg3 = randint(1, 2)
	pregunta = r'{"category": "1 de Primaria", "type": "multiple", "difficulty": "easy", "question": "¿Cuanto es la suma de ' + str(arg1) + ' mas ' + str(arg2) +'?", "correct_answer": "' + str(arg1+arg2) + r'", "incorrect_answers": ["' + str(arg1+arg2+arg3) + r'", "' + str(arg1+arg2-arg3) + r'", "' + str(arg1+arg2+arg3+1) + r'"]}'
	return pregunta;

def generaPreguntaSumas2Cifras():
	arg1 = randint(0, 80)
	arg2 = randint(0, 99)
	arg3 = randint(1, 20)
	pregunta = r'{"category": "1 de Primaria", "type": "multiple", "difficulty": "easy", "question": "¿Cuanto es la suma de ' + str(arg1) + ' mas ' + str(arg2) +'?", "correct_answer": "' + str(arg1+arg2) + r'", "incorrect_answers": ["' + str(arg1+arg2+arg3) + r'", "' + str(arg1+arg2-arg3) + r'", "' + str(arg1+arg2+arg3+1) + r'"]}'
	return pregunta;

def generaPreguntaSumas2CifrasFacil():
	arg1u = randint(0, 9)
	arg1d = randint(0, 9)
	arg2u = randint(0, 9)
	arg2d = randint(0, 9)
	arg3 = randint(1, 20)
	while (arg2u+arg1u>9):
		arg2u = randint(0, 9)
	while (arg2d+arg1d>9):
		arg2d = randint(0, 9)
	arg1 = arg1d*10 + arg1u
	arg2 = arg2d*10 + arg2u
	pregunta = r'{"category": "1 de Primaria", "type": "multiple", "difficulty": "easy", "question": "¿Cuanto es la suma de ' + str(arg1) + ' mas ' + str(arg2) +'?", "correct_answer": "' + str(arg1+arg2) + r'", "incorrect_answers": ["' + str(arg1+arg2+arg3) + r'", "' + str(arg1+arg2-arg3) + r'", "' + str(arg1+arg2+arg3+1) + r'"]}'
	return pregunta;

def generaPreguntaMayorQue():
	arg1 = randint(0, 95)
	bueno = arg1 + randint(1,100-arg1)
	malo1 = arg1 - randint(0, arg1)
	malo2 = arg1 - randint(0, arg1)
	malo3 = arg1 - randint(0, arg1)
	pregunta = r'{"category": "1 de Primaria", "type": "multiple", "difficulty": "easy", "question": "¿Cual de estos números es MAYOR que ' + str(arg1) +'?", "correct_answer": "' + str(bueno) + r'", "incorrect_answers": ["' + str(malo1) + r'", "' + str(malo2) + r'", "' + str(malo3) + r'"]}'
	return pregunta;

def generaPreguntaMenorQue():
	arg1 = randint(0, 95)
	bueno = arg1 - randint(1,arg1)
	malo1 = arg1 + randint(0, 100-arg1)
	malo2 = arg1 + randint(0, 100-arg1)
	malo3 = arg1 + randint(0, 100-arg1)
	pregunta = r'{"category": "1 de Primaria", "type": "multiple", "difficulty": "easy", "question": "¿Cual de estos números es MENOR que ' + str(arg1) +'?", "correct_answer": "' + str(bueno) + r'", "incorrect_answers": ["' + str(malo1) + r'", "' + str(malo2) + r'", "' + str(malo3) + r'"]}'
	return pregunta;

def generaPreguntaSerie():
	buena = []
	buena.append(randint(0, 99))
	valor = randint(0, 99)
	while (valor in buena):
		valor = randint(0, 99)
	buena.append(valor)
	valor = randint(0, 99)
	while (valor in buena):
		valor = randint(0, 99)
	buena.append(valor)
	buena.sort()
	strBuena = str(buena[0]) + ' < ' + str(buena[1]) + ' < '  + str(buena[2])

	malas = []
	iMalas = 0
	while (iMalas<3):
		mala = []
		mala.append(randint(0, 99))
		valor = randint(0, mala[0])
		while (valor in mala):
			valor = randint(0, mala[0])
		mala.append(valor)
		valor = randint(mala[1], 99)
		while (valor in mala):
			valor = randint(mala[1], 99)
		mala.append(valor)
		strMala = str(mala[0]) + ' < ' + str(mala[1]) + ' < '  + str(mala[2])
		malas.append(strMala)
		iMalas = iMalas + 1

	pregunta = r'{"category": "1 de Primaria", "type": "multiple", "difficulty": "easy", "question": "¿Cual de estas series es correcta?", "correct_answer": "' + strBuena + r'", "incorrect_answers": ["' + malas[0] + r'", "' + malas[1] + r'", "' + malas[2] + r'"]}'
	return pregunta;

def generaPreguntaAnteriorA():
	arg1 = randint(5, 99)
	bueno = arg1 - 1
	malo1 = arg1 - randint(1, 10)
	malo2 = arg1 - randint(1, 10)
	while (malo2 == malo1):
		malo2 = arg1 - randint(1, 10)
	malo3 = arg1 - randint(1, 10)
	while ((malo3 == malo1) or (malo3 == malo2)):
		malo3 = arg1 - randint(1, 10)
	pregunta = r'{"category": "1 de Primaria", "type": "multiple", "difficulty": "easy", "question": "¿Cual de estos números es el ANTERIOR a ' + str(arg1) +'?", "correct_answer": "' + str(bueno) + r'", "incorrect_answers": ["' + str(malo1) + r'", "' + str(malo2) + r'", "' + str(malo3) + r'"]}'
	return pregunta;

def generaPreguntasPrimaria():
	preguntas = r'{"response_code": 0,"results": ['
	pr = 0
	while (pr<10):
		categoria = randint(0,5)
		if (categoria == 0):
			preguntas = preguntas + generaPreguntaSumas1Cifra()
		if (categoria == 1):
			preguntas = preguntas + generaPreguntaSumas2CifrasFacil()
		if (categoria == 2):
			preguntas = preguntas + generaPreguntaMayorQue()
		if (categoria == 3):
			preguntas = preguntas + generaPreguntaMenorQue()
		if (categoria == 4):
			preguntas = preguntas + generaPreguntaSerie()
		if (categoria == 5):
			preguntas = preguntas + generaPreguntaAnteriorA()
		pr = pr + 1
		if (pr < 10):
			preguntas = preguntas + ','
	preguntas = preguntas + ']}'
	return preguntas

def dameLetra (pos):
	print("dentro de dameletra. Pos=("+str(pos[0])+","+str(pos[1])+")")
	letra = ''
	if 24 <= pos[0] <= 57 and 117 <= pos[1] <= 157:			# A
		letra = 'A'
	elif 74 <= pos[0] <= 107 and 117 <= pos[1] <= 157:		# B
		letra = 'B'
	elif 124 <= pos[0] <= 157 and 117 <= pos[1] <= 157:		# C
		letra = 'C'
	elif 174 <= pos[0] <= 207 and 117 <= pos[1] <= 157:		# D
		letra = 'D'
	elif 224 <= pos[0] <= 257 and 117 <= pos[1] <= 157:		# E
		letra = 'E'
	elif 274 <= pos[0] <= 307 and 117 <= pos[1] <= 157:		# F
		letra = 'F'
	elif 324 <= pos[0] <= 357 and 117 <= pos[1] <= 157:		# G
		letra = 'G'
	elif 374 <= pos[0] <= 407 and 117 <= pos[1] <= 157:		# H
		letra = 'H'
	elif 424 <= pos[0] <= 457 and 117 <= pos[1] <= 157:		# I
		letra = 'I'
	elif 24 <= pos[0] <= 57 and 167 <= pos[1] <= 207:		# J
		letra = 'J'
	elif 74 <= pos[0] <= 107 and 167 <= pos[1] <= 207:		# K
		letra = 'K'
	elif 124 <= pos[0] <= 157 and 167 <= pos[1] <= 207:		# L
		letra = 'L'
	elif 174 <= pos[0] <= 207 and 167 <= pos[1] <= 207:		# M
		letra = 'M'
	elif 224 <= pos[0] <= 257 and 167 <= pos[1] <= 207:		# N
		letra = 'N'
	elif 274 <= pos[0] <= 307 and 167 <= pos[1] <= 207:		# Ñ
		letra = 'Ñ'
	elif 324 <= pos[0] <= 357 and 167 <= pos[1] <= 207:		# O
		letra = 'O'
	elif 374 <= pos[0] <= 407 and 167 <= pos[1] <= 207:		# P
		letra = 'P'
	elif 424 <= pos[0] <= 457 and 167 <= pos[1] <= 207:		# Q
		letra = 'Q'
	elif 24 <= pos[0] <= 57 and 217 <= pos[1] <= 257:		# R
		letra = 'J'
	elif 74 <= pos[0] <= 107 and 217 <= pos[1] <= 257:		# S
		letra = 'K'
	elif 124 <= pos[0] <= 157 and 217 <= pos[1] <= 257:		# T
		letra = 'L'
	elif 174 <= pos[0] <= 207 and 217 <= pos[1] <= 257:		# U
		letra = 'M'
	elif 224 <= pos[0] <= 257 and 217 <= pos[1] <= 257:		# V
		letra = 'N'
	elif 274 <= pos[0] <= 307 and 217 <= pos[1] <= 257:		# W
		letra = 'Ñ'
	elif 324 <= pos[0] <= 357 and 217 <= pos[1] <= 257:		# X
		letra = 'O'
	elif 374 <= pos[0] <= 407 and 217 <= pos[1] <= 257:		# Y
		letra = 'P'
	elif 424 <= pos[0] <= 457 and 217 <= pos[1] <= 257:		# Z
		letra = 'Q'
	
	print("letra="+letra)
	return letra

while (playing == True):
	# -------- Bucle de la PANTALLA INICIAL -----------
	if ((playing == True) and (currentPhase == f_INTRO)):
		# Limpia la pantalla y establece su color de fondo
		pantalla.fill(cWHITE)
	
		# Muestra la pantalla inicial en pantalla:
		imagen = pygame.image.load("./Images/quiz_pantalla_0_INICIO_ingles.png").convert()
		pantalla.blit(imagen, posicion_base)

		# Limitamos a 20 fotogramas por segundo.
		reloj.tick(20)
 
		# Avancemos y actualicemos la pantalla con lo que hemos dibujado.
		pygame.display.flip()

		pygame.mixer.music.load(sound_intro)
		pygame.mixer.music.play(0)
	
		# Wait for button press
		btnPressed = -1
		looping = True
		while (looping):
			if (btnPressed == btnBlue):			# El usuario pulsa el BOTON BLUE pasamos al menu
				btnPressed = -1
				playing = False
				looping = False
			if (btnPressed == btnRed):			# El usuario pulsa el BOTON RED pasamos al menu
				btnPressed = -1
				looping = False
				currentPhase = f_MENU
				
	# -------- Bucle del MENU -----------
	if (playing and (currentPhase == f_MENU)):
		# Limpia la pantalla y establece su color de fondo
		pantalla.fill(cWHITE)
 
		# Muestra la pantalla inicial en pantalla:
		imagen = pygame.image.load("./quiz_pantalla_1_MENU_ingles.png").convert()
		pantalla.blit(imagen, posicion_base)

		# Limitamos a 60 fotogramas por segundo.
		reloj.tick(20)
 
		# Avancemos y actualicemos la pantalla con lo que hemos dibujado.
		pygame.display.flip()

		pygame.mixer.music.load(sound_click)
		pygame.mixer.music.play(0)
	
		# Esperamos pulsacion de boton
		btnPressed = -1
		looping = True
		while (looping):
			if (btnPressed == btnRed):			# El usuario pulsa el BOTON RED pasamos a IDENTIFICACION
				btnPressed = -1
				currentPhase = f_REGISTRATION
				looping = False
			if (btnPressed == btnYellow):			# El usuario pulsa el BOTON YELLOW pasamos a los MEJORES
				btnPressed = -1
				currentPhase = f_HIGHSCORES
				looping = False
			if (btnPressed == btnGreen):			# El usuario pulsa el BOTON GREEN pasamos a la INFO
				btnPressed = -1
				currentPhase = f_ABOUT
				looping = False
			if (btnPressed == btnBlue):			# El usuario pulsa el BOTON BLUE salimos al INICIO
				btnPressed = -1
				currentPhase = f_INTRO
				looping = False
		
	# -------- Bucle de la Pantalla de INFORMACION -----------
	if (playing and (currentPhase == f_ABOUT)):
		# Limpia la pantalla y establece su color de fondo
		pantalla.fill(cWHITE)
 
		# Muestra la pantalla inicial en pantalla:
		imagen = pygame.image.load("./quiz_pantalla_4_INFORMACION_ingles.png").convert()
		pantalla.blit(imagen, posicion_base)

		# Limitamos a 60 fotogramas por segundo.
		reloj.tick(20)
 
		# Avancemos y actualicemos la pantalla con lo que hemos dibujado.
		pygame.display.flip()

		pygame.mixer.music.load(sound_click)
		pygame.mixer.music.play(0)
	
		# Esperamos pulsacion de boton
		btnPressed = -1
		looping = True
		while (looping):
			if (btnPressed == btnRed):				# El usuario pulsa el BOTON RED volvemos al MENU
				btnPressed = -1
				currentPhase = f_MENU
				looping = False
		
	# -------- Bucle de la Pantalla de MEJORES -----------
	if (playing and (currentPhase == f_HIGHSCORES)):
		# Limpia la pantalla y establece su color de fondo
		pantalla.fill(cWHITE)
 
		# Muestra la pantalla inicial en pantalla:
		imagen = pygame.image.load("./quiz_pantalla_5_MEJORES_ingles.png").convert()
		pantalla.blit(imagen, posicion_base)

		# Recuperamos el fichero de mejores
		high_scores = {}
		if (os.path.exists('./losmejores.txt')) and (os.path.getsize('./losmejores.txt')>0):
			high_scores = json.load(open('./losmejores.txt'))
		else:
			high_scores = {}

		# Iteramos para mostrar
		i = 1
		for key, scores in high_scores.items():
			for tupla in sorted(sorted(sorted(scores, key=itemgetter(3), reverse=False), key=itemgetter(2), reverse=True), key=itemgetter(4), reverse=True):
				nombre = tupla[0]
				nota = tupla[1]
				tiempo = tupla[3]
				porcentaje = tupla[4]
				fuente = pygame.font.SysFont('arial', 22)
				mensaje = fuente.render(str(i), 1, cRED)
				pantalla.blit(mensaje, (40-mensaje.get_rect().width/2, 52+i*18))
				fuente = pygame.font.SysFont('arial', 22)
				mensaje = fuente.render(nombre, 1, cBLUE)
				pantalla.blit(mensaje, (60, 52+i*18))
				mensaje = fuente.render(str(nota), 1, cBLUE)
				pantalla.blit(mensaje, (300-mensaje.get_rect().width/2, 52+i*18))
				mensaje = fuente.render(str(tiempo), 1, cBLUE)
				pantalla.blit(mensaje, (380-mensaje.get_rect().width/2, 52+i*18))
				i = i + 1

		# Limitamos a 60 fotogramas por segundo.
		reloj.tick(20)
 
		# Avancemos y actualicemos la pantalla con lo que hemos dibujado.
		pygame.display.flip()

		pygame.mixer.music.load(sound_applause)
		pygame.mixer.music.play(0)
	
		# Esperamos pulsacion de boton
		btnPressed = -1
		looping = True
		while (looping):
			if (btnPressed == btnRed):			# El usuario pulsa el BOTON RED volvemos al MENU
				btnPressed = -1
				currentPhase = f_MENU
				looping = False

	# -------- Bucle de IDENTIFICACION -----------
	if (playing and (currentPhase == f_REGISTRATION)):
		# Limpia la pantalla y establece su color de fondo
		pantalla.fill(cWHITE)
 
		# Muestra la pantalla inicial en pantalla:
		imagen = pygame.image.load("./quiz_pantalla_21_NOMBRE_ingles.png").convert()
		pantalla.blit(imagen, posicion_base)

		fuente = pygame.font.SysFont('arial', 64)
		mensaje = fuente.render('A', 1, cBLUE)
		pantalla.blit(mensaje, (240-mensaje.get_rect().width/2, 130))

		# Limitamos a 60 fotogramas por segundo.
		reloj.tick(20)
 
		# Avancemos y actualicemos la pantalla con lo que hemos dibujado.
		pygame.display.flip()

		pygame.mixer.music.load(sound_click)
		pygame.mixer.music.play(0)
	
		# Esperamos pulsacion de boton
		btnPressed = -1
		looping = True
		aLetras = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','Ñ','O','P','Q','R','S','T','U','V','W','X','Y','Z','«']
		iLetra = 0
		strPlayerName = ''
		while (looping):
			# for event in pygame.event.get():
				# if event.type == pygame.MOUSEBUTTONDOWN:
					# pos = (pygame.mouse.get_pos() [0], pygame.mouse.get_pos() [1])
					# pygame.draw.circle(pantalla, cRED, pos, 2, 0)
					# print("llamo a dameletra. Pos=("+str(pos[0])+","+str(pos[1])+")")
					# # Comprobamos si hemos pulsado una tecla
					# letra = dameLetra(pos)
					# print("letra="+letra)
					# if (letra != ''):
						# strPlayerName = strPlayerName + letra
						# strPlayerName = "Paco"
						# pygame.draw.rect(pantalla,cWHITE,(20,66,450,105))
						# mensaje = fuente.render(strPlayerName, 1, cBLUE)
						# pantalla.blit(mensaje, (240-mensaje.get_rect().width/2, 73))
						# pygame.display.flip()

			# if (btnPressed == btnRed):			# El usuario pulsa el BOTON RED pasamos a PREGUNTAS
				# currentPhase = f_QUESTIONS
				# looping = False
			# if (btnPressed == btnYellow):		# El usuario pulsa el BOTON YELLOW borramos la ultima letra del nombre
				# if (len(strPlayerName) > 0):
					# strPlayerName = strPlayerName[:-1]
					# #borrar la ultima letra del nombre
					# pygame.draw.rect(pantalla,cWHITE,(20,66,450,105))
					# mensaje = fuente.render(strPlayerName, 1, cBLUE)
					# pantalla.blit(mensaje, (240-mensaje.get_rect().width/2, 73))
					# pygame.display.flip()
			# if (btnPressed == btnBlue):			# El usuario pulsa el BOTON BLUE salimos al MENU
				# currentPhase = f_MENU
				# looping = False

			if (btnPressed == btnRed):			# El usuario pulsa el BOTON RED añadimos letra
				btnPressed = -1
				if iLetra == 27:
					strPlayerName = strPlayerName[:-1]
				else:
					if len(strPlayerName)<15:
						strPlayerName = strPlayerName + aLetras[iLetra]
				# Limpia la pantalla y establece su color de fondo
				pantalla.fill(cWHITE)
 				# Muestra la pantalla inicial en pantalla:
				imagen = pygame.image.load("./quiz_pantalla_21_NOMBRE_ingles.png").convert()
				pantalla.blit(imagen, posicion_base)
				fuente = pygame.font.SysFont('arial', 24)
				mensaje = fuente.render(strPlayerName, 1, cBLUE)
				pantalla.blit(mensaje, (240-mensaje.get_rect().width/2, 73))
				fuente = pygame.font.SysFont('arial', 64)
				mensaje = fuente.render(aLetras[iLetra], 1, cBLUE)
				pantalla.blit(mensaje, (240-mensaje.get_rect().width/2, 130))
				pygame.display.flip()
				pygame.mixer.music.load(sound_click)
				pygame.mixer.music.play(0)
			if (btnPressed == btnYellow):		# El usuario pulsa el BOTON YELLOW pasamos a anterior letra
				btnPressed = -1
				iLetra = iLetra - 1
				if iLetra < 0:
					iLetra = 27
				# Limpia la pantalla y establece su color de fondo
				pantalla.fill(cWHITE)
 				# Muestra la pantalla inicial en pantalla:
				imagen = pygame.image.load("./quiz_pantalla_21_NOMBRE_ingles.png").convert()
				pantalla.blit(imagen, posicion_base)
				fuente = pygame.font.SysFont('arial', 24)
				mensaje = fuente.render(strPlayerName, 1, cBLUE)
				pantalla.blit(mensaje, (240-mensaje.get_rect().width/2, 73))
				fuente = pygame.font.SysFont('arial', 64)
				mensaje = fuente.render(aLetras[iLetra], 1, cBLUE)
				pantalla.blit(mensaje, (240-mensaje.get_rect().width/2, 130))
				pygame.display.flip()
				pygame.mixer.music.load(sound_click)
				pygame.mixer.music.play(0)
			if (btnPressed == btnGreen):		# El usuario pulsa el BOTON GREEN pasamos a siguiente letra
				btnPressed = -1
				iLetra = iLetra + 1
				if iLetra > 27:
					iLetra = 0
				# Limpia la pantalla y establece su color de fondo
				pantalla.fill(cWHITE)
				imagen = pygame.image.load("./quiz_pantalla_21_NOMBRE_ingles.png").convert()
				pantalla.blit(imagen, posicion_base)
				fuente = pygame.font.SysFont('arial', 24)
				mensaje = fuente.render(strPlayerName, 1, cBLUE)
				pantalla.blit(mensaje, (240-mensaje.get_rect().width/2, 73))
				fuente = pygame.font.SysFont('arial', 64)
				mensaje = fuente.render(aLetras[iLetra], 1, cBLUE)
				pantalla.blit(mensaje, (240-mensaje.get_rect().width/2, 130))
				pygame.display.flip()
				pygame.mixer.music.load(sound_click)
				pygame.mixer.music.play(0)
			if (btnPressed == btnBlue):			# El usuario pulsa el BOTON BLUE continuamos
				currentPhase = f_QUESTIONS
				looping = False

	# -------- Bucle de PREGUNTAS -----------
	if (playing and (currentPhase == f_QUESTIONS)):
		instanteInicial = datetime.now()
		score = 0
		score = int(score)  #Convert the 0 into a number so we can add scores

		NResponse = 10
		nRespuesta = 0
		
		#Cargo desde fichero
		#data = json.load(open('./test.json'))

		#Cargo desde URL
		url = 'https://opentdb.com/api.php?amount=10&category=9&difficulty=easy&type=multiple'
		#url = 'https://opentdb.com/api.php?amount=10&type=multiple'
		req = urllib.request.Request(url)
		r = urllib.request.urlopen(req).read()
		data = json.loads(r.decode('utf-8-sig'))

		#Cargo desde generadores
		#data = json.loads(generaPreguntasPrimaria())
		
		while (nRespuesta < NResponse):
			# Limpia la pantalla y establece su color de fondo
			pantalla.fill(cWHITE)
			# Muestra la pantalla de fondo de la pregunta:
			imagen = pygame.image.load("./quiz_pantalla_231_RESPUESTASLARGAS_ingles.png").convert()
			pantalla.blit(imagen, posicion_base)
			
			# Escribe la pregunta
			#print ('PREGUNTA NÚMERO ' + str(nRespuesta+1) + ': ' + data['results'][nRespuesta]['question'])
			fuente = pygame.font.SysFont('./Fonts/Antonio-Bold.ttf', 36)

			txtPregunta = 'PREGUNTA ' + str(nRespuesta+1)
			#render(texto,1,color)
			mensaje = fuente.render(txtPregunta, 1, cBLUE)
			pantalla.blit(mensaje, (40, 10))

			fuente = pygame.font.SysFont('./Fonts/Antonio-Light.ttf', 28)
			txtPregunta = data['results'][nRespuesta]['question'].replace('"','\\"').replace("'","\\'").replace("&shy;",'').replace("&quot;",'"').replace('&#039;',"'")
			if len(txtPregunta)<=45:
				txtLinea1 = txtPregunta
				mensaje = fuente.render(txtPregunta, 1, cBLUE)
				pantalla.blit(mensaje, (40, 55))
			elif len(txtPregunta)<=90:
				txtLinea1 = txtPregunta[:45]
				txtLinea2 = txtPregunta[45:]
				mensaje = fuente.render(txtLinea1, 1, cBLUE)
				pantalla.blit(mensaje, (40, 47))
				mensaje = fuente.render(txtLinea2, 1, cBLUE)
				pantalla.blit(mensaje, (40, 73))
			else:
				txtLinea1 = txtPregunta[:45]
				txtLinea2 = txtPregunta[45:]
				txtLinea3 = txtLinea2[45:]
				txtLinea2 = txtLinea2[:45]
				mensaje = fuente.render(txtLinea1, 1, cBLUE)
				pantalla.blit(mensaje, (40, 47))
				mensaje = fuente.render(txtLinea2, 1, cBLUE)
				pantalla.blit(mensaje, (40, 66))
				mensaje = fuente.render(txtLinea3, 1, cBLUE)
				pantalla.blit(mensaje, (40, 85))

			randomnumber = randint(0, 3)
			i = 0
			nr = 0;
			respuesta = "";
			while (i < 4):
				if (i == randomnumber):
					txtRespuesta = data['results'][nRespuesta]['correct_answer'].replace('"','\\"').replace("'","\\'").replace('&shy;','').replace('&quot;','"').replace('&#039;',"'")
					# Escribe la respuesta
					fuente = pygame.font.SysFont('./Antonio-Bold.ttf', 28)
					mensaje = fuente.render(txtRespuesta, 1, cBLUE)
					pantalla.blit(mensaje, (142, 129+i*50))
				else:
					txtRespuesta = data['results'][nRespuesta]['incorrect_answers'][nr].replace('"','\\"').replace("'","\\'").replace('&shy;','').replace('&quot;','"').replace('&#039;',"'")
					# Escribe la respuesta
					fuente = pygame.font.SysFont('./Antonio-Bold.ttf', 28)
					mensaje = fuente.render(txtRespuesta, 1, cBLUE)
					pantalla.blit(mensaje, (142, 129+i*50))
					nr = nr + 1
				i = i + 1

			# Limitamos a 60 fotogramas por segundo.
			reloj.tick(20)
 
			# Avancemos y actualicemos la pantalla con lo que hemos dibujado.
			pygame.display.flip()

			pygame.mixer.music.load(sound_click)
			pygame.mixer.music.play(0)
	
			# Esperamos pulsacion de boton
			btnPressed = -1
			qResponse = ' '
			looping = True
			while (looping):
				if (btnPressed == btnRed):			# El usuario pulsa el BOTON RED 
					btnPressed = -1
					qResponse = '0'
					looping = False
				if (btnPressed == btnYellow):		# El usuario pulsa el BOTON YELLOW 
					btnPressed = -1
					qResponse = '1'
					looping = False
				if (btnPressed == btnGreen):		# El usuario pulsa el BOTON GREEN
					btnPressed = -1
					qResponse = '2'
					looping = False
				if (btnPressed == btnBlue):			# El usuario pulsa el BOTON BLUE
					btnPressed = -1
					qResponse = '3'
					looping = False

				#Actualizo reloj
				instanteFinal = datetime.now()
				tiempo = instanteFinal - instanteInicial
				segundos = tiempo.seconds
				pygame.draw.rect(pantalla,cWHITE,(280,0,479,50))
				fuente = pygame.font.Font('./Antonio-Regular.ttf', 18)
				txtPregunta = 'Tiempo: ' + str(segundos) + ' segundos'
				mensaje = fuente.render(txtPregunta, 1, cBLACK)
				pantalla.blit(mensaje, (380-mensaje.get_rect().width/2, 20))

				# Limitamos a 60 fotogramas por segundo.
				reloj.tick(20)
 
				# Avancemos y actualicemos la pantalla con lo que hemos dibujado.
				pygame.display.flip()

			if (qResponse != str(randomnumber)):
				# Limpia la pantalla y establece su color de fondo
				pantalla.fill(cWHITE)

				# Muestra la pantalla de ERROR:
				imagen = pygame.image.load("./Images/quiz_pantalla_26_ERROR_ingles.png").convert()
				pantalla.blit(imagen, posicion_base)

				# Limitamos a 60 fotogramas por segundo.
				reloj.tick(20)
 
				# Avancemos y actualicemos la pantalla con lo que hemos dibujado.
				pygame.display.flip()
				
				pygame.mixer.music.load(sound_error)
				pygame.mixer.music.play(0)
	
				# Esperamos 3 segundos
				time.sleep(3)
			else:
				# Limpia la pantalla y establece su color de fondo
				pantalla.fill(cWHITE)
 
				# Muestra la pantalla CORRECTO:
				imagen = pygame.image.load("./Images/quiz_pantalla_25_CORRECTO_ingles.png").convert()

				pantalla.blit(imagen, posicion_base)

				# Limitamos a 60 fotogramas por segundo.
				reloj.tick(20)
 
				# Avancemos y actualicemos la pantalla con lo que hemos dibujado.
				pygame.display.flip()
				
				pygame.mixer.music.load(sound_applause)
				pygame.mixer.music.play(0)
			
				# Esperamos 3 segundos
				time.sleep(3)
				score = score + 1
				
			instanteFinal = datetime.now()
			tiempo = instanteFinal - instanteInicial
			segundos = tiempo.seconds
			
			# Mostramos los resultados parciales
			#print ('Llevas acertadas ' + str(score) + ' de ' + str(nRespuesta+1)+' en ' + str(segundos) + ' segundos.\n')
			nRespuesta = nRespuesta + 1
			
		instanteFinal = datetime.now()
		tiempo = instanteFinal - instanteInicial
		segundos = tiempo.seconds
		minu=int(segundos/60)
		seg=segundos-minu*60
		
		# Mostramos los resultados finales
		#print ('Tu resultado final es ' + str(score) + ' acertadas de ' + str(NResponse) + ' en un tiempo de ' + str(minu) + ':' + str(seg) + '.\n')

		# Borrar pantalla
		pantalla.fill(cWHITE)

		# Muestra la pantalla de fondo de la pregunta:
		imagen = pygame.image.load("./Images/quiz_pantalla_24_RESULTADOS_ingles.png").convert()
		pantalla.blit(imagen, posicion_base)
			
		#Escribe el texto
		fuente = pygame.font.SysFont('arial', 32)
		txtResultados = strPlayerName
		mensaje = fuente.render(txtResultados, 1, cBLUE)
		pantalla.blit(mensaje, (240-mensaje.get_rect().width/2, 70))
		
		fuente = pygame.font.Font('./Antonio-Bold.ttf', 36)
		if (score >=10):
			txtResultados = '¡ PERFECT !'
		elif (score >=7):
			txtResultados = '¡ VERY GOOD !'
		elif (score >=5):
			txtResultados = '¡ NOT BAD !'
		elif (score >=3):
			txtResultados = '¡ BAD !'
		elif (score < 3):
			txtResultados = '¡ DISASTROUS !'
		else:
			txtResultados = '¡ ERROR !'
		mensaje = fuente.render(txtResultados, 1, cBLUE)
		pantalla.blit(mensaje, (240-mensaje.get_rect().width/2, 115))
		
		fuente = pygame.font.Font('./Antonio-Bold.ttf', 24)
		txtResultados = 'You have succesfully answered ' + str(score) + ' of ' + str(NResponse) + ' questions'
		mensaje = fuente.render(txtResultados, 1, cBLUE)
		pantalla.blit(mensaje, (240-mensaje.get_rect().width/2, 185))
		txtResultados = 'with a time of ' + str(segundos) + ' seconds.'
		mensaje = fuente.render(txtResultados, 1, cBLUE)
		pantalla.blit(mensaje, (240-mensaje.get_rect().width/2, 215))

		# Añadimos a los mejores y nos quedamos con los 10 primeros
		# Recuperamos el fichero de mejores
		high_scores = {}
		if (os.path.exists('./losmejores.txt')) and (os.path.getsize('./losmejores.txt')>0):
			high_scores = json.load(open('./losmejores.txt'))
		else:
			high_scores = {}

		if len(high_scores) == 0:
			#Fichero estaba vacio, rellenamos high_scores con el resultado
			array_scores = []
		else:
			array_scores = high_scores["lista"]
		array_scores.append((strPlayerName,score,NResponse,segundos,score*100/NResponse,segundos/score))
		array_scores = sorted(sorted(sorted(array_scores, key=itemgetter(3), reverse=False), key=itemgetter(2), reverse=True), key=itemgetter(4), reverse=True)[:10]
		nuevo_high_scores = {}
		nuevo_high_scores["lista"] = array_scores

		with open('./losmejores.txt', 'w') as outfile:
			json.dump(nuevo_high_scores, outfile)		
		
		# Limitamos a 60 fotogramas por segundo.
		reloj.tick(20)

		# Avancemos y actualicemos la pantalla con lo que hemos dibujado.
		pygame.display.flip()
				
		pygame.mixer.music.load(sound_drumroll)
		pygame.mixer.music.play(0)
		pygame.mixer.music.load(sound_tada)
		pygame.mixer.music.play(0)
	
		# Esperamos pulsacion de boton
		btnPressed = -1
		looping = True;
		while (looping):
			if (btnPressed == btnRed):			# El usuario pulsa el BOTON RED 
				btnPressed = -1
				currentPhase = f_HIGHSCORES
				looping = False;
		
# Pórtate bien con el IDLE. Si nos olvidamos de esta línea, el programa se 'colgará'
# en la salida.
pygame.quit()
