from moviepy.editor import *
import moviepy.video.fx.all as vfx
import transitions as tran
import constants as ssc
import time, requests, os, subprocess
from urlparse import urlparse
import uuid
# ssc = __import__('constants',globals(),locals(),['*'])
# tran = __import__('transitions',globals(),locals(),['*'])

class StyxScene(object):
	def __init__(self,sinfo,tpl):
		self.sinfo = sinfo
		self.method = sinfo['type']
		self.params = sinfo['params']
		self.intrans = sinfo['trans']
		self.tpl = tpl

	def process(self):
		self.result = getattr(self.tpl,self.method)()
		return self

	def render(self):
		pass

	def preview(self):
		pass

	def destroy(self):
		del self.result

class CombinedStyxScene(StyxScene):
	def __init__(self, s1, s2):
		objpass = {"combined":[s1.sinfo,s2.sinfo],"type":"--combined--","params":{},"trans":s2.intrans}
		super(CombinedStyxScene,self).__init__(objpass,s2.tpl)
		# print 'put something for',s2.method,'with',self.intrans
		transition = getattr(tran, 't_'+self.intrans)
		if 'bundled' in s2.sinfo:
			if len(s2.result) > 1:
				s2.result = reduce(lambda x,y: transition(x,y,scsize=s2.tpl.screensize), s2.result)
			elif len(s2.result) > 0:
				s2.result = s2.result[0]
			else:
				self.result = s1.result
				return
		self.result = transition(s1.result,s2.result,scsize=s2.tpl.screensize)

	def destroy(self):
		pass

class CoreTemplate(object):
	def __init__(self,screensize=ssc.SCSIZE):
		self.screensize = screensize
		self.allimages = []
		self.imgcnt = 0
		self.scenemargin = (0,0,0,0) #(up,right,down,left)

	def set_scenemargin(self,val):
		if type(val) is list:
			self.scenemargin = val
		else:
			self.scenemargin = (val,val,val,val)

	def genTS(self):
		return int(time.time())

	def _fnamesplit(self, url):
		urll = urlparse(url)
		fname, fext = os.path.splitext(urll.path)
		return (fname, fext)

	def grabImage(self,url):
		# print 'grabbing file '+url
		r = requests.get(url)
		fout = self._fnamesplit(url)
		cur_dir=os.path.dirname(os.path.realpath(__file__))
		fname = cur_dir+'/tempimages/img_' + str(self.genTS()) + str(self.imgcnt) + fout[1]
		#fname = os.getcwd()+'/tempimages/img_' + str(self.genTS()) + str(self.imgcnt) + fout[1]
		self.imgcnt+=1
		f = open(fname,'w+')
		# print 'writing file '+url
		f.write(r.content)
		f.close()
		self.allimages.append(fname)
		return fname

	def truncate_string(self,strd,chlen=150):
		return (strd[:150] + '..') if len(strd) > 250 else strd

	def processScenes(self,datascenes):
		self.scenes = [StyxScene(scene,self).process() for scene in datascenes]
		return self.scenes

	def putMarginOnScene(self,scene,margin):
		lepos = (margin[3],margin[0])
		lesize = (self.screensize[0]-(margin[1]+margin[3]), self.screensize[1]-(margin[0]+margin[2]))
		return scene.set_pos(lepos).resize(lesize)

	def mergeScenes(self):
		if not hasattr(self,'scenes'):
			raise ValueError("Could not find merged scenes. Unable to create.")
		self.merged = reduce( lambda x, y: CombinedStyxScene(x,y), self.scenes )
		#print(self.scenemargin)
		self.merged.result = self.putMarginOnScene(self.merged.result,self.scenemargin)

	def gatherDefaults(self):
		if not hasattr(self,'bg'):
			self.bg = ImageClip(ssc.DEFWP)
		if not hasattr(self,'bgaudio'):
			self.bgaudio = AudioFileClip(ssc.DEFNOTE)	

	def wrapUp(self):
		if hasattr(self,'nocompile'):
			return
		if not hasattr(self,'merged'):
			raise ValueError("Could not find merged scenes. Unable to create.")
		#self.gatherDefaults()
		if hasattr(self,'finalize'):
			self.finalize()
		thevid = self.merged.result
		auds = self.bgaudio.subclip(0,thevid.duration).audio_fadeout(self.speedslide)
		self.composition = CompositeVideoClip([self.bg,thevid.fx(vfx.fadeout, 1)],size=self.screensize).set_audio(auds).subclip(0,thevid.duration)
		# self.composition = CompositeVideoClip([thevid.fx(vfx.fadeout, 1)],size=self.screensize).subclip(0,thevid.duration)
		#print(self.composition)

	def removeImages(self):
		return [os.remove(f) for f in self.allimages]
		#pass

	def ipython(self):
		vout = ipython_display(self.composition,fps=25,codec='mpeg4' )
		self.removeImages()
		return vout

	def writevid(self):
		myHashId=self.createuuid()
		vidloc = 'composer/tempimages/'+str(myHashId)+'-'+'video.mp4'
		vout = self.composition.write_videofile(vidloc,fps=25,codec='mpeg4' )
		self.removeImages()
		#self.composition.close()
		return vidloc

	def destroy(self):
		del self.composition

	def createuuid(self):
		return uuid.uuid4()

