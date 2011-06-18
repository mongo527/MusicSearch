import pylast, sys, sqlite3, os, re
from musicbrainz2.webservice import Query, ArtistFilter, WebServiceError
import musicbrainz2.webservice as ws
import musicbrainz2.model as model

# Notifo API settings
USERNAME = ""
API_KEY = ""

# NZBMatrix Account Details
#API_URL = "http://api.nzbmatrix.com/v1.1/search.php?search=" + searchTerm + #"&catid=22&age=800&username=burningfire&apikey=75390295cf99a1db49c9314c86061405"

connection = sqlite3.connect('musicSearch.db')
cursor = connection.cursor()

q = Query()
query = ArtistFilter("Streetlight Manifesto", limit = 2)
artistResults = q.getArtists(query)

path = "C:\Users\Mongo\Music\iTunes\iTunes Media\Music"
unknown = ".+unknown.+"

itunesArtist = os.listdir(path)
artistExists = 0

def findArtist():
    artistName = cursor.execute('SELECT ArtistName FROM Artists')
    
    for i in itunesArtist:
        try:
            filter = ArtistFilter(i, limit = 2)
            artistResults = q.getArtists(filter)
        except WebServiceError, e:
            print 'Could not find artist ' + i
            sys.exit(1)
        
    for result in artistResults:
        for j in itunesArtist:
            if j != "Unknown Artist":
                artist = result.artist
                if j == artist:
                    artistName = artist.name
                    artistID = artist.id
                    print artistName
                    print
                    print artistID
        
                
def checkAlbums(numAlbums, albumName, artist):
    numAlbumsOwned = cursor.execute('SELECT NumAlbums FROM Artists')
    albumsOwned = cursor.execute('SELECT AlbumName FROM Albums')
    
    if numAlbumsOwned != numAlbums:
        for album in albumsOwned:
            if album != albumName:
                #notifo.send_notification(USERNAME, API_KEY, USERNAME, artist + ": " + albumName, "Music", "New Album Found")
                print "This is where Notifo comes in!"
        else:
            print "No new Albums"

def addArtists(mbid, name, albums):
    DBArtist = cursor.execute('SELECT ArtistName FROM Artists')
    
    for i in itunesArtist:
#        if i != name:
        cursor.execute('''INSERT INTO Artists (ArtistMBID, ArtistName, NumAlbums)
        VALUES (?, ?, ?)''', (mbid, name, 3))
#        else:
#            print "Artist already exists"
    
def addAlbums(mbid, name):
    if name == getAlbum():
        cursor.execute('''INSERT INTO Albums (AlbumMBID, AlbumName)
        VALUES (?, ?)''', (mbid, name))
    else:
        print "Album already exists"

def main():
    z = ws.Query()
    try:
        inc = ws.ArtistIncludes (
            releases = (model.Release.TYPE_OFFICIAL, model.Release.TYPE_ALBUM),
            tags = False, releaseGroups = False)
        artist = z.getArtistById("http://musicbrainz.org/artist/cbc9199f-944b-42e9-a945-627c9fc0ba6e", inc)
    except ws.WebServiceError, e:
        print 'Error:', e
        sys.exit(1)

    numAlbums = len(artist.getReleases())
#    addArtists(artist.id, artist.name, numAlbums)
    findArtist()

#    if len(artist.getReleases()) == 0:
#        print "No Albums found by " + artist.name
#        sys.exit(1)
#    else:
#        for release in artist.getReleases():
#            addAlbums(release.id, release.title)
#            checkAlbums(numAlbums, release.title, artist.name)
    
    connection.commit()
            
    cursor.close()
    
if __name__ == '__main__': main()