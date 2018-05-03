from . import myjwt as sj
import json

class RequestSec:

	def __init__(self):
		print 'API Tool ready'
		self.tokener = sj.SSJWT()

	def validate_token(self,dataobj):
		security = dataobj['security']
		if (self.tokener.is_valid(security['token']) == False):
			outjs = self.apiOut(success=False,code=-1,message='session does not match',error_msg='session_not_match')
		else: 
			outjs = self.apiOut(success=True,message='session valid',result=dataobj)
		return outjs

	def isAssumedLogged(self,dout):
		if (dout['security']['user_id'] != None): return True
		else: return False

	def genericChecks(self,request,needed='',logged_in=True,skip_token=False):
		global login_userid 

		dataout = json.loads(request.POST.get('data'))
		if (dataout == None):
			return self.apiOut(success=False,code=-2,message='missing parameter',error_msg='missing_parameters')

		if (isinstance(needed, list) == True):
			if (dataout['request'] == None):
				return self.apiOut(success=False,code=-3,message='missing request parameter',error_msg='missing_request_param')
			else: 
				missings = self.findRequirements(dataout['request'],needed)
				if (isinstance(missings,list) == True):
					misstrings = 'missing ' + ', '.join(missings)
					return self.apiOut(success=False,code=-4,message=misstrings,error_msg='missing_request_param')

		if (skip_token == False):
			
			#is token valid?
			if (dataout['security'] == None or dataout['security']['token'] == None):
				return self.apiOut(success=False,code=-5,message='cant find token',error_msg='missing_token')
			if (logged_in): typelog = 'login'
			else: typelog = 'nonlogin'
			vald = self.validate_token(dataout)
			if (vald['success'] == False): return vald
			
			#does a uid inside token matches security.user_id?
			if (logged_in):
				if (dataout['security']['user_id'] == None):
					return self.apiOut(success=False,code=-6,message='missing user_id',error_msg='missing_uid')

				uid = dataout['security']['user_id']
				dectok = self.tokener.decode(dataout['security']['token'],'login')
				login_userid = dectok['data']['user_id']
				if (dectok['data']['user_id'] == None):
					return self.apiOut(success=False,code=-6,message='missing uid in token',error_msg='missing_token_uid')
				if (int(dectok['data']['user_id']) != int(uid)):
					return self.apiOut(success=False,code=-6,message='uid in token does not match',error_msg='token_uid_mismatch')
		
		return self.apiOut(success=True,message='data valid',result=dataout)

	def whoisuser(request):
		test = login_userid
		return test


	def findRequirements(self, data, reqs):
		err = False 
		missing = []
		for r in reqs:
			if (data[r] == None):
				missing.append(r)
				err = True
		if (err):
			return missing
		else:
			return False
	
	def apiOut(self,**op):
		toout = {}

		if (op.get('success') == None): toout['success'] = True
		else: toout['success'] = bool(op.get('success'))

		if (toout['success'] == True and op.get('code') == None): 
			toout['code'] = 0

		if (toout['success'] == False):
			if (op.get('code') == None): toout['code'] = -1
			if (op.get('error_msg') != None):
				toout['error_msg'] = op.get('error_msg')
			else:
				toout['error_msg'] = "Error"

		if (op.get('message') == None):
			if (toout['success'] == True): 
				toout['message'] = 'Success'
		else: toout['message'] = op.get('message')

		if (op.get('result') != None): 
			toout['data'] = op.get('result')

		if (op.get('extra') != None):
			toout['extra'] = op.get('extra')

		return toout