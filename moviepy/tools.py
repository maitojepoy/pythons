"""

moviepy tools
includes cropping and animation

"""


import moviepy.video.fx.all as vfx
from moviepy.video.tools.drawing import color_gradient
from moviepy.editor import *
import easing as eas
import numpy as np
import math

def gcd(a,b):
	if b==0:
		return a
	return gcd(b,a%b)

def aspect_ratio(w,h):
	cd = gcd(w,h)
	return w/cd,h/cd

def basis_crop(size1,size2):
	w1, h1 = np.array(size1).astype('float').tolist()
	w2, h2 = np.array(size2).astype('float').tolist()
	i1 = aspect_ratio(w1,h1)
	i2 = aspect_ratio(w2,h2)
	diffw = i1[0]-i2[0]
	diffh = i1[1]-i2[1]
	if diffw > diffh:
		return 'h'
	else:
		return 'w'

def _dim_resize_value(size,val,baseon='w'):
	if baseon=='w':
		return size[1]*val/size[0]
	else:
		return size[0]*val/size[1]

def dim_resize(src,targ):
	basis = basis_crop(src,targ)
	vuse = 0
	# print src
	# print targ
	if basis == 'w': 
		vuse = targ[0]
	else: 
		vuse = targ[1]
	# print vuse, basis
	vres = _dim_resize_value(src,vuse,basis)
	if basis == 'w':
		return targ[0], vres
	else:
		return vres, targ[1]

def scaleDim(size,perc):
	wn = size[0] * perc
	hn = _dim_resize_value(size,wn,'w')
	return wn, hn

def flip_clip(clip,dir='h'):
	if dir == 'h':
		return clip.fx(vfx.mirror_x)
	else:
		return clip.fx(vfx.mirror_y)

def fade_it(clip,to='in',easefxn=None,dur=0.5):
	if easefxn==None:
		easefxn = eas.easeOutQuad
	if to=='in':
		i = 0.
		o = 1.
	else:
		i = 1.
		o = 0.
	def fl(gf, t):
		v = eas.tween(easefxn, t, i, o-i, dur) if to=='in' else eas.tranOut(clip.duration,easefxn,t,i,o-i,dur)
		f = gf(t)
		om = np.zeros(f.shape)
		om[:,:] = 1-v
		return np.clip(f-om,0.,1.)

	clip.mask = clip.mask.fl(fl)
	return clip

def create_linear_mask_clip(lsz,dir='r'):
	if dir == 'r' or dir == 'l':
		dh = lsz[0]/3
		ph1 = (dh*1,0)
		ph2 = (dh*2,0)
		if dir == 'r':
			c1 = 0
			c2 = 1.0
		else:
			c1 = 1.0
			c2 = 0
		grad = color_gradient(lsz, p1=ph1, p2=ph2, col1=c1, col2=c2)
	elif dir == 'u' or dir == 'd':
		dh = lsz[1]/3
		ph1 = (0,dh*1)
		ph2 = (0,dh*2)
		if dir == 'u':
			c1 = 0
			c2 = 1.0
		else:
			c1 = 1.0
			c2 = 0
		grad = color_gradient(lsz, p1=ph1, p2=ph2, col1=c1, col2=c2)

	return ImageClip(grad,ismask=True)

def clip_brush_fade_in(clip,easefxn=None,dur=0.5,dir='r'):
	efxn = eas.easeOutExpo if easefxn == None else easefxn
	w, h = clip.size
	stx = 0
	edx = 0
	dtype = ''
	if dir == 'r' or dir == 'l':
		dtype = 'h'
		wsz = (w*3,h)
		dhh = wsz[0]
		dh = w
		ph1 = (dh*1,0)
		ph2 = (dh*2,0)
		if dir == 'r':
			c1 = 0
			c2 = 1.0
			stx = dhh - dh
			edx = 0
		else:
			c1 = 1.0
			c2 = 0
			stx = 0
			edx = dhh - dh
	elif dir == 'u' or dir == 'd':
		dtype = 'v'
		wsz = (w,h*3)
		dhh = wsz[1]
		dh = h
		ph1 = (0,dh*1)
		ph2 = (0,dh*2)
		if dir == 'u':
			c1 = 1.
			c2 = 0
			stx = 0
			edx = dhh - dh
		else:
			c1 = 0
			c2 = 1.
			stx = dhh - dh
			edx = 0
			
	mgrad = color_gradient(wsz, p1=ph1, p2=ph2, col1=c1, col2=c2)
	
	chx = edx - stx
	
	def fl(gf, t):
		curx = eas.tween(efxn, t, stx, chx, dur)
		curg = mgrad[:,int(curx):int(curx+dh)] if dtype=='h' else mgrad[int(curx):int(curx+dh),:]
		f = gf(t)
		om = np.zeros(f.shape)
		om[:,:] = 1-curg
		return np.clip(f-om,0.,1.)

	if clip.mask is None:
		clip = clip.add_mask()
	clip.mask = clip.mask.fl(fl)
	return clip

def clean_after_mask(clip):
	return clip.fx(vfx.mask_color, color=(0,0,0))

def center_crop(img, size):
		newsize = dim_resize(img.size,size)
		res = img.resize(newsize)
		if res.size[0]==res.size[1]:
			return res
		else:
			return res.fx(vfx.crop,x_center=newsize[0]/2,y_center=newsize[1]/2,width=size[0],height=size[1])

