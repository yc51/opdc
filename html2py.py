# coding: utf-8
import htmlPy
import json
from cloud import cloud
import time
from PySide import QtCore
import sys
import urllib2
import ssl
import lxml.etree as etree
import base64
import os
import socket
import subprocess
import hashlib

global cecos, context
context = ssl._create_unverified_context()
cecos = cloud()

class opdc(htmlPy.Object):
	
	def __init__(self, app):
		super(opdc ,self).__init__()
		self.app, self.domainlist, self.autoconnect, self.code, uuid = app, [], 1, "8e4db523d4b7db00f78957df58b4e217c5370c1e", ''
		try:
			with open('config.json', 'r') as f:
				self.ss = json.load(f)
		except IOError:
			print('config.json read error')
			sys.exit()
		try:
			cardname = os.listdir('/sys/class/net')
			cardname.remove('lo')
			self.cardname = cardname[0]
			with open('/sys/class/net/'+cardname[0]+'/address') as f:
				self.mac = f.read()
		except:
			self.cardname = 0
			self.mac = '00-00-00-00-00-00'
		u = self.sh1md5(self.mac)
		v = self.sh1md5(u)
		if self.code != self.ss['code']:
			self.code = v
			if  self.ss['code'] != v:
				self.app.template = ("code.html",{'uuid':u})
				return
		self.start(v)
		
	def sh1md5(self, code):
		md5 = hashlib.md5()
		md5.update(code)
		sha1 = hashlib.sha1()
		sha1.update(md5.hexdigest())
		st = sha1.hexdigest()
		return st[0:8] + st[-8:]

	@htmlPy.Slot(str, result=str)
	def start(self,code):
		if self.code == "8e4db523d4b7db00f78957df58b4e217c5370c1e" or self.code == code:
			self.save(code)
		else:
			return
		self.server, self.pwd, self.setpass = 'https://'+self.ss['server'], base64.decodestring(self.ss['pwd']), base64.decodestring(self.ss['set_pass'])
		self.autologin = self.ss['autologin'] == '1' and 1 or 0
		self.autoswitch = self.ss['autoswitch'] or '0'
		self.user = self.ss['user']
		try:
			self.hostname = socket.gethostname()
		except:
			self.hostname = ''
		self.load()
		(self.hpath, self.npath, self.dpath) = os.name == 'nt' and ("C:\Windows\System32\drivers\etc\hosts", 0 , 0) or ('/etc/hosts', '/etc/network/interfaces', '/etc/resolvconf/resolv.conf.d/head')
		self.app.template= ("login.html",{'server':self.ss['server'],'password':self.setpass,'hostname':self.hostname,'ip':self.ip,'mac':self.mac})

	#加载配置
	def load(self):
		try:
			self.ip = subprocess.Popen(('hostname','--all-ip-addresses'),stdout=subprocess.PIPE).communicate()[0].rstrip()
		except:
			self.ip = ''
		
	#保存配置
	def save(self, code=''):
		if code:
			self.ss['code'] = code
		if hasattr(self,'pwd'):
			self.ss['pwd'], self.ss['set_pass'] = base64.encodestring(self.pwd), base64.encodestring(self.setpass)
			self.ss['user'] = self.user
		with open('config.json', 'w') as f:
			f.write(json.dumps(self.ss))

	def dmlist(self,res):
		try:
			a = self.user.split('@')[1]
			b = res.index(a)
			if b:
				res[0], res[b] = a, res[0]
		except:
			pass
		self.app.evaluate_javascript("cecos_domains('"+json.dumps(res)+"')")

	#刷新域列表
	@htmlPy.Slot()
	def domains(self):
		if self.autologin:
			self.login(self.user, self.pwd, self.ss['autologin'])
		else:
			if len(self.domainlist) > 1:
				self.dmlist(self.domainlist)
			else:
				self.th = domains_thread(self.server)
				self.th.finishSignal.connect(self.domainsdone)
				self.th.start()
		return True

	@htmlPy.Slot()
	def changeuser(self):
		self.autologin = 0
		try:
			self.ss['autologin'] = '0'
			self.save()
		except Exception,e:  
			pass
		self.app.template= ("login.html",{'server':self.ss['server'],'password':self.setpass,'hostname':self.hostname,'ip':self.ip,'mac':self.mac})
		if hasattr(self,'ths'):
			self.ths.loop = 0
		self.autoconnect = 1
		self.domains()
			
	@htmlPy.Slot(str, str, str, result=str)
	def login(self,user,pwd,auto):
		try:
			user, pwd = user.encode('utf-8'), pwd.encode('utf-8')
			self.ss['autologin'] = auto
			self.user, self.pwd = user, pwd
		except Exception,e:  
			pass
		self.th = login_thread(user, pwd, self.server)
		self.th.finishSignal.connect(self.logindone)
		self.th.start()
		return True

	@htmlPy.Slot(str, str, int, result=str)
	def task(self,work,vmid,vmusb=0):
		# getattr改进
		aa = 0
		if work == u'启动':
			aa = cecos.sdk.startvm(vmid)				
		elif work == u'重启':
			aa = cecos.sdk.rebootvm(vmid)
		elif work == u'关机':
			aa = cecos.sdk.shutdown(vmid)
		elif work == u'远程':
			if self.autoconnect == 1:
				self.autoconnect = 0
			aa = cecos.vmconnect(vmid,vmusb)
		elif work == u'断电':
			aa = cecos.sdk.stopvm(vmid)
		return aa or 0

	@htmlPy.Slot(str, str, str, result=str)
	def system(self, work, ser='', pwd=''):
		try:
			ser, pwd = ser.encode('utf-8'), pwd.encode('utf-8')
		except Exception,e:  
			pass
		aa = 0
		if work == u'关机':
			aa = os.system('poweroff')
		elif work == u'重启':
			aa = os.system('reboot')
		elif work == 'pass':
			return self.setpass
		elif work == 'set':
			if ser and (ser != self.ss['server']):
				self.ss['server'] = ser
				self.server = 'https://'+ser
				if hasattr(self,'th'):
					self.th.server = self.server
				elif self.domainlist:
					self.domains()
			if pwd and (pwd != self.setpass):
				self.setpass= pwd
			self.save()
		elif work == 'loadhost':
			with open(self.hpath, 'r') as f:
				hosts =f.read()
				hosts = hosts.replace('\n','<br>')
			return hosts
		elif work == 'savehost':
			if ser:
				with open(self.hpath, 'w') as f:
					f.write(ser)
		elif work =='exit':
			try:
				subprocess.Popen('xterm -class UXTerm -title uxterm -u8', shell=True)
			except:
				pass
			self.app.stop()
			sys.exit()
		elif work == 'loadnet':
			res = self.ss['network']
			res['cecos_set_hostname'] = self.hostname
			return json.dumps(res)
		elif work == 'savenet':
			net = json.loads(ser.encode('utf-8'))
			try:
				ctime = net['cecos_set_time']
				net.pop('cecos_set_time')
				if ctime:
					subprocess.Popen('date -s "'+ctime+'"', shell=True)
					subprocess.Popen('hwclock  -w', shell=True)
			except:
				pass
			if not self.cardname:
				return
			try:
				if net['cecos_set_hostname'] != self.hostname:					
					subprocess.Popen('hostnamectl set-hostname "'+net['cecos_set_hostname']+'"', shell=True)
					self.hostname = net['cecos_set_hostname']
			except:
				pass
			finally:
				net.pop('cecos_set_hostname')
				self.ss['network'].pop('cecos_set_hostname')
			if 'cecos_set_dhcp' not in net:
				net.update({'cecos_set_dhcp':'off'})
			try:
				if (net['cecos_set_dns1'] == self.ss['network']['cecos_set_dns1']) and (net['cecos_set_dns2'] == self.ss['network']['cecos_set_dns2']):
					raise ValueError
				dfile = ''
				if net['cecos_set_dns1']:
					dfile = 'nameserver ' + net['cecos_set_dns1'] + '\n'
				if net['cecos_set_dns2']:
					dfile += 'nameserver ' + net['cecos_set_dns2'] + '\n'
				if dfile:
					with open(self.dpath, 'w') as f:
						f.write(dfile)
					subprocess.Popen('resolvconf -u', shell=True)
			except:
				pass
			try:
				cardname = self.cardname
				nfile = 'auto lo\niface lo inet loopback\nauto '+cardname+'\niface '+cardname+' inet'
				if net['cecos_set_dhcp'] == 'on':
					if self.ss['network']['cecos_set_dhcp'] == 'on':
						raise ValueError
					net['cecos_set_ip'] = net['cecos_set_netmask']=net['cecos_set_gateway']=net['cecos_set_dns1']=net['cecos_set_dns2'] = ''
					nfile += ' dhcp\n'
					subprocess.Popen('systemctl restart networking', shell=True)
				else:
					if not cmp(net,self.ss['network']):
						raise ValueError
					nfile += ' static' + '\naddress ' + net['cecos_set_ip'] + '\nnetmask ' + net['cecos_set_netmask'] + '\ngateway ' + net['cecos_set_gateway']
					cmd1 = 'ifconfig ' + cardname+' '+net['cecos_set_ip'] + ' netmask ' + net['cecos_set_netmask']
					cmd2 = 'route add default gw ' + net['cecos_set_gateway']
					subprocess.Popen(cmd1, shell=True)
					subprocess.Popen(cmd2, shell=True)
				with open(self.npath, 'w') as f:
					f.write(nfile)
			except:
				pass
			self.ss['network'] = net
			self.save()
			self.load()
			self.app.evaluate_javascript("cecos_footer('"+self.hostname+","+self.ip+"')")

		elif work == 'display':
			try:
				cmd = ['wmctrl', '-c', 'Display Settings']
				subprocess.Popen(cmd)
			except:
				return 'wmctrl'
			try:
				cmd = ['lxrandr']
				subprocess.Popen(cmd)
			except:
				return 'lxrandr'
		return aa or 0
		
	@htmlPy.Slot(str,result=str)
	def status(self, vmid):
		return cecos.sdk.getvmstatus(vmid)

	#虚拟机自动刷新
	@htmlPy.Slot()
	def refresh(self):
		if hasattr(self,'ths'):
			while self.ths.isRunning():
				time.sleep(1)
		self.ths = vms_thread()
		self.ths.vmsSignal.connect(self.vmsupdate)
		self.ths.start()
		
	#登录回调函数
	def logindone(self, res):
		if not res:
			self.save()
			self.app.template = ("index.html", {'login_user': self.user,'hostname':self.hostname,'ip':self.ip,'mac':self.mac,'autoswitch':self.autoswitch})
		else:
			self.app.evaluate_javascript("cecos_login('"+res+"')")
			if self.autologin == 1:
				self.autologin = 0
				self.domains()

	#虚拟机刷新回调
	def vmsupdate(self, res):
		re = json.dumps(res)
		self.app.evaluate_javascript("cecos_list('"+re+"')")		
		if self.autoconnect == 1:
			if len(res) > 1:
				self.autoconnect = 0
			else:
				sw = self.autoswitch
				self.app.evaluate_javascript("auto_connect('"+sw+"')")
			
	#域列表刷新回调
	def domainsdone(self, res):		
		self.domainlist = res
		self.dmlist(res)

	#联动开关机设置
	@htmlPy.Slot(str)
	def vmswitch(self,sw):
		self.autoswitch = sw
		self.ss['autoswitch'] =sw
		self.save()


