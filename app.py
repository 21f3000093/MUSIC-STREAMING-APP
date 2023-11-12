from flask import *
from flask_restful import *
from flask_cors import *
from model1 import *

app = Flask(__name__)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydbmtm.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)

app.app_context().push()



##################### functions ##############################

def calculate_avg_rating(s_id):
    ratings = Rating.query.filter_by(song_id=s_id).all()

    total_ratings = len(ratings)
    if total_ratings > 0:
        sum_ratings = sum([rating.rating for rating in ratings])
        avg_rating = sum_ratings / total_ratings
        return avg_rating
    else:
        return 0  # Return 0 if there is no rating


########################### login, register Controllers ##########################################
##################################################################################################
##################################################################################################


# Index page
@app.route("/", methods=["GET", "POST"])
def index_page():
    return render_template("index.html")


# user login
@app.route("/user_login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "GET":
        return render_template("login_form.html")

    if request.method == "POST":
        u_name = request.form.get("u_name")
        u_password = request.form.get("u_password")

        user = User.query.filter_by(username=u_name).first()

        if user:
            if user.password == u_password:
                user.isloggedin = True
                db.session.commit()

                return redirect("/home/{}".format(user.user_id))

            elif user.password != u_password:
                msg = "Username or Password is incorrect! Try Again!"
                return render_template("error.html", msg=msg)

        else:
            msg = "Username not found! Register as a new User."
            return render_template("error.html", msg=msg)


# user logout
@app.route("/user_logout/<int:u_id>", methods=["GET", "POST"])
def logout(u_id):
    user = User.query.get(u_id)
    user.isloggedin = False
    db.session.commit()

    return redirect("/")


# Register new user


@app.route("/register_user", methods=["GET", "POST"])
def register_user():
    msg = ""
    if request.method == "GET":
        return render_template("register_user_form.html")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        user = User.query.filter_by(username=username).first()

        if user:
            msg = "Username already exist! try another username."
            return render_template("error.html", msg=msg)

        else:
            u1 = User(username=username, password=password, email=email)

            db.session.add(u1)
            db.session.commit()
            return redirect("/user_login")
        



################################   NORMAL USER CONTROLLERS   ###########################################
########################################################################################################
########################################################################################################


######    Home page for  user (when logged in )

@app.route("/home/<int:u_id>", methods=["GET", "POST"])
def home_page(u_id):
    songs = Song.query.filter(Song.song_flag==False).all()
    albums = Album.query.filter(Album.album_flag==False).all()
    playlists=Playlist.query.all()
    user = User.query.get(u_id)
    song_genres = Song.query.with_entities(Song.song_genre).distinct().filter(Song.song_flag==False).all()
    song_genre_list = [genre[0] for genre in song_genres]


    if user.isloggedin:
        return render_template("home.html", songs=songs, albums=albums, user=user,playlists=playlists,song_genres=song_genre_list)

    else:
        return redirect("/")
    


### play song
@app.route("/play_song/<int:u_id>/<int:s_id>", methods=["GET", "POST"])
def play_song(s_id, u_id):
    song = Song.query.get(s_id)
    user = User.query.get(u_id)

    song.song_play_count += 1
    db.session.commit()
    return render_template("play_song.html",user=user,song=song)


#### Add a playlist
@app.route("/add_playlist/<int:u_id>", methods=["GET", "POST"])
def add_playlist(u_id):

    songs = Song.query.filter(Song.song_flag==False).all()    
    user = User.query.get(u_id)

    if request.method=="GET":
        return render_template("add_playlist_form.html",user=user,songs=songs)
    
    if request.method=="POST":

        song_id_list=request.form.getlist("song_id_list")
        playlist_name= request.form.get("playlist_name")

        p1=Playlist(
            playlist_name=playlist_name,
            user_id=u_id,
        )

        db.session.add(p1)
        db.session.commit()

        p_id=p1.playlist_id

        for s_id in song_id_list:
            ps1=Playlist_Songs(
                playlist_id=p_id,
                song_id=s_id,
            )
            
            db.session.add(ps1)
            db.session.commit()
    
        return redirect("/home/{}".format(u_id))
    


##### show all playlist songs 
@app.route("/playlist_songs/<int:u_id>/<int:p_id>", methods=["GET", "POST"])
def playlist_songs(u_id,p_id):
    user = User.query.get(u_id)
    playlist=Playlist.query.get(p_id)

    playlist_songs = Playlist_Songs.query.filter_by(playlist_id=p_id).all()

    songs=[]
    for p_songs in playlist_songs:
        s_id=p_songs.song_id
        song=Song.query.get(s_id)
        songs.append(song)

    
    if request.method=="GET":
        return render_template("playlists_songs.html",user=user,songs=songs,playlist=playlist)    
    
    

# Normal user account song lyrics page
@app.route("/user_song_lyrics/<int:u_id>/<int:s_id>", methods=["GET", "POST"])
def user_song_lyrics(s_id, u_id):
    song = Song.query.get(s_id)
    user = User.query.get(u_id)
    return render_template("user_song_lyrics.html", song=song, user=user)


###  rate a song
@app.route("/rate_song/<int:u_id>/<int:s_id>", methods=["GET", "POST"])
def rate_song(s_id, u_id):
    song = Song.query.get(s_id)
    user = User.query.get(u_id)
    rating = Rating.query.filter_by(user_id=u_id ,song_id=s_id ).first()


    if request.method == "GET":
        return render_template("rate_song.html", song=song, user=user)

    if request.method == "POST":
        rate = int(request.form.get("s_rate"))


        if rating:
            rating.rating=rate
            db.session.commit()
            
            song.song_avg_rating = calculate_avg_rating(song.song_id)
            db.session.commit()
            return redirect("/home/{}".format(u_id))
        
        else:
            
            r1 = Rating(
                user_id=u_id,
                song_id=s_id,
                rating=rate,
            )

            db.session.add(r1)
            db.session.commit()

            
            song.song_avg_rating = calculate_avg_rating(song.song_id)
            db.session.commit()
            return redirect("/home/{}".format(u_id))


#######  All Songs (show more)
@app.route("/all_songs/<int:u_id>")
def all_songs(u_id):
    songs = Song.query.filter(Song.song_flag==False).all()   
    user = User.query.get(u_id)

    return render_template("all_songs_page.html",user=user,songs=songs) 

#######  All Albums (show more)
@app.route("/all_albums/<int:u_id>")
def all_albums(u_id):
    albums = Album.query.filter(Album.album_flag==False).all()   
    user = User.query.get(u_id)

    return render_template("all_albums_page.html",user=user,albums=albums) 

#######  All Playlists (show more)
@app.route("/all_playlists/<int:u_id>")
def all_playlists(u_id):
    albums = Album.query.filter(Album.album_flag==False).all()   
    user = User.query.get(u_id)
    playlists=Playlist.query.all()

    return render_template("all_playlists_page.html",user=user,albums=albums,playlists=playlists) 



    
####### all songs of an album for Normal user account


@app.route("/album_songs/<int:u_id>/<int:a_id>", methods=["GET", "POST"])
def album_songs(a_id, u_id):
    # songs = Song.query.filter(album_id=a_id)
    user = User.query.get(u_id)
    
    songs = Song.query.filter(Song.song_flag==False , Song.album_id==a_id).all()
    album = Album.query.get(a_id)
    return render_template(
        "album_songs.html", songs=songs, album=album, user=user
    )


### search songs and albums

@app.context_processor
def search_processor():
    return {'searched': request.form.get("searched")}

@app.route("/search_user/<int:u_id>", methods=["GET", "POST"])
def search_user(u_id):
    user = User.query.get(u_id)
    searched = request.form.get("searched")
    songs = []
    albums = []

    if searched:
        
        songs = Song.query.filter(
            (Song.song_name.like('%' + searched + '%')) |
            (Song.song_artist.like('%' + searched + '%')) |
            (Song.song_genre.like('%' + searched + '%')) , Song.song_flag==False
        ).all()

        albums = Album.query.filter(
            (Album.album_name.like('%' + searched + '%')) |
            (Album.album_artist.like('%' + searched + '%')) |
            (Album.album_genre.like('%' + searched + '%')) , Album.album_flag==False
        ).all()

        

    return render_template("search_user.html", songs=songs,albums=albums, user=user)



##################################   Creator page  ##################################################
#####################################################################################################
#####################################################################################################

@app.route("/home/<int:u_id>/creator_account", methods=["GET", "POST"])
def creator_account(u_id):
    user = User.query.get(u_id)
    songs = Song.query.filter_by(creator_id=u_id).all()
    albums = Album.query.filter_by(creator_id=u_id).all()
    # s_count=len(songs)
    
    avg_rating=0
    sum_ratings=0
    if songs:
        for song in songs :
            sum_ratings += song.song_avg_rating


        avg_rating=(sum_ratings/len(songs))



    if request.method == "GET":
        if user.user_role_id == 1:
            return render_template("creator_account.html", user=user, songs=songs, albums=albums,avg_rating=avg_rating)
        else:
            return render_template("register_creator_form.html", user=user)

    if request.method == "POST":
        user.user_role_name = "creator"
        user.user_role_id = 1
        db.session.commit()
        return redirect("/home/{}/creator_account".format(u_id))


####### all songs of an album for creator account

@app.route("/creator_album_songs/<int:u_id>/<int:a_id>", methods=["GET", "POST"])
def creator_album_songs(a_id, u_id):
    # songs = Song.query.filter(album_id=a_id)
    user = User.query.get(u_id)
    songs = Song.query.filter_by(album_id=a_id).all()
    album = Album.query.get(a_id)
    return render_template(
        "creator_album_songs.html", songs=songs, album=album, user=user)


##### add songs to an album
@app.route("/add_album_song/<int:u_id>/<int:a_id>", methods=["GET", "POST"])
def add_album_song(a_id, u_id):
    user = User.query.get(u_id)
    album = Album.query.get(a_id)
    if request.method == "GET":
        return render_template("add_album_song_form.html", album=album, user=user)

    if request.method == "POST":
        s_name = request.form.get("s_name")
        s_artist = request.form.get("s_artist")
        s_language = request.form.get("s_language")
        s_genre = request.form.get("s_genre")
        s_lyrics = request.form.get("s_lyrics")
        s_duration = request.form.get("s_duration")
        s_release_date = request.form.get("s_release_date")
        s_creator_id = u_id

        s_path = request.form.get("s_path")
        s_thumbnail = request.form.get("s_thumbnail")

        s1 = Song(
            song_name=s_name,
            song_artist=s_artist,
            song_language=s_language,
            song_genre=s_genre,
            song_lyrics=s_lyrics,
            song_duration=s_duration,
            release_date=s_release_date,
            creator_id=s_creator_id,
            song_path=s_path,
            song_thumbnail=s_thumbnail,
            album_id=a_id,
        )

        db.session.add(s1)
        db.session.commit()
        return redirect("/home/{}/creator_account".format(u_id))


# delete an album song
@app.route(
    "/delete_album_song/<int:u_id>/<int:a_id>/<int:s_id>", methods=["GET", "POST"]
)
def delete_album_song(s_id, u_id, a_id):
    song = Song.query.get(s_id)
    user = User.query.get(u_id)
    if request.method == "GET":
        db.session.delete(song)
        db.session.commit()
        return redirect("/creator_album_songs/{}/{}".format(u_id, a_id))


# add new songs
@app.route("/add_song/<int:u_id>", methods=["GET", "POST"])
def add_song(u_id):
    user = User.query.get(u_id)
    if request.method == "GET":
        return render_template("add_song_form.html", user=user)

    if request.method == "POST":
        s_name = request.form.get("s_name")
        s_artist = request.form.get("s_artist")
        s_language = request.form.get("s_language")
        s_genre = request.form.get("s_genre")
        s_lyrics = request.form.get("s_lyrics")
        s_duration = request.form.get("s_duration")
        s_release_date = request.form.get("s_release_date")
        s_creator_id = u_id

        s_path = request.form.get("s_path")
        s_thumbnail = request.form.get("s_thumbnail")

        s1 = Song(
            song_name=s_name,
            song_artist=s_artist,
            song_language=s_language,
            song_genre=s_genre,
            song_lyrics=s_lyrics,
            song_duration=s_duration,
            release_date=s_release_date,
            creator_id=s_creator_id,
            song_path=s_path,
            song_thumbnail=s_thumbnail,
        )

        db.session.add(s1)
        db.session.commit()
        return redirect("/home/{}/creator_account".format(u_id))


# creator account song lyrics page
@app.route("/creator_song_lyrics/<int:u_id>/<int:s_id>", methods=["GET", "POST"])
def creator_song_lyrics(s_id, u_id):
    song = Song.query.get(s_id)
    user = User.query.get(u_id)
    return render_template("creator_song_lyrics.html", song=song, user=user)




#### edit / update a song
@app.route("/edit_song/<int:u_id>/<int:s_id>", methods=["GET", "POST"])
def update_song(s_id, u_id):
    song = Song.query.get(s_id)
    user = User.query.get(u_id)
    if request.method == "GET":
        return render_template("update_song.html", song=song, user=user)

    if request.method == "POST":
        song.song_name = request.form.get("s_name")
        song.song_artist = request.form.get("s_artist")
        song.song_language = request.form.get("s_language")
        song.song_genre = request.form.get("s_genre")
        song.song_lyrics = request.form.get("s_lyrics")
        song.song_duration = request.form.get("s_duration")
        song.release_date = request.form.get("s_release_date")
        song.song_path = request.form.get("s_path")
        song.song_thumbnail = request.form.get("s_thumbnail")

        db.session.commit()

        return redirect("/home/{}/creator_account".format(u_id))


# dekete a song
@app.route("/delete_song/<int:u_id>/<int:s_id>", methods=["GET", "POST"])
def delete_song(s_id, u_id):
    song = Song.query.get(s_id)
    user = User.query.get(u_id)
    if request.method == "GET":
        db.session.delete(song)
        db.session.commit()
        return redirect("/home/{}/creator_account".format(u_id))


########## add new album


@app.route("/add_album/<int:u_id>", methods=["GET", "POST"])
def add_album(u_id):
    user = User.query.get(u_id)
    if request.method == "GET":
        return render_template("add_album_form.html", user=user)

    if request.method == "POST":
        a_name = request.form.get("a_name")
        a_genre = request.form.get("a_genre")
        a_artist = request.form.get("a_artist")
        a_thumbnail = request.form.get("a_thumbnail")

        a1 = Album(
            album_name=a_name,
            album_genre=a_genre,
            album_artist=a_artist,
            album_thumbnail=a_thumbnail,
            creator_id=u_id,
        )

        db.session.add(a1)
        db.session.commit()
        return redirect("/home/{}/creator_account".format(u_id))


# edit / update a album
@app.route("/edit_album/<int:u_id>/<int:a_id>", methods=["GET", "POST"])
def update_album(a_id, u_id):
    album = Album.query.get(a_id)
    user = User.query.get(u_id)
    if request.method == "GET":
        return render_template("update_album.html", album=album, user=user)

    if request.method == "POST":
        album.album_name = request.form.get("a_name")
        album.album_genre = request.form.get("a_genre")
        album.album_artist = request.form.get("a_artist")
        album.album_thumbnail = request.form.get("a_thumbnail")
        album.creator_id = u_id

        db.session.commit()

        return redirect("/home/{}/creator_account".format(u_id))


# delete a Album
@app.route("/delete_album/<int:u_id>/<int:a_id>", methods=["GET", "POST"])
def delete_album(a_id, u_id):
    album = Album.query.get(a_id)
    user = User.query.get(u_id)
    if request.method == "GET":
        db.session.delete(album)
        db.session.commit()
        return redirect("/home/{}/creator_account".format(u_id))
    



###############################   ADMINISTRATOR  CONTROLLERS   #############################################
############################################################################################################
############################################################################################################
    

# Admin login
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    msg = ""
    if request.method == "GET":
        return render_template("admin_login_form.html")
    
    if request.method == "POST":
        a_name = request.form.get("a_name")
        a_password = request.form.get("a_password")

        admin = Admin.query.filter_by(admin_name=a_name).first()

        if admin:
            if admin.password == a_password:
                admin.isloggedin = True
                db.session.commit()

                return redirect("/admin_home/{}".format(admin.admin_id))

            elif admin.password != a_password:
                msg = "AdminName or Password is incorrect! Try Again!"
                return render_template("error.html", msg=msg)

        else:
            msg = "AdminName not found! "
            return render_template("error.html", msg=msg)



######    Home page for  Admin (when logged in )

@app.route("/admin_home/<int:a_id>", methods=["GET", "POST"])
def admin_home_page(a_id):
    songs = Song.query.all()
    albums = Album.query.all()
    playlists=Playlist.query.all()
    admin = Admin.query.get(a_id)
    users=User.query.all()
    creators=User.query.filter_by(user_role_id=1).all()
    genres = Song.query.with_entities(Song.song_genre).distinct().all()
    genre_list = [genre[0] for genre in genres]

    if admin.isloggedin:
        return render_template("admin_home.html", songs=songs, albums=albums, admin=admin,playlists=playlists,users=users,creators=creators,genres=genre_list)

    else:
        return redirect("/")
    

## admin logout
@app.route("/admin_logout/<int:a_id>", methods=["GET", "POST"])
def admin_logout(a_id):
    admin = Admin.query.get(a_id)
    admin.isloggedin = False
    db.session.commit()

    return redirect("/")

### all creators page
@app.route("/all_creators/<int:a_id>")
def all_creators(a_id):
    admin = Admin.query.get(a_id)
    creators=User.query.filter_by(user_role_id=1).all()

    return render_template("admin_all_creators.html",creators=creators, admin=admin)

### flag a creator 
@app.route("/flag_creator/<int:a_id>/<int:c_id>")
def flag_creator(a_id,c_id):
    user = User.query.get(c_id)
    songs = Song.query.filter(Song.creator_id==c_id).all()
    albums = Album.query.filter(Album.creator_id==c_id).all()
    

    if user.user_flag == False:
        user.user_flag=True
        for song in songs:
            song.song_flag=True

        for album in albums:
            album.album_flag=True

        db.session.commit()
        return redirect("/all_creators/{}".format(a_id))
    
    else:
        user.user_flag=False
        for song in songs:
            song.song_flag=False

        for album in albums:
            album.album_flag=False

        db.session.commit()
        return redirect("/all_creators/{}".format(a_id))

    
 ##### creator uploads summary   
@app.route("/creator_uploads/<int:a_id>/<int:c_id>")
def creator_uploads(a_id,c_id):
    user = User.query.get(c_id)
    admin = Admin.query.get(a_id)
    songs = Song.query.filter(Song.creator_id==c_id).all()
    albums = Album.query.filter(Album.creator_id==c_id).all()

    avg_rating=0
    sum_ratings=0
    if songs:
        for song in songs :
            sum_ratings += song.song_avg_rating


        avg_rating=(sum_ratings/len(songs))


    return render_template("admin_creator_uploads.html",songs =songs,albums=albums , admin=admin,creator=user ,avg_rating=avg_rating)





# all songs admin account 
@app.route("/admin_songs/<int:a_id>", methods=["GET", "POST"])
def admin_songs(a_id):
    admin = Admin.query.get(a_id)
    songs = Song.query.all()
    genres = Song.query.with_entities(Song.song_genre).distinct().all()
    genre_list = [genre[0] for genre in genres]
    if admin.isloggedin:
        return render_template("admin_songs.html", songs=songs, admin=admin,genres=genre_list)

    else:
        return redirect("/")
    
# flag a song
@app.route("/flag_song/<int:a_id>/<int:s_id>")
def flag_song(s_id,a_id):
    admin = Admin.query.get(a_id)
    song = Song.query.get(s_id)
    song.song_flag = not song.song_flag
    db.session.commit()
    return redirect("/admin_songs/{}".format(a_id))



# delete a song (for admin )
@app.route("/admin_delete_song/<int:a_id>/<int:s_id>", methods=["GET", "POST"])
def admin_delete_song(s_id, a_id):
    song = Song.query.get(s_id)
    
    if request.method == "GET":
        db.session.delete(song)
        db.session.commit()
        return redirect("/admin_songs/{}".format(a_id))
    

##### admin song lyrics page
@app.route("/admin_song_lyrics/<int:a_id>/<int:s_id>", methods=["GET", "POST"])
def admin_song_lyrics(s_id, a_id):
    song = Song.query.get(s_id)
    admin = Admin.query.get(a_id)
    



    return render_template("admin_song_lyrics.html", song=song, admin=admin)


## all albums (admin)
@app.route("/admin_albums/<int:a_id>", methods=["GET", "POST"])
def admin_albums(a_id):
    admin = Admin.query.get(a_id)
    songs = Song.query.all()
    albums=Album.query.all()
    genres = Album.query.with_entities(Album.album_genre).distinct().all()
    genre_list = [genre[0] for genre in genres]
    if admin.isloggedin:
        return render_template("admin_albums.html", songs=songs, admin=admin,genres=genre_list,albums=albums)

    else:
        return redirect("/")
    


 ####### all songs of an album for admin account

@app.route("/admin_album_songs/<int:a_id>/<int:alb_id>", methods=["GET", "POST"])
def admin_album_songs(a_id, alb_id):
    admin = Admin.query.get(a_id)
    songs = Song.query.filter_by(album_id=alb_id).all()
    album = Album.query.get(alb_id)
    return render_template(
        "admin_album_songs.html", songs=songs, album=album, admin=admin)



### flag a album
@app.route("/flag_album/<int:a_id>/<int:alb_id>")
def flag_album(a_id,alb_id):
    admin = Admin.query.get(a_id)
    album = Album.query.get(alb_id)
    songs = Song.query.filter_by(album_id=alb_id).all()
    # album.album_flag = not album.album_flag  # will add after the update in album model
    # db.session.commit()
    if album.album_flag == False:
        album.album_flag = True
        for song in songs:
            song.song_flag = True

        db.session.commit()
        return redirect("/admin_albums/{}".format(alb_id))
    
    else:
        album.album_flag = False
        for song in songs:
            song.song_flag = False

        db.session.commit()
        return redirect("/admin_albums/{}".format(alb_id))
    








# delete a album (for admin )
@app.route("/admin_delete_album/<int:a_id>/<int:alb_id>", methods=["GET", "POST"])
def admin_delete_album(a_id,alb_id):
    album = Album.query.get(alb_id)
    
    if request.method == "GET":
        db.session.delete(album)
        db.session.commit()
        return redirect("/admin_albums/{}".format(a_id))
    

# searched page for admin 
@app.route("/search_admin/<int:a_id>", methods=["GET", "POST"])
def search_admin(a_id):
    admin = Admin.query.get(a_id)
    searched = request.form.get("searched")
    songs = []
    

    if searched:
        
        songs = Song.query.filter(
            (Song.song_name.like('%' + searched + '%')) |
            (Song.song_artist.like('%' + searched + '%')) |
            (Song.song_genre.like('%' + searched + '%'))
        ).all()

  
    return render_template("search_admin.html", songs=songs,admin=admin)

   




########################################################################################
if __name__ == "__main__":
    app.run(debug=True)
