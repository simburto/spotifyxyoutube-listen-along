from flask import Flask
from random import randint
from multiprocessing import Process
import main
import spotipy
from os import getenv as env

# return code guide: 0 = Nothing playing, 1 = Paused, 2 = Advertisement, 3 = Song playing
# mode code guide: 0 = not using (service), 1 = hosting with (service), 2 = client with (service)
client_id = env('API_KEY')
client_secret = env('API_SECRET')
redirect_uri = 'http://127.0.0.1:5000/spotify/callback' #change redirect when implementing into website
app = Flask(__name__)
rooms = []
roomcodes = []

@app.route('/getroomcode') # create new room
def getroomcode(request):
    roomcode = randint(11111111,99999999) # generate roomcode
    roomcodevalid = False
    while not roomcodevalid: # check if roomcode is used or not
        if roomcode not in roomcodes:
            roomcodevalid = True
            return {
            'id': roomcode,
            }
        else:
            roomcode = randint(11111111,99999999)
    
@app.route('/hostroom/<roomcode>/<spmode>/<ytmode>/<ytpassword>/<ytip>/<token_info>') # host room
def hostroom(roomcode, spmode, ytmode, ytpassword, ytip, token_info):
    if spmode == 1: # if using spotify
        spu = spotipy.Spotify(auth=token_info)
        exec = roomcode, Process(target=main.main(), args=(spmode, ytmode, None, None, spu))
    elif ytmode == 1: # if using youtubemusic
        exec = roomcode, Process(target=main.main(), args=(spmode, ytmode, ytpassword, ytip, None))
    exec[1].start() # starts new instance of main.py
    rooms[len(rooms)+1] = exec # adds instance to array of instances to be accessed by client
    return {
        'isHosting': True
    }

@app.route('/joinroom/<roomcode>/<spmode>/<ytmode>') # join room
def joinroom(roomcode, spmode, ytmode):
    if roomcode in roomcodes: # check if roomcode exists
        for i in range(len(rooms)): # find roomPos and roomcode (prevent brute force attack)
            if rooms[i][0] == roomcode and spmode == 2:
                return {
                    'roomPos': i,
                    'roomCode': roomcode,
                    'method': 'SpClient'
                }
            elif rooms[i][0] == roomcode and ytmode ==2:
                return {
                    'roomPos': i,
                    'roomCode': roomcode,
                    'method': 'YTClient'
                }
    else:
        return{
            'error': 404,
            'desc': 'RoomNotFound'
        }
    
@app.route('/room/spotify/<i>/<roomcode>/<token_info>') # spotify enter room
def sproom(i, roomcode, token_info):
    i= int(i)
    try:
        if roomcode != rooms[i][0]: # prevent brute force attack
            return{
                'error': 401,
                'desc': 'Unauthorized'
            }
    except IndexError:
        return{
                'error': 401,
                'desc': 'Unauthorized'
            }
    host = rooms[i][1].join() # join session
    #check returncodes
    if host[0] == 0: 
        return {
            'notUsingService': True
        }
    elif host[0] == 1:
        return {
            'isPaused': True
        }
    elif host[0] == 2:
        return {
            'isAdvertisement': True
        }
    elif host[0] == 3:
        spu = spotipy.Spotify(auth=token_info)
        position_ms = host[1]
        artistname = host[2]
        trackname = host[3]
        songid = main.spotify.client(trackname, artistname, position_ms, spu)[0]
        return {
            'songid': songid # for spotify HTML embed
        }

@app.route('/room/youtube/<i>/<roomcode>') # youtube enter room
def ytroom(i, roomcode):
    i= int(i)
    try:
        if roomcode != rooms[i][0]: # prevent brute force attack
            return{
                'error': 401,
                'desc': 'Unauthorized'
            }
    except: 
        return{
            'error': 401,
            'desc': 'Unauthorized'
        }
    host = rooms[i][1].join() # join room
    #check returncodes
    if host[0] == 0: 
        return {
            'notUsingService': True
        }
    elif host[0] == 1:
        return {
            'isPaused': True
        }
    elif host[0] == 2:
        return {
            'isAdvertisement': True
        }
    elif host[0] == 3:
        position_ms = host[1]
        artistname = host[2]
        trackname = host[3]
        songid = main.youtube.client(trackname, artistname) # MAIN.YOUTUBE.CLIENT IS NOT DONE YET!!
        return {
            'isPaused': True,
            'songid': songid,
            'position_ms': position_ms
        }

@app.route('/disconnect')
#find how to figure out when host is disconnected, if spotify clear host cache, free roomPos and roomcode
def disconnect():
    return('awfoeij')

if __name__ == '__main__':
    app.run()