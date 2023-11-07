from flask import Flask
from random import randint
from multiprocessing import Process, Queue
import main
import spotipy
from os import getenv as env
import sqlite3

# return code guide: 0 = Nothing playing, 1 = Paused, 2 = Advertisement, 3 = Song playing
# mode code guide: 0 = not using (service), 1 = hosting with (service), 2 = client with (service)
client_id = env('API_KEY')
client_secret = env('API_SECRET')
redirect_uri = 'http://127.0.0.1:5000/spotify/callback' #change redirect when implementing into website
app = Flask(__name__)
rooms = []
con = sqlite3.connect("host.db", check_same_thread=False)
cur = con.cursor()
init = 0
try:
    cur.execute("CREATE TABLE room(roomcode INT, returncode, trackname, artistname, position_ms)")
    con.commit()
except sqlite3.OperationalError:
    cur.execute("DROP TABLE room")
    cur.execute("CREATE TABLE room(roomcode INT, returncode, trackname, artistname, position_ms)")
    con.commit()
con.close()
for i in range(11111111,111111111):
    rooms.append(None)
roomcodes = []
#initialize database

@app.route('/getroomcode') # create new room
def getroomcode():
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
    
@app.route('/hostroom/<roomcode>/<spmode>/<ytmode>/<ytpassword>/<ytip>/<token_info>')  # host room
def hostroom(roomcode, spmode, ytmode, ytpassword, ytip, token_info):
    roomcode = int(roomcode)
    if spmode == '1':  # Note that I've changed this to a string comparison
        instance = Process(target=main.main, args=(roomcode, spmode, ytmode, None, None, token_info))
    elif ytmode == '1':  # Also changed this to a string comparison
        instance = Process(target=main.main, args=(roomcode, spmode, ytmode, ytpassword, ytip, None))
    roomcodes.append(roomcode) # add roomcode to roomcodes list
    rooms[roomcode] = instance  # Store the instance in the dictionary using the roomcode as the key
    instance.start()  # Start the process
    return {
        'isHosting': True
    }

@app.route('/joinroom/<roomcode>') # join room
def joinroom(roomcode):
    if roomcode in roomcodes: # check if roomcode exists
        return{
            'isRoomcode': True
        }
    else:
        return{
            'error': 404,
            'desc': 'RoomNotFound'
        }
    
@app.route('/room/spotify/<roomcode>/<token_info>') # spotify enter room
def sproom(roomcode, token_info):
    host = None
    while host == None:
        try:
            con = sqlite3.connect("host.db", check_same_thread=False)
            cur = con.cursor()
            host = cur.execute("SELECT * FROM room WHERE roomcode =?", (roomcode,)).fetchone()
            con.close()
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
        except TypeError:
            pass
@app.route('/room/youtube/<roomcode>') # youtube enter room
def ytroom(roomcode):
    host = None
    while host == None:
        try:
            con = sqlite3.connect("host.db", check_same_thread=False)
            cur = con.cursor()
            host = cur.execute("SELECT * FROM room WHERE roomcode =?", (roomcode,)).fetchone()
            con.close()
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
                    'isPaused': False,
                    'songid': songid,
                    'position_ms': position_ms
                }
        except TypeError:
            pass

@app.route('/disconnect')
#find how to figure out when host is disconnected, if spotify clear host cache, free roomPos and roomcode
def disconnect():
    return('awfoeij')

if __name__ == '__main__':
    app.run()