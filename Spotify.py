import spotipy
import sys

import spotipy.util as util

#function that creates a dictionary containing the track name, artist name, and track ID of each track in the playlist
def trackNameFCN(results):
    trackNames = {}
    for item in (results['items']):
        track = item['track']
        name = track['name']
        id = track['id']
        artist = track['artists'][0]['name']
        trackNames[id] = (name, artist)
    return (trackNames)

def playlist_tracks(username, list_of_playlists, sp, playlist_name):
    i = 0
    for playlist in playlists['items']:
        #checks to see if input playlist name matches an existing user playlist
        if playlist['name'] == playlist_name:
            results = sp.user_playlist(username, playlist['id'], fields="tracks,next")
            tracks = results['tracks']
            #calls another function which returns track name, artist name, and track ID of each track as a dict.
            tracklist = trackNameFCN(tracks)
            #Spotify can only return 100 tracks at a time, so this while loop adds additional tracks if the playlist has more than 100 songs
            while tracks['next']:
                    tracks = sp.next(tracks)
                    tracklist2 = trackNameFCN(tracks)
                    tracklist.update(tracklist2)
            return (tracklist, playlist['uri'])
        #if input playlist name doesn't match, i is incremented by 1
        else:
            i += 1
        #if i exceeds the number of playlists the user has, the input playlist does not exist
        if i >= len(playlists['items']):
            print ("That playlist does not exist. Please input a valid playlist name.")
            return False


if __name__ == "__main__":

    #checks for sufficient number of arguments
    if len(sys.argv) > 1:
      username = sys.argv[1]
    else:
      print ("Please input the username of the account you would like to access.")
      sys.exit()

    scope = 'playlist-modify-public'
    #get access token
    token = util.prompt_for_user_token(username,scope, client_id,client_secret,redirect_uri)

    if token:
        sp = spotipy.Spotify(auth=token)
        #gets the user's playlist names
        playlists = sp.user_playlists(username)
        print("Here is a list of playlists created by %s: " % (username))
        #prints the names of the users playlists
        for playlist in playlists['items']:
            print (playlist['name'])

        update_name = input('Which playlist do you want to update? ')
        update_info = playlist_tracks(username, playlists, sp, update_name)
        #dict containing track info for playlist you want to update
        update_tracks = update_info[0]
        #variable containing playlist URI of update playlist
        update_id = update_info[1]

        add_name = input('Which playlist do you want to add to %s? ' % (update_name))
        add_info = playlist_tracks(username, playlists, sp, add_name)
        add_tracks = add_info[0]

        #turns track dicts into sets and finds the songs that are in add playlist but not update playlist
        common_tracks1 = set(add_tracks.items())
        common_tracks2 = set(update_tracks.items())
        difference = common_tracks1.difference(common_tracks2)

        #checks if there are tracks to add
        if difference == set():
            print("Playlist is up to date.")
            sys.exit()

        #adds missing tracks
        print ("Tracks added to %s from %s: " %(update_name, add_name))
        trackID = set()
        for item in difference:
            trackID.add(item[0])
            print ('%s by %s' % (item[1][0], item[1][1]))
        sp.trace = False
        new_playlist = sp.user_playlist_add_tracks(username, update_id, trackID)

    else:
        print("Can't get token for", username)
