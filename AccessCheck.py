import netaddr
import ConfigParser, os
from netaddr import IPNetwork,IPAddress
import MySQLdb,json,inspect

class AccessCheck:
	def __init__(self, ContentId, ClientIp):
	    self.ContentId = ContentId
	    self.ClientIp = ClientIp
	    self.TrustedIPs=self.fetchFromConfig()
	    self.Acl=self.fetchACLDb()
	    self.Status=False

	def execute(self):
		if self.ClientIp in self.TrustedIPs:
			self.Status=True
			return json.dumps({"status": 1, "message": "Client is the one of trusted ips, so that it is able to access!"})
		if self.Acl==False:
			self.Status=False
			return json.dumps({"status": 0, "message": "Client Ip is not able to access!"}) 
		if len(self.Acl) != 0:
			for Acl_item in self.Acl:
				(ContentId,AclId,AclName,AclComment,AclVal1,AclVal2,AclType)=Acl_item;
				message=self.checkGeneric(AclVal1,AclVal2,AclType)
				if self.Status:
					return message
			return message
		else:
			self.Status=True
			return json.dumps({"status": 1, "message": "No ACL defined, so that everyone is able to access!"})	

	def checkGeneric(self,AclVal1,AclVal2,AclType):
		if AclType=="Network":
			result=self.checkNetwork(AclVal1,AclVal2)
		elif AclType=="IPRange":
			result=self.checkIPRange(AclVal1,AclVal2)
		else:
			result=self.checkIP(AclVal1)
		if result:
			self.Status=True
			return json.dumps({"status": 1, "message": "Client Ip is able to access!"})
		self.Status=False	
		return json.dumps({"status": 0, "message": "Client Ip is not able to access!"})

	def checkNetwork(self,Ip,Mask):
		try:
			if IPAddress(self.ClientIp) in IPNetwork(Ip+"/"+Mask):
				return True
			return False
		except:
			print self.ContentId+":An exception occured in checkNetwork function! Please check your ACL!"
			return False

	def checkIPRange(self,Ip1,Ip2):
		try:
			IPRange=list(netaddr.iter_iprange(Ip1, Ip2))
			return IPAddress(self.ClientIp) in IPRange
		except:
			print self.ContentId+":An exception occured in checkIPRange function! Please check your ACL!"
			return False

	def checkIP(self,Ip):
		try:
			if(self.ClientIp==Ip):
				return True
			return False
		except:
			print self.ContentId+":An exception occured in checkIP function! Please check your ACL!"
			return False

	def getStatus(self):
		return self.Status

	def listRange(self,Ip,Mask):
	    for ip in IPNetwork(Ip+'/'+Mask):
	        print ip

	def fetchACLDb(self):
		try:
			connection = MySQLdb.connect(host="pufferfish.private.services.okutus.com", user="arowana", passwd="5CFsmvfWfCctGUqP",db="catalog")
			cursor = connection.cursor()
			cursor.execute("select * from contentACL where contentACL.contentId='"+self.ContentId+"'")
			acl=[]
			for row in cursor.fetchall() :
				acl.append(row)
			cursor.close()
			connection.close()
			return acl
		except:
			print self.ContentId+":DB is not accessible right now!"
			return False

	def fetchFromConfig(self):
		try:
			Config = ConfigParser.ConfigParser()
			Config.read(os.path.dirname(os.path.realpath(__file__))+"/linden-host.config")
			return json.loads(Config.get("ACL","trusted_ips"))
		except:
			print self.ContentId+":An exception occured in fetchFromConfig! Please check linden-host.config and sure about whether you have entered trusted ips"
			return []

