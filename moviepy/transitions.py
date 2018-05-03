from moviepy.editor import *
import constants as ssc
import easing as eas
import moviepy.video.fx.all as vfx
import tools
#eas = __import__('easing',globals(),locals(),['*'],-1)
#ssc = __import__('constants',globals(),locals(),['*'],-1)

def t_concat(v1,v2,scsize=ssc.SCSIZE,t_time=ssc.TRAN_TIME):
	return concatenate_videoclips([v1,v2],padding=-t_time,method="compose")

def t_fade(v1,v2=None,scsize=ssc.SCSIZE,t_time=ssc.TRAN_TIME):
	if v2 == None:
		v1 = v1.crossfadein(t_time)
	else:
		v2 = v2.crossfadein(t_time)
	return t_concat(v1, v2)

def t_slideright(v1,v2=None,scsize=ssc.SCSIZE,t_time=ssc.TRAN_TIME,easefxn=None):
	if easefxn == None:
		easefxn = eas.easeOutExpo
	if v2 == None:
		v1 = CompositeVideoClip([v1.set_pos(lambda a: (easefxn(a,scsize[0],0-scsize[0],t_time),0))],size=scsize)
		return v1
	else:
		v1 = CompositeVideoClip([v1.set_pos(lambda a: (eas.tranOut(v1.duration,easefxn,a,0,-scsize[0],t_time),0))],size=scsize)
		v2 = CompositeVideoClip([v2.set_pos(lambda a: (easefxn(a,scsize[0],0-scsize[0],t_time),0))],size=scsize)
		return t_concat(v1, v2)

def t_boxout(v1,v2,scsize=ssc.SCSIZE,t_time=ssc.TRAN_TIME,easefxn=None):
	if easefxn == None:
		easefxn = eas.easeOutExpo
	nv1 = v1.set_pos('center').fx(vfx.resize, lambda a: eas.tranOut(v1.duration,easefxn,a,1,0.01-1,t_time))
	return CompositeVideoClip([v2.set_start(nv1.duration-t_time),nv1],size=scsize)
