"""Playlist Track operations for KFJC Trivia Robot."""

from model import db, connect_to_db, PlaylistTrack


def create_playlist_track(playlist_id, indx, is_current, artist, track_title,
    album_title, album_id, album_label, time_played):
    """Create and return a new playlist_track."""

    playlist_track = PlaylistTrack(playlist_id=playlist_id, indx=indx, is_current=is_current, 
        artist=artist, track_title=track_title, album_title=album_title, album_id=album_id,
        album_label=album_label, time_played=time_played)

    db.session.add(playlist_track)
    # Don't forget to call model.db.session.commit() when done adding items.

    return playlist_track


def get_playlist_tracks(limit_to=10):
    """Get all playlist_tracks up to limit_to. There are ~2.5mil rows in this table."""

    return PlaylistTrack.query.limit(limit_to).all()


def get_playlist_track_by_playlist_id_and_indx(playlist_id, indx):
    """Get a playlist_track by playlist_id and indx. The primary key is not the station's playlist_id."""
    return PlaylistTrack.query.filter(
        PlaylistTrack.playlist_id == playlist_id,
        PlaylistTrack.indx == indx).first()
    
def get_playlist_tracks_by_user_id(playlist_id):
    return PlaylistTrack.query.filter(
        PlaylistTrack.playlist_id == playlist_id).all()


if __name__ == '__main__':
    """Will connect you to the database when you run playlist_tracks.py interactively"""
    from server import app
    connect_to_db(app)
