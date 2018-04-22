#import spotify
import Bose_Functions as bf
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse, Message
from twilio.rest import Client
from threading import Timer
import urllib
import requests
import xmltodict
import json
import pandas as pd
import re
try:
	import Queue as Q  # ver. < 3.0
except ImportError:
	import queue as Q
q1 = Q.PriorityQueue()
q2 = Q.PriorityQueue()
client = Client('AC22b947e22fa835ea721401cf4016817b', '0cfdae9c98181b341cddfd21b6541e3e')
sid = '35bc763fa7264c44b3db49feaf8d5a9e'
ssecret = '69ca704b0a824ce68043d1f04173eba2'
soath = 'BQAgfYft_OcY400oz3HZdY1-gCpyb853gOYTGtqMERr7VRrWQBX_bWYLZBuae6r6TRdUF7Vr_6d5NI0INBU8YQpvSqYi65qzOTQoTxGTAPsSVxfKiVgDI3k-wCkPF7Wz7_-X4T3ZQQQEvAx9bAoFA-43Q2q7D5W4kZLi2lY-q_PlJyeSxKjr1fY52U0gPMUjaqz_NHpRC9kwB_uuR8AgxR-cfdrsaiJYfu9uguUV6ESOSMGavd9iXujRjPTMr86lkVytYsTQHhif'
dec_count = 1	

app = Flask(__name__)

def skip():
	global q1
	song = q1.get()
	print("song struct is: ",song)
	playSong(song[2], song[1])



#volume Control
def volume(song_title):
	#step=0
	if (song_title.lower().startswith('vol')):
		try:
			step = int((song_title.split("%20"))[2])
			print("regex step is: ",step)
		except:
			print('no volume specified', song_title)
			step=5			

		if(step<0):
			step=0
		elif(step>100):
			step=100
		print("step: ",step)
		if( 'up' in song_title.lower()):
			bf.volumeUp(step)
		else:
			bf.volumeDown(step)

 
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
		#print("type of data is: ",type(data["sources"]["sourceItem"]))
		
		counter=0
		for attribute in data["sources"]["sourceItem"]:
			#print(list(attribute.items())[0][1])

			if(list(attribute.items())[0][1] == "SPOTIFY"):
				acc_num=list(attribute.items())[1][1]
				#print("success")
				break
			counter+=1
		#print("counter is ",counter)
		#print("type is ",type(spotify))
		print("Account Number is: ",acc_num)
		r = requests.post(url = URL_Select, data='<ContentItem source="SPOTIFY" type="uri" location='+uri+' sourceAccount='+acc_num+' isPresetable="true"><itemName>'+name+'</itemName></ContentItem>')
		print("r is: ",r.text)
		timer = Timer(3, transitionTracks, None)
		timer.start();
 
#adds song to priority queue
def enqueueSong(uri, entername):
	global q1
	global q2
	global dec_count
	dec_count+=1
	inThere = False
	if q1.empty():
		q1.put(((1.0000, entername, uri)))
		print('Added song' + entername + uri)
		timer = Timer(3, transitionTracks, None)
		timer.start();
		return()
	while not q1.empty():
		song = q1.get()
		print("song q is ",song)
		priority = song[0]
		ename = song[1]
		uri_s = song[2]
		if entername == ename:
			q2.put((priority-1, ename, uri_s))
			inThere = True;
		else:
			q2.put((priority, ename, uri_s))
			
	q1 = q2
	if not inThere:
		q1.put(((1+(dec_count*0.0001), entername, uri)))
	print("Not empty, added song" + entername)
	q2 = Q.PriorityQueue()
	
def transitionTracks():
	global q1
	global q2
	if bf.isDone():
		song = q1.get()
		print("song struct is: ",song)
		playSong(song[2], song[1])
	else:
		timer = Timer(3, transitionTracks, None)
		timer.start();
		
# A route to respond to SMS messages and play music
@app.route('/sms', methods=['POST'])
def inbound_sms():
	response = MessagingResponse()
	response.message('Hi')
	print("Q is:")
	print(q1)
	# Grab the song title from the body of the text message.
	song_title = urllib.parse.quote(request.form['Body'])
	
	# Grab the relevant phone numbers.
	from_number = request.form['From']
	to_number = request.form['To']
	
	if (song_title.lower().startswith('volume')):
		volume(song_title)
	elif(song_title.lower().strip()=='skip'):
		skip()
		
	else:
		#get auth token
		url='https://accounts.spotify.com/api/token'
		postr=requests.post(url, data = {'grant_type' : 'client_credentials'}, auth = (sid, ssecret))
		token = postr.json()
		token=(token['access_token'])
		
		#Get song information
		surl = 'https://api.spotify.com/v1/search?q='+ song_title + '&type=track&limit=1&offset=0'
		r = requests.get(url = surl, headers={'Authorization' : 'Bearer '+ (token)})
		uri = (r.json()['tracks']['items'][0]['uri'])
		if(uri is None):
			print("No such track")
			response.message("No such song")
			return str(response)
		track = (r.json()['tracks']['items'][0]['name'])
		name = track
		message = client.messages.create(from_number,body="Your song has been queued!",from_=to_number)
		print("Read song: " + name)
		print("URI IS: ", uri)
		enqueueSong(uri, name)

	return str(response)
	
if __name__ == '__main__':		
	print(q1)
	app.run(host='0.0.0.0', debug=True)
