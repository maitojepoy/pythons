from math import pow, fabs
import copy, random
from shadelib import _JJSHADES, _JJCOLORNAMES

_NUMERALS = '0123456789abcdefABCDEF'
_HEXDEC = {v: int(v, 16) for v in (x+y for x in _NUMERALS for y in _NUMERALS)}
LOWERCASE, UPPERCASE = 'x', 'X'

class ColorValues:

    @staticmethod
    def toRGB(triplet):
        global _HEXDEC
        return _HEXDEC[triplet[0:2]], _HEXDEC[triplet[2:4]], _HEXDEC[triplet[4:6]]
    
    @staticmethod
    def toHex(rgb, lettercase=LOWERCASE):
        return format(rgb[0]<<16 | rgb[1]<<8 | rgb[2], '06'+lettercase)

    @staticmethod
    def toHSL(triplet):
        r,g,b = triplet[0] / 255.0, triplet[1] / 255.0, triplet[2] / 255.0
        r = r / 255.0
        g = g / 255.0
        b = b / 255.0
        
        mmin = min((r,g,b))
        mmax = max((r,g,b))
        delta = mmax - mmin
        l = (mmin + mmax) / 2

        s = 0
        if l > 0 and l < 1:
            if l < 0.5:
                w = 2 * l
            else:
                w = 2 - 2 * l
            s = delta / w

        h = 0
        if delta > 0:
            if mmax == r and mmax != g: 
                h = h + (g - b) / delta
            if mmax == g and mmax != b: 
                h = h + (2 + (b - r) / delta)
            if mmax == b and mmax != r: 
                h = h + (4 + (r - g) / delta)
            h = h / 6;
        return (int(h * 255), int(s * 255), int(l * 255))

class ColorChooser(object):
    def __init__(self,col,ctbl):
        self.color_table = ctbl
        cnames = map(lambda x: x[1], _JJSHADES)
        cidx = cnames.index(col)
        self.colidx = cidx
        self.color = col
        self.colorval = '#'+_JJSHADES[cidx][0]
        self.cgrp = ctbl[self.colorval]
        # self.chosen = self.cgrp[0]
        self.chosen = self.cgrp[0] if len(self.cgrp)==0 else self.cgrp[random.randint(0,len(self.cgrp)-1)]
        self.chosenrgb = map(lambda x: ColorValues.toRGB(x[1:len(x)]), self.chosen) 

class ColorTell:
    def __init__(self):
        self.shades = []
        self.shadenames = []
        self.colnames = []
        for shade in _JJSHADES:
            _arr = copy.copy(shade)
            _rgb = ColorValues.toRGB(shade[0])
            _arr.append(_rgb)
            _arr.append(ColorValues.toHSL(_rgb))
            self.shadenames.append(shade[1])
            self.shades.append(_arr)

        for color in _JJCOLORNAMES:
            _arr = copy.copy(color)
            _rgb = ColorValues.toRGB(color[0])
            _arr.append(_rgb)
            _arr.append(ColorValues.toHSL(_rgb))
            self.colnames.append(_arr)
    
    def findBaseColor(self,cname):
        try:
            idx = self.shadenames.index(cname)
            return self.shades[idx][2]
        except:
            return (0,0,0)

    def nameThisColor(self,rgb):

        r,g,b = rgb
        h,s,l = ColorValues.toHSL(rgb)

        ndf1 = 0
        ndf2 = 0
        ndf = 0
        cl = -1
        df = -1

        for i in range(len(self.colnames)):
            crgb = self.colnames[i][3]
            chsl = self.colnames[i][4]
            if r == crgb[0] and g == crgb[1] and b == crgb[2]:
                return ((r,g,b), (r,g,b), self.findBaseColor(self.colnames[i][2]), self.colnames[i][2], True)

            ndf1 = pow(r - crgb[0], 2) + pow(g - crgb[1], 2) + pow(b - crgb[2], 2)
            ndf2 = fabs(pow(h - chsl[0], 2)) + pow(s - chsl[1], 2) + abs(pow(l - chsl[2], 2))
            ndf = ndf1 + ndf2 * 2
            if df < 0 or df > ndf:
                df = ndf
                cl = i
        
        if cl < 0:
            black = (0,0,0)
            return (black, black, black, 'Invalid Color', False)
        else:
            return (self.colnames[cl][3], self.colnames[cl][1], self.findBaseColor(self.colnames[cl][2]), self.colnames[cl][2], False)