def create_boxtwist(clip,dur=0.5,easefxn=None):
	if easefxn == None:
		easefxn = eas.easeOutExpo
	sz = clip.size
	im = clip.ismask
	nclip = clip.set_pos('center').fx(vfx.resize, lambda a: easefxn(a,0.1,1,dur)).fx(vfx.rotate,lambda a: easefxn(a,-90,-90,dur))
	return CompositeVideoClip([nclip],size=sz,ismask=im)

def vid_stackin(clips,add_start=0,add_last=0):
	fulldur = reduce(lambda x,y: x+y, map(lambda x: x.duration, clips)) + add_last
	fd = 0 + add_start
	nvids = []
	for n in range(0,len(clips)):
		olddur = clips[n].duration
		nvids.append(clips[n].set_start(fd).set_duration(fulldur-fd))
		fd = fd + olddur
	return nvids

def colorize(clip, RGB = (1,1,1), intense=65):
    Cphos = [0.2125, 0.7154, 0.0721]

    R,G,B = 1.0*np.array(Cphos)/ sum(Cphos)
    
    def fl(im):     
        itns = np.empty(3)
        itns.fill(intense)
        col = np.array(RGB)
        im = R*im[:,:,0]
        return np.clip( np.dstack(3*[im])/itns * col ,0,255).astype('uint8')

    return clip.fl_image(fl)

def flex_flow(clips, dir='h', gap=0, return_as='array'):
	c = 0
	m = 0
	nclips = []
	for n in range(0,len(clips)):
		sw, sh = clips[n].size
		lep = clips[n].pos(0)
		oppos = lep[(1 if dir is 'h' else 0 )]
		nclips.append( clips[n].set_pos( (c,oppos) if dir is 'h' else (oppos,c) ) )
		op = sh if dir is 'w' else sw
		if m < op: m = op
		c = c + (sw if dir is 'h' else sh) + gap
	lesize = (c-gap,m) if dir is 'h' else (m,c-gap)
	return nclips if return_as is 'array' else CompositeVideoClip(nclips,size=lesize)

def makeboxborder(color,bsize,thick=3):
	w, h = bsize
	shape = (h, w) if np.isscalar(color) else (h,w,len(color))
	dm = np.zeros(shape)
	dm[:,:] = color
	dm[thick:h-thick,thick:w-thick] = 0
	return ImageClip(dm.astype('uint8'))

def makediagboxborder(color,bsize,thick=3):
    w, h = bsize
    shape = (h, w)
    dm = np.zeros(shape)
    dm[:,:] = 1
    dm[thick:h-thick,thick:w-thick] = 0
    i = ImageClip(dm,ismask=True).rotate(45)
    c = ColoredClip((w,h),color)
    return c.set_mask(i)

def makediagsquare(sqsize,top_color,bottom_color):
	psize = (sqsize,sqsize)
	shape = psize if np.isscalar(top_color) else (sqsize, sqsize, len(top_color))
	dm = np.zeros(shape)
	dm[:,:] = top_color
	rng = np.arange(sqsize)
	dm[rng, rng] = False
	dm = dm[::-1] #reverse the array, so instead of "\", its now "/""
	for x in rng:
		mrkd = 0
		for y in rng:
			if mrkd==0 and not np.any(dm[x, y]):
				mrkd=1
			if mrkd==1:
				dm[x, y] = bottom_color
	return ImageClip(dm.astype('uint8'))

def ImageTileClip(imgclip,size):
	imgnp = imgclip.get_frame(0)
	imgmsk = imgclip.mask.get_frame(0)
	w, h = size
	rep = map(lambda a: int(math.ceil(a)),(np.array(size).astype('float')/np.array(imgclip.size))[::-1].tolist())
	imgl = np.tile(imgnp,rep+[1])
	imgm = np.tile(imgmsk,rep)
	imm = ImageClip(imgm[:h,:w],ismask=True)
	return ImageClip(imgl[:h,:w].astype('uint8')).set_mask(imm)

# Another class for ColorClip so I call it ColoredClip. 
# this has "astype" at the end of numpy array generation (compatible with PIL image rotate)

class ColoredClip(ImageClip):
    """An ImageClip showing just one color.

    Parameters
    -----------

    size
      Size (width, height) in pixels of the clip.

    color
      If argument ``ismask`` is False, ``color`` indicates
      the color in RGB of the clip (default is black). If `ismask``
      is True, ``color`` must be  a float between 0 and 1 (default is 1)

    ismask
      Set to true if the clip will be used as a mask.

    col
      Has been deprecated. Do not use.
    """

    def __init__(self, size, color=None, ismask=False, duration=None, col=None):
        if col is not None:
            warnings.warn("The `ColorClip` parameter `col` has been deprecated."
                          " Please use `color` instead.", DeprecationWarning)
            if color is not None:
                warnings.warn("The arguments `color` and `col` have both been "
                              "passed to `ColorClip` so `col` has been ignored.",
                              UserWarning)
            else:
                color = col
        w, h = size
        shape = (h, w) if np.isscalar(color) else (h, w, len(color))
        dm = np.tile(color, w * h).reshape(shape)
        if not np.isscalar(color): 
        	dm = dm.astype('uint8')

        ImageClip.__init__(self, dm, ismask=ismask, duration=duration)