#登录线程
class login_thread(QtCore.QThread):
	finishSignal = QtCore.Signal(str)
	
	def __init__(self, user, pwd, server, parent=None):
		super(login_thread, self).__init__(parent)
		self.user, self.pwd, self.server = user, pwd, server

	def run(self):
		self.finishSignal.emit(cecos.auth_user(self.user,self.pwd,self.server))

#域列表刷新线程
class domains_thread(QtCore.QThread):
	finishSignal = QtCore.Signal(list)
	
	def __init__(self, server, parent=None):
		super(domains_thread, self).__init__(parent)
		self.server = server
	def run(self):
		while True:
			try:
				domains = urllib2.urlopen(self.server+'/ovirt-engine/domains',context=context).read()
				html = etree.XML(domains)
				domains = html.xpath('//domain/text()')
				break
			except Exception,e:
				pass				
			time.sleep(4)
		self.finishSignal.emit(domains)

#虚拟机列表刷新线程
class vms_thread(QtCore.QThread):
	vmsSignal = QtCore.Signal(list)

	def __init__(self, parent=None):
		super(vms_thread, self).__init__(parent)
		self.loop = 1

	def wait(self):
		i = 1
		while i<9:
			if self.loop:
				time.sleep(1)
			else:
				break
			i += 1

	def run(self):
		vmshow = {}
		while self.loop:
			vmchange, weblist = {}, []
			vmweb = cecos.sdk.getvmlist()
			showlist = vmshow.keys()
			if not vmweb or not len(vmweb):
				self.wait()
				continue
			for vm in vmweb:
				vmid = vm.id
				state = vm.status.state
				weblist.append(vmid)				
				if vmid in showlist:
					if state and state != vmshow.get(vmid):
						vmchange.update({str(vmid):state})
				else:
					cecos.status(vmid)
					value = {
							'state': cecos.state,
							'cpu': cecos.cpu,
							'mem': cecos.memory,
							'os': cecos.os,
							'usb': cecos.usb,
							'type':cecos.display.type_,
							'name':cecos.name
						}
					vmchange.update({str(vmid):value})
				vmshow.update({str(vmid):state})
			for vmid in showlist:
				if vmid in weblist:
					continue
				vmchange.update({str(vmid):{}})
				del vmshow[str(vmid)]
			if (len(vmchange) > 0):
				#vmchange = json.dumps(vmchange)
				self.vmsSignal.emit(vmchange)
			self.wait()