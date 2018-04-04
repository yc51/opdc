# coding: utf-8
import sys
import os
import subprocess
import urllib2
import tempfile
import re
import ssl
from ovirtsdk.api import API
from ovirtsdk.infrastructure.errors \
	import NoCertificatesError, RequestError, ConnectionError
import re
api = None


class cloud():
	def __init__(self):
		self.sdk = OvirtApi()
		self.usb = 0
	
	def auth_user(self, username, password, url):
		res = 0
		cert_path = "/ca.crt"
		try:
			context = ssl._create_unverified_context()
			cert = urllib2.urlopen(url+cert_path, context=context).read()
			cert_file = tempfile.NamedTemporaryFile(delete=False)
			self._ca_content = cert
			cert_file.write(cert)
			cert_file.close()
			self._ca_file = cert_file.name
		except:
			self._ca_file = None
			return u"无法访问服务器或者服务器没有SSL认证"
		login, info = self.sdk.login(url, username, password, self._ca_file)
		if login:
			cert_txt = subprocess.check_output(["openssl","x509","-text","-noout","-in",self._ca_file])
			pattarn = re.compile(r"O=(.*?),")
			tmp = pattarn.findall(cert_txt)
			if len(tmp) != 0:
				self._organ = tmp[0]
			else:
				return u'CA证书验证错误'
		else:
			return info

		
	def vmconnect(self,vmid,vmusb):
		ticket, expiry = self.sdk.ticketvm(vmid)
		if ticket == 0:
			return expiry
		self.status(vmid)
		self._port = self.display.get_port()
		self._sport = self.display.get_secure_port()
		self._host = self.display.get_address()
		self.certificate = self.display.get_certificate().subject
		self._usb = 0
		self._fullScreen = 1			
		self._smartcard = self.display.get_smartcard_enabled()
		if self.state == "up" or self.state == "powering_up":
			if self.display.type_ == "spice":			
				if vmusb == 1:
					self._usb = 1
		vmname = self.name
		if type(vmname).__name__ == 'unicode':
			vmname = vmname.encode("utf-8")
		try:
			vvFile = tempfile.NamedTemporaryFile(delete=False)
			if self.display.type_ == "vnc":
				t_vvContent = self.__createVncFile(ticket,vmname)
			elif self.display.type_ == "spice":
				t_vvContent = self.__createSpiceFile(ticket,vmname)
			vvFile.writelines(t_vvContent)
		except BaseException, e:
			return e
		finally:
			vvFile.close()
		cmd = ["remote-viewer",vvFile.name]
		try:
			subprocess.Popen(cmd)
		except:
			return u'请安装virt-viewer,并添加到环境变量'

	def __createVncFile(self,ticket,vmname):
		return ["[virt-viewer]\n","type=vnc\n","host={}\n".format(self._host),
					   "port={}\n".format(self._port),"password={}\n".format(ticket),"delete-this-file=0\n",
					   "fullscreen={}\n".format(1 if self._fullScreen==1 else 0),
					   "title={}\n".format(vmname),
					   "secure-attention=ctrl+alt+end"]

	def __createSpiceFile(self,ticket,vmname):
		return ["[virt-viewer]\n","type=spice\n","host={}\n".format(self._host),
					   "port={}\n".format(self._port),"password={}\n".format(ticket),"tls-port={}\n".format(self._sport),
					   "fullscreen={}\n".format(1 if self._fullScreen==1 else 0),
					   "title={} - 按 SHIFT+F12 释放光标\n".format(vmname),
					   "enable-smartcard={}\n".format(1 if self._smartcard==1 else 0),
					   "enable-usb-autoshare={}\n".format(1 if self._usb==1 else 0),
					   "delete-this-file=0\n",
					   "usb-filter=-1,-1,-1,-1,0\n",
					   "video-qmax=21\n",
					   "tls-ciphers=DEFAULT\n",
					   "host-subject={}\n".format(self.certificate),
					   "ca={}\n".format(self._ca_content.replace("\n","\\n")),
					   "toggle-fullscreen=shift+f11\n",
					   "release-cursor=shift+f12\n",
					   "secure-attention=ctrl+alt+end\n",
					   "secure-channels=main;inputs;cursor;playback;record;display;usbredir;smardcard"]

	def status(self,vmid):
		vm = self.sdk.getvmbyid(vmid)
		self.state = vm.status.state
		vcpus = vm.cpu.topology 
		self.cpu = str(vcpus.cores * vcpus.sockets)
		self.memory = '%.1f' % (vm.memory / (1024*1024*1024))
		self.os = vm.os.type_
		if vm.usb.enabled:
			self.usb = 1
		self.display = vm.get_display()
		self.name = vm.name	

class OvirtApi(object):
	def login(self, url, username, password, ca_file):
		global api
		ipPattern = re.compile(r"//\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
		isIp = ipPattern.search(url)

		try:
			if isIp is None:
				api = API(url=url,
						  username=username,
						  password=password,
						  ca_file=ca_file,
						  filter=True,
						  session_timeout=1,
						  persistent_auth=False
						  #insecure=True
						  )
			else:
				api = API(url=url,
						  username=username,
						  password=password,
						  ca_file=ca_file,
						  filter=True,
						  insecure=True
						  )
		except RequestError:
			return False, u"用户名密码错误或者登录域不正确"
		except ConnectionError:
			return False, u"网络连接错误"
		except NoCertificatesError:
			return False, u"SSL错误. 请用'http(s)://'"
		except Exception as e:
			return False, u"登录异常"
		return True, ''

	def getvmlist(self):
		global api
		try:
			return api.vms.list()
		except Exception,e:
			return 0

	def getvmbyid(self, id):
		global api
		return api.vms.get(id=id)

	def getvmstatus(self, id):
		global api
		try:
			return api.vms.get(id=id).status.state
		except:
			return 0

	def startvm(self, vmid):
		global api
		try:
			api.vms.get(id=vmid).start()
		except RequestError:
			return u"请求失败，请稍后重试！"
		except ConnectionError:
			return u"网络连接错误"

	def rebootvm(self, vmid):
		global api
		try:
			api.vms.get(id=vmid).reboot()
		except RequestError:
			return u"请求失败，请稍后重试！"
		except ConnectionError:
			return u"网络连接错误"

	def stopvm(self, vmid):
		global api
		try:
			api.vms.get(id=vmid).stop()
		except RequestError:
			return u"请求失败，请稍后重试！"
		except ConnectionError:
			return u"网络连接错误"

	def shutdown(self, vmid):
		global api
		try:
			api.vms.get(id=vmid).shutdown()
		except RequestError:
			return u"请求失败，请稍后重试！"
		except ConnectionError:
			return u"网络连接错误"

	def ticketvm(self, vmid):
		global api
		try:
			ticket = api.vms.get(id=vmid).ticket()
			value = ticket.get_ticket().get_value()
			expiry = ticket.get_ticket().get_expiry()
			return value, expiry
		except RequestError:
			return 0, u"请稍后重试或者重启虚拟机再试"
		except ConnectionError:
			return 0, u"网络连接错误"