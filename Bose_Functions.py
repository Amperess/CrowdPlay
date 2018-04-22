import requests
import xmltodict
import json
import pandas as pd

import re
def playSong(uri):
	URL_Select="http://192.168.1.144:8090/select"
	URL_Sources="http://192.168.1.144:8090/sources"
	#PARAMS = {'address':location}

	#r = requests.post(url = URL, data = "<ContentItem source="AUX" sourceAccount="AUX"></ContentItem>")

	r = requests.get(url = URL_Sources, params=None)
	if r is not None:
		print("read: ",r)
		data=xmltodict.parse(r.text)
		#J=json.dumps(data)
		#k=pd.read_json(J)
		#l=pd.read_json(k['sourceItem
		#print(k["sourceItem"]["sources"])
		#print("data:",k["sourceItem"])
		
		for key, value in data["sources"].items():
			#print("key: ",key, "Value: ", value)
			#print("type:",type(value))
			if(type(value) is list):
				spotify=value[-1]#json.dumps((value[-1]))
		#print("spotify is ",spotify)
		#print("type is ",type(spotify))
		acc_num=list(spotify.items())[1][1]
		print("Account Number is: ",acc_num)
		r = requests.post(url = URL_Select, data='<ContentItem source="SPOTIFY" type="uri" location='+uri+' sourceAccount='+acc_num+' isPresetable="true"><itemName>The Hollow</itemName></ContentItem>')

	   
def isDone():
	URL_NP="http://192.168.1.144:8090/now_playing"
	r = requests.get(url = URL_NP, params=None).text
	if r is not None:
		print("read: ",r)
		index=r.index("time total=")+len("time total=")
		total=r[index+1:]
		
		total=int(re.search('[0-9]+', total).group())
		index+=len(str(total))
		current=r[index+1:]
		#print(current)
		current=int(re.search('[0-9]+', current).group())
		print("total time is: ",total)
		print("current time is:",current)
		if(total-current<=5):
			return True
		else:
			return False

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

print(isDone())

