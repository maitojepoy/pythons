import os
cwd = os.getcwd()

def get_rsrc_dir():
	#up to the cloud
	# return "https://storage.googleapis.com/sfinal/templates/"
	#just local
	#return "/home/jov/work/templates/"
	return cwd


RANDY = get_rsrc_dir()+'randy.mp4'

DEFNOTE = get_rsrc_dir()+'defaudio.mp3'

DEFBG = get_rsrc_dir()+'defwp.jpg'

#720p
#SCSIZE = (1280,720)
SCSIZE = (720,460)

TRAN_TIME = 0.6

