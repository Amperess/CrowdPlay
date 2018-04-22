import requests
import xmltodict
import json
import pandas as pd
import re
	   
def isDone():
	URL_NP="http://192.168.1.144:8090/now_playing"
	r = requests.get(url = URL_NP, params=None).text
	if r is not None:
		#print("read: ",r)
		try:
			index=r.index("time total=")+len("time total=")
			if(index is None):
				return True
			total=r[index+1:]
			
			total=int(re.search('[0-9]+', total).group())
			if(total is None):
				return True
			index+=len(str(total))
			current=r[index+1:]
			#print(current)
			current=int(re.search('[0-9]+', current).group())
			print("total time is: ",total)
			print("current time is:",current)
			if(total-current<=5 and total>5):
				return True
			else:
				return False
		except:
			print("exception occured")
			return True
	print("Error")
	return True

def volumeUp(step=5):
	URL_Vol="http://192.168.1.144:8090/volume"
	r = requests.get(url = URL_Vol, params=None).text
	if r is not None:
		print("read: ",r)
		index=r.index("targetvolume>")+len("targetvolume>")
		vol=int(re.search('[0-9]+', r[index:]).group())
		print("current volume is: ",vol)
		vol+=step
		r = requests.post(url = URL_Vol, data='<volume>'+str(vol)+'</volume>')

def volumeDown(step=5):
	URL_Vol="http://192.168.1.144:8090/volume"
	r = requests.get(url = URL_Vol, params=None).text
	if r is not None:
		print("read: ",r)
		index=r.index("targetvolume>")+len("targetvolume>")
		vol=int(re.search('[0-9]+', r[index:]).group())
		print("current volume is: ",vol)
		vol-=step
		r = requests.post(url = URL_Vol, data='<volume>'+str(vol)+'</volume>')
def volumeMax():
	URL_Vol="http://192.168.1.144:8090/volume"
	r = requests.post(url = URL_Vol, data='<volume>'+str(65)+'</volume>')
def mute():
	URL_Vol="http://192.168.1.144:8090/volume"
	r = requests.post(url = URL_Vol, data='<volume>'+str(0)+'</volume>')

