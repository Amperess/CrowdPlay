import spotify
 
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse, Message
from twilio.rest import Client
import urllib
import requests
import xmltodict
import json
import pandas as pd
 
 
 
def playSong(uri,name):
	print("Playing song")
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
		
		'''for key, value in data["sources"]["sourceItem"].items():
			print("key: ",key, "Value: ", value)
			#print("type:",type(value))
			if(type(value) is list):
				spotify=value[-1]#json.dumps((value[-1]))'''
		counter=0
		for attribute in data["sources"]["sourceItem"]:
			#print(list(attribute.items())[0][1])

			if(list(attribute.items())[0][1] == "SPOTIFY"):
				acc_num=list(attribute.items())[1][1]
				#print("success")
				break
			counter+=1
		#print("counter is ",counter)
		print("spotify is ",spotify)
		#print("type is ",type(spotify))
		print("Account Number is: ",acc_num)
		r = requests.post(url = URL_Select, data='<ContentItem source="SPOTIFY" type="uri" location='+uri+' sourceAccount='+acc_num+' isPresetable="true"><itemName>'+name+'</itemName></ContentItem>')
		print("r is: ",r.text)
 
 
# Account SID and Auth Token from www.twilio.com/console
client = Client('AC22b947e22fa835ea721401cf4016817b', '0cfdae9c98181b341cddfd21b6541e3e')
sid = '35bc763fa7264c44b3db49feaf8d5a9e'
ssecret = '69ca704b0a824ce68043d1f04173eba2'
app = Flask(__name__)
soath = 'BQAgfYft_OcY400oz3HZdY1-gCpyb853gOYTGtqMERr7VRrWQBX_bWYLZBuae6r6TRdUF7Vr_6d5NI0INBU8YQpvSqYi65qzOTQoTxGTAPsSVxfKiVgDI3k-wCkPF7Wz7_-X4T3ZQQQEvAx9bAoFA-43Q2q7D5W4kZLi2lY-q_PlJyeSxKjr1fY52U0gPMUjaqz_NHpRC9kwB_uuR8AgxR-cfdrsaiJYfu9uguUV6ESOSMGavd9iXujRjPTMr86lkVytYsTQHhif'
# A route to respond to SMS messages and kick off a phone call.
@app.route('/sms', methods=['POST'])
def inbound_sms():
	response = MessagingResponse()
	
	# Grab the song title from the body of the text message.
	song_title = urllib.parse.quote(request.form['Body'])
	
	# Grab the relevant phone numbers.
	from_number = request.form['From']
	to_number = request.form['To']
	
	url='https://accounts.spotify.com/api/token'
	postr=requests.post(url, data = {'grant_type' : 'client_credentials'}, auth = (sid, ssecret))
	
	surl = 'https://api.spotify.com/v1/search?q='+ song_title + '&type=track&limit=1&offset=0'
	#pd.read_json(postr)
	#token = str(list(postr)[0])
	token = postr.json()
	#token = '[' + str(token) + ']'
	token=(token['access_token'])
	#print("token: "+token)
	#df = pd.read_json(token)
	#print('access token is:', df['acces_token'])
	r = requests.get(url = surl, headers={'Authorization' : 'Bearer '+ (token)})
	#print(s)
	uri = (r.json()['tracks']['items'][0]['uri'])
	track = (r.json()['tracks']['items'][0]['name'])
	print(uri)
	print(track)
	name=track
	'''for v in vals:
		print("value: ",v)'''
	message = client.messages.create(from_number,body="Let's grab lunch at Brower tomorrow!",from_=to_number)
	playSong(uri, name)
	#response.message(r.json())
	return str(response)
	
if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
