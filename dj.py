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
currentSong=" "
client = "Don't you wish"
sid = "Your girlfriend"
ssecret = "was hot"
soath = "like me"
dec_count = 1	
app = Flask(__name__)

def skip():
	global q1
	if not q1.empty():
		song = q1.get()
		print("song struct is: ",song)
		playSong(song[2], song[1])
		return('Song skipped')
	else:
		#print("No songs left in queue")
		return('No songs left in queue')


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
			return('Volume increased by ' + str(step))
		else:
			bf.volumeDown(step)
			return('Volume decreased by ' + str(step))
def mute():
	bf.mute()
def volumeMax():
	bf.volumeMax()
def nextFive():
	global q1
	s = 'Coming up next: '
	sname=" "
	sname2=" "
	sname3=" "
	sname4=" "
	sname5=" "
	spri=-10000
	spri2=-10000
	spri3=-10000
	spri4=-10000
	spri5=-10000
	suri=" "
	suri2=" "
	suri3=" "
	suri4=" "
	suri5=" "
	#grab them and hold them all to cocatenate, can't add them back in because 
	#it would put them back at the front and they would just get got again
	if not q1.empty():
		song = q1.get()
		spri = song[0]
		sname = song[1]
		suri = song[2]
		s = s + sname + ', '
	if not q1.empty():
		song = q1.get()
		spri2 = song[0]
		sname2 = song[1]
		suri2 = song[2]
		s = s + sname2 + ', '
	if not q1.empty():
		song = q1.get()
		spri3 = song[0]
		sname3 = song[1]
		suri3 = song[2]
		s = s + sname3 + ', '
	if not q1.empty():
		song = q1.get()
		spri4 = song[0]
		sname4 = song[1]
		suri4 = song[2]
		s = s + sname4 + ', '
	if not q1.empty():
		song = q1.get()
		spri5 = song[0]
		sname5 = song[1]
		suri5 = song[2]
		s = s + sname5
	
	#If it actually got taken out and checked aka the atributes werent null, put them back with same values
	#!!!check if theres an issue with doing this near the end of a song 
	if not sname is " ":
		q1.put(((spri, sname, suri)))
	if not sname2 is " ":
		q1.put(((spri2, sname2, suri2)))
	if not sname3 is " ":
		q1.put(((spri3, sname3, suri3)))
	if not sname4 is " ":
		q1.put(((spri4, sname4, suri4)))
	if not sname5 is " ":
		q1.put(((spri5, sname5, suri5)))
	if sname is " " and sname2 is " " and sname3 is " " and sname4 is " " and sname5 is " ":
		s = "Nothing up next. Add something?"
	return s
 
def playSong(uri,name):
	print("Playing song")
	global currentSong
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
		timer.start()
		currentSong = name
 
#adds song to priority queue
def enqueueSong(uri, entername):
	global q1
	global q2
	global dec_count
	global currentSong
	dec_count+=1
	inThere = False
	if q1.empty():
		q1.put(((1.0000, entername, uri)))
		print('Added song' + entername + uri)
		timer = Timer(3, transitionTracks, None)
		currentSong = entername
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
	global currentSong
	 
	response = MessagingResponse()
	print("Q is:")
	print(q1)
	# Grab the song title from the body of the text message.
	song_title = urllib.parse.quote(request.form['Body'])
	
	# Grab the relevant phone numbers.
	from_number = request.form['From']
	to_number = request.form['To']
	
	#print("song title is:", song_title.lower().strip())

	if (song_title.lower().startswith('volume')):
		#volume(song_title)
		response.message(volume(song_title))
	elif(song_title.lower().strip()=='skip'):
		#skip()
		response.message(skip())
	elif(song_title.lower().strip()=='mute'):
		mute()
		response.message('Volume Off')
	elif(song_title.lower().strip()=='max%20volume' or song_title.lower().strip()=='volume max'):
		print("Maximum volume")
		volumeMax()
		response.message('It\'s over 9000!')
	elif(song_title.lower().strip()=='up%20next'):
		response.message(nextFive())
	elif(song_title.lower().strip()=='current%20song'):
		print('Current song is: ' + currentSong)
		if not currentSong == " ":
			response.message('The current song is ' +currentSong)
		else:
			response.message('There is no song playing right now')
	else:
		#get auth token
		url='https://accounts.spotify.com/api/token'
		postr=requests.post(url, data = {'grant_type' : 'client_credentials'}, auth = (sid, ssecret))
		token = postr.json()
		token=(token['access_token'])
		#Get song information
		surl = 'https://api.spotify.com/v1/search?q='+ song_title + '&type=track&limit=5&offset=0'
		r = requests.get(url = surl, headers={'Authorization' : 'Bearer '+ (token)})
		#print("information: "+r.json()['tracks']['items'][corr])
		uri = (r.json()['tracks']['items'][0]['uri'])
		#trackname = 
		if(uri is None):
			print("No such track")
			response.message("No such song")
			return str(response)
		track = (r.json()['tracks']['items'][0]['name'])
		name = track
		print("Read song: " + name)
		print("URI IS: ", uri)
		enqueueSong(uri, name)
		response.message(name + ' is being added to the queue!')

	return str(response)
	
if __name__ == '__main__':		
	print(q1)
	app.run(host='0.0.0.0', debug=True)
