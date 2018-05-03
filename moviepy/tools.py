"""

moviepy tools
includes cropping and animation

"""


import moviepy.video.fx.all as vfx
from moviepy.video.tools.drawing import color_gradient
from moviepy.editor import *
import easing as eas
import numpy as np

def gcd(a,b):
	if b==0:
		return a
	return gcd(b,a%b)

def aspect_ratio(w,h):
	cd = gcd(w,h)
	return w/cd,h/cd

def basis_crop(size1,size2):
	w1, w2 = size1
	h1, h2 = size2
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

def clip_brush_fade_in(clip,dir='r',dur=0.5,easefxn=None):
	if easefxn == None:
		easefxn = eas.easeOutExpo
	csize = clip.size
	#create mask
	if dir == 'r' or dir == 'l':
		msize = (csize[0]*3,csize[1])
		rd = csize[0]
	else:
		msize = (csize[0],csize[1]*3)
		rd = csize[1]
	themask = create_linear_mask_clip(msize,dir)

	#grad = color_gradient(moving_txt.size,p1=(0,2*h/3),
	#            p2=(0,h/4),col1=0.0,col2=1.0)
	#gradmask = ImageClip(grad,ismask=True)

	#let us make animation - using the mask mismo
	rpt = -rd*2
	lpt = 0
	if dir == 'r' or dir == 'l':
		if dir == 'r':
			maskanim = themask.set_pos( lambda a: ( easefxn(a, rpt, lpt-rpt, dur ), 0))
		else:
			maskanim = themask.set_pos( lambda a: ( easefxn(a, lpt, rpt-lpt, dur ), 0))
	elif dir == 'u' or dir == 'd':
		if dir == 'u':
			maskanim = themask.set_pos( lambda a: ( 0, easefxn(a, rpt, lpt-rpt, dur )))
		else:
			maskanim = themask.set_pos( lambda a: ( 0, easefxn(a, lpt, rpt-lpt, dur )))

	maskappl = CompositeVideoClip([maskanim], size=csize, ismask=True)

	return CompositeVideoClip([clean_after_mask(clip.set_mask(maskappl))], size=csize)

def clean_after_mask(clip):
	return clip.fx(vfx.mask_color, color=(0,0,0))

def center_crop(img, size):
		newsize = dim_resize(img.size,size)
		return img.resize(newsize).fx(vfx.crop,x_center=newsize[0]/2,y_center=newsize[1]/2,width=size[0],height=size[1])

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
    shape = (h, w)
    dm = np.zeros(shape)
    dm[:,:] = 1
    dm[thick:h-thick,thick:w-thick] = 0
    i = ImageClip(dm,ismask=True)
    c = ColoredClip((w,h),color)
    return c.set_mask(i)

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
