from flask_sqlalchemy import *

db = SQLAlchemy()


# User Model
class User(db.Model):
    user_id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_role_name = db.Column(db.String(20), nullable=False ,default="general_user")
    user_role_id = db.Column(db.Integer(), default=0, nullable=False) #(for normal user = 0 ; for creator = 1 )
    isloggedin = db.Column(db.Boolean(),default=False,nullable=False)
    user_flag = db.Column(db.Boolean,default=False)

    def __repr__(self):
        return "%r" % self.username




class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    # total_users = db.Column(db.Integer)
    # total_creators = db.Column(db.Integer)
    # total_albums = db.Column(db.Integer)
    # total_songs = db.Column(db.Integer)
    isloggedin = db.Column(db.Boolean(),default=False,nullable=False)

# SOng model


class Song(db.Model):
    song_id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(100), nullable=False)
    song_artist = db.Column(db.String(100))
    song_language = db.Column(db.String(30))
    song_genre = db.Column(db.String(50))
    song_lyrics = db.Column(db.String(1000))
    song_duration = db.Column(db.Integer)  # in seconds
    release_date = db.Column(db.String(20))
    creator_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey("album.album_id") ,default=None)
    song_path = db.Column(db.String(255),default=None)
    song_thumbnail = db.Column(db.String(255),default=None)
    song_play_count = db.Column(db.Integer, default=0)
    song_flag = db.Column(db.Boolean,default=False)

    creator = db.relationship("User", backref="songs")

    def __repr__(self):
        return "%r" % self.song_name


# Album Model
class Album(db.Model):
    album_id = db.Column(db.Integer, primary_key=True)
    album_name = db.Column(db.String(100), nullable=False)
    album_genre = db.Column(db.String(50))
    album_artist = db.Column(db.String(100))
    creator_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    album_play_count = db.Column(db.Integer, default=0)
    album_thumbnail = db.Column(db.String(255))

    songs = db.relationship("Song", backref="albums",cascade="all, delete")
    creator = db.relationship("User", backref="albums")

    def __repr__(self):
        return "%r" % self.album_name


# playlist model
class Playlist(db.Model):
    playlist_id = db.Column(db.Integer, primary_key=True)
    playlist_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    
    playlist_songs = db.relationship("Playlist_Songs", backref="playlist",cascade="all, delete")

    user = db.relationship("User", backref="playlists")

    def __repr__(self):
        return "%r" % self.playlist_name


class Playlist_Songs(db.Model):
    playlist_id = db.Column(db.Integer, db.ForeignKey("playlist.playlist_id"), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey("song.song_id"), primary_key=True)


class Rating(db.Model):
    rating_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    song_id = db.Column(db.Integer, db.ForeignKey("song.song_id"))
    rating = db.Column(db.Integer,default=None)
    user = db.relationship("User", backref="ratings")
    song = db.relationship("Song", backref="ratings")



