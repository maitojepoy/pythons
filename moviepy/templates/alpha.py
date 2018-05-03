from moviepy.editor import *
#from . import easing as ease
#from . import constants as ssconst
#from . import maker
ease = __import__('easing',globals(),locals(),['*'],-1)
ssconst = __import__('constants',globals(),locals(),['*'],-1)
maker = __import__('maker',globals(),locals(),['*'],-1)

CoreTemplate = maker.CoreTemplate

class TemplateAlpha(CoreTemplate):
	def __init__(self,scsize=ssconst.SCSIZE):
		print 'begin'
		super(TemplateAlpha,self).__init__(scsize)
		self.defloc = ssconst.get_rsrc_dir() + "_alpha/"
		self.screensize = scsize
		self.textcolor = 'white'
		self.font = 'Helvetica-Narrow'
		self.fontbold = 'Helvetica-Narrow-Bold'
		self.fz_h1 = 72	
		self.fz_h2 = 64
		self.kern = 0
		self.speedslide = 1
		self.defEase = ease.easeOutExpo
		self.makebackdrop()
		self.marginslide = int(self.screensize[0] * 0.0138889)
		self.set_scenemargin(self.marginslide)
		#self.areaslide = [sz-self.marginslide*2 for sz in self.screensize]

	def makebackdrop(self):
		aimg = ImageClip(self.defloc+'patdemo.png').set_pos(lambda a: ('left',ease.linearTween(a,0,-139,10))).set_duration(10)
		self.bg = CompositeVideoClip([aimg],size=self.screensize).fx(vfx.loop)

	def headline(self,params):
		text1 = params.get('text1','Introducing')
		text2 = params.get('text2','Shopstyx')
		startanim = 1
		bgc = ColorClip(self.screensize,col=(200,200,200))
		bgcanim = bgc.set_duration(2)
		#bgcanim = bgc.set_duration(2).resize(lambda a: (easeOutExpo(a,100,self.areaslide[0]-100,self.speedslide),self.areaslide[1]))
		#bgcanim = bgcanim.set_mask(bgca)
		offstt = .5
		txts = [text1,text2]
		txtsfzs = [self.fz_h1,self.fz_h2]
		txtsff = [self.font,self.fontbold]
		outt = [ TextClip(o,color=self.textcolor, font=txtsff[i], kerning = self.kern, fontsize=txtsfzs[i]) for i,o in enumerate(txts) ]
		outt[1] = outt[1].set_start(offstt)
		desty = [170,250]
		srcy = self.screensize[1]
		showCenter = lambda o,src,dest: o.set_pos(lambda a: ('center', self.defEase(a,src,dest-src,self.speedslide)))
		outt = [showCenter(txti,srcy,desty[i]) for i,txti in enumerate(outt)]
		aa = CompositeVideoClip([bgc,outt[0],outt[1]],size=self.screensize).subclip(0,self.speedslide*2+offstt)
		cret = concatenate_videoclips([bgcanim,aa],method="compose")
		return cret.subclip(0,cret.duration)

	def videoout(self,params):
		src = params.get('src', ssconst.RANDY)
		drange = params.get('drange',(0,7))

		vid = VideoFileClip(src,audio=False).resize(self.screensize).subclip(drange[0],drange[1])
		return CompositeVideoClip([vid],size=self.screensize)