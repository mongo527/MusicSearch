import pylast, sys, sqlite3, os, re, notifo
from musicbrainz2.webservice import Query, ArtistFilter, WebServiceError
import musicbrainz2.webservice as ws
import musicbrainz2.model as model

# Notifo API settings
USERNAME = "mongo527"
API_KEY = "xdcba2f866515d5f417c98b49d3198cb97512b12b"

# NZBMatrix Account Details
#API_URL = "http://api.nzbmatrix.com/v1.1/search.php?search=" + searchTerm + #"&catid=22&age=800&username=burningfire&apikey=75390295cf99a1db49c9314c86061405"

connection = sqlite3.connect('musicSearch.db')
cursor = connection.cursor()

q = Query()
z = ws.Query()

path = "C:\Users\Mongo\Music\iTunes\iTunes Media\Music"
unknown = ".+unknown.+"

numAlbums = None

itunesArtist = os.listdir(path)

def findArtist():
    artistName = cursor.execute('SELECT ArtistName FROM Artists')
    count = 1
    
#    for i in itunesArtist:
    try:
        filter = ArtistFilter("Sum 41", limit = 5)
        artistResults = q.getArtists(filter)
    except WebServiceError, e:
        print 'Error:', e
        sys.exit(1)
     
    print
    for result in artistResults:
        artist = result.artist
        print "Number:      ", count
        print "Unique Name: ", artist.getUniqueName()
        print "ID:          ", artist.id
        print
        count += 1
    
    selection = raw_input("Please Select the [Number] of the correct Artist: ")
    
    count = 1
    artist = None
    for result in artistResults:
        artist = result.artist
        if int(selection) == count:
            getAlbumNum(artist.id)
            print
            print artist.name, "will be added to the database!"
            break
        count += 1
    
    return artist

def findAlbumsOwned(artist):
    albumPath = 'C:\Users\Mongo\Music\iTunes\iTunes Media\Music\%s' % artist.name
    itunesAlbums = os.listdir(albumPath)
    checkAlbum = dict()
    album = ()
    albumList = []
    
    try:
        inc = ws.ArtistIncludes (
            releases = (model.Release.TYPE_OFFICIAL, model.Release.TYPE_ALBUM),
            tags = False, releaseGroups = False)
        artist = z.getArtistById(artist.id, inc)
    except ws.WebServiceError, e:
        print 'Error:', e
        sys.exit(1)
    
    for release in artist.getReleases():
        if release.title in itunesAlbums:
            code = 2
#            print release.title, "will be added to the database!"
            album = (release.title, release.id, code,)
            albumList.append(album)
#            print album
        elif release.title not in itunesAlbums:
            code = 0
#            print release.title, "will be added to the database!"
            album = (release.title, release.id, code,)
            albumList.append(album)
#            print album
            
    return albumList
            
def getAlbumNum(id):

    global numAlbums
    
    try:
        inc = ws.ArtistIncludes (
            releases = (model.Release.TYPE_OFFICIAL, model.Release.TYPE_ALBUM),
            tags = False, releaseGroups = False)
        artist = z.getArtistById(id, inc)
    except ws.WebServiceError, e:
        print 'Error:', e
        sys.exit(1)
        
    numAlbums = len(artist.getReleases())
    
    return numAlbums
        
def sendNotifo(album, artist):
        
#   notifo.send_notification(USERNAME, API_KEY, USERNAME, album[2] + " by " + artist, "Music", "Missing Albums")
        
    cursor.execute('UPDATE Albums SET Code=1 WHERE AlbumMBID=?', (album[1],))

        
def addArtist(artist):
    
    cursor.execute('''INSERT INTO Artists (ArtistMBID, ArtistName, NumAlbums) 
    VALUES (?, ?, ?)''', (artist.id, artist.name, numAlbums))
        
    connection.commit()

def addAlbum(album, artist):

    cursor.execute('''INSERT INTO Albums (AlbumMBID, AlbumName, ArtistMBID, Code)
    VALUES (?, ?, ?, ?)''', (album[1], album[0], artist.id, album[2]))
    
    connection.commit()
    
def compareAlbums():

    DBArtist = cursor.execute('SELECT * FROM Artists')
    DBArtistFetch = DBArtist.fetchall()

    print
    print "Checking for new albums!"
    
    for i in DBArtistFetch:
        DBAlbum = cursor.execute('SELECT * FROM Albums WHERE ArtistMBID = ? AND Code = 0', (i[1],))
        allAlbums = DBAlbum.fetchall()
#        print len(DBAlbum.fetchall())
        if allAlbums:
            print
            print "Albums Missing!"
            for j in allAlbums:
                sendNotifo(j, i[2])
#                print j[2], "is missing..."
#                albumsMissing = findAlbumsMissing(allAlbums)
        else:
            print "No New Albums Found!"

def main():

    artist = findArtist()
    DBArtist = cursor.execute('SELECT ArtistName FROM Artists WHERE ArtistMBID = ?', (artist.id,))
    
    if DBArtist.fetchone() is None:
        addArtist(artist)
        print artist.name, "was successfully added!"
    else:
        print artist.name, "already exists in the database."
        
    releaseList = findAlbumsOwned(artist)
    for release in releaseList:
        DBAlbum = cursor.execute('SELECT DISTINCT AlbumName FROM Albums WHERE AlbumName = ?', (release[0],))
#        print DBAlbum.fetchone()
        if DBAlbum.fetchone() is None:
            addAlbum(release, artist)
            print release[0], "was successfully added!"
        elif DBAlbum.fetchone() is not None:
            pass
#            print release[0], "already exists in the database."
    
    selection = raw_input("Would you like to check for new albums? ")
    
    if selection is "n":
        print
        print "Goodbye!"
    elif selection is "y":
        compareAlbums()
    
    cursor.close()
    
if __name__ == '__main__': main()







#Add every album to the database add column with code:
#0 = Do not own
#1 = Notified
#2 = Owned