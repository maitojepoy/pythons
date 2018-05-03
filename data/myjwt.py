import jwt

def getmykeys():
	conf = {}
	conf['key_nonlogin'] = "d460d31c5a68afa07e7c8c1003781bbe"
	conf['key_login'] = "3ba0f6fc6c8b674544213ae9c7ac0172"

	# These are for the hashed passwords
	conf['key_salt'] = "1252e61e1b9b6fa12a184b64dd0eeee1";
	conf['hash_salt'] = "10-5-6-6"; # stands for jeff
	return conf

class MyJWT:
	def __init__(self):
		self.mkeys = mk.getmykeys()
		self.nonloginkey = self.mkeys['key_nonlogin']
		self.loginkey = self.mkeys['key_login']

	def decode(self,token,type):
		if (type == "login"):
			key = self.loginkey
		else:
			key = self.nonlogin_key
		return jwt.decode(token, key)

	def is_valid(self,token,islogin=True):
		if (islogin): ttype = 'login'
		else: ttype = 'nonlogin'
		try:
			decode = self.decode(token,ttype)
		except:
			return False
		if (decode['data'] == None):
			return False
		else:
			return True