"""Playlist operations for KFJC Trivia Robot."""

from model import db, connect_to_db, Playlist


def create_playlist(playlist_id, user_id, air_name, start_time, end_time):
    """Create and return a new playlist."""

    playlist = Playlist(playlist_id=playlist_id, user_id=user_id, air_name=air_name,
        start_time=start_time, end_time=end_time)

    db.session.add(playlist)
    # Don't forget to call model.db.session.commit() when done adding items.

    return playlist

def get_playlists():
    """Get all playlists."""

    return Playlist.query.all()

def get_playlists_with_limit(limit_to=10):
    """Get all playlists."""
    
    return Playlist.query.limit(limit_to).all()

def get_playlist_by_playlist_id(playlist_id):
    """Get a playlist by id. The primary key is not the station's playlist_id."""

    return Playlist.query.filter(Playlist.playlist_id == playlist_id).first()

def max_date_is_the_freshest_data_stamp():

    from sqlalchemy import func, and_

    subq = db.query(Playlist.identifier,
        func.max(Table.date).label('maxdate')
    ).group_by(Table.identifier).subquery('t2')

    query = session.query(Table).join(
        subq,
        and_(
            Table.identifier == subq.c.identifier,
            Table.date == subq.c.maxdate
        )
    )

    return Playlist.query.filter(Playlist.playlist_id == playlist_id).first()


if __name__ == '__main__':
    """Will connect you to the database when you run playlists.py interactively"""
    from server import app
    connect_to_db(app)
