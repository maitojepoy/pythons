import constants as ssc
import maker

#group of scenes = composition
class StyxComposition:
	def __init__(self, tdata, size=ssc.SCSIZE):
		self.cdata = tdata
		self.screensize = size

	def getTpl(self, tid):
		if (tid == 0): 
			return None
		_NAH = "--nahnah---"
		templist = {
			0: _NAH,
			1: ["alpha","TemplateAlpha"],
		}
		#add more soon
		template = templist.get(tid, _NAH)
		if (template == _NAH):
			return None
		return [__import__('templates.'+template[0],globals(),locals(),['*']),template[1]]

	def begin(self):
		#print self.cdata['tpl']

		self.theTpl = self.getTpl(self.cdata['tpl'])
		if (self.theTpl == None):
			raise ValueError("Could not find tpl value %n in template list" % (self.cdata['tpl']))
		self.tpl = getattr(self.theTpl[0],self.theTpl[1])(scsize=self.screensize)
		self.tpl.processScenes(self.cdata['scenes'])
		self.tpl.mergeScenes()
		self.tpl.wrapUp()
		print('done')

	def debug_preview(self):
		return self.tpl.ipython()

	def render(self,scene=None):
		return self.tpl.writevid()

	def destroy_tpl(self):
		self.tpl.destroy()
		del self.tpl