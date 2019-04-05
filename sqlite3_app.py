# app.py
from flask import Flask, session, redirect, render_template
from flask import request, make_response, json
from functools import wraps
import sqlite3
from flask import g

app = Flask(__name__)
app.secret_key = "notSoObviousSecretKey"

DATABASE = 'chinook.db'
tracks_keys = [
    "album_id",
    "media_type_id",
    "genre_id",
    "name",
    "composer",
    "milliseconds",
    "bytes",
    "price"
]


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/genres', methods=['GET'])
def genres():
    db = get_db()
    data = db.execute("SELECT genres.name, (SELECT COUNT(*) FROM tracks WHERE GenreId = genres.GenreId) FROM genres "
                      "ORDER BY genres.name").fetchall()
    data_dict = {row[0]: row[1] for row in data}
    return json.jsonify(data_dict), 200


@app.route('/tracks', methods=['GET', 'POST'])
def tracks():
    if request.method == 'GET':
        artist = request.args.get('artist')
        per_page = request.args.get('per_page', type=int)
        page = request.args.get('page', type=int)

        if per_page is not None and page is None:
            page = 1

        db = get_db()
        if artist is None:
            if per_page is not None and page is not None:
                data = db.execute('SELECT name FROM tracks ORDER BY name COLLATE NOCASE LIMIT ? OFFSET ?', (per_page, (page - 1)*per_page)).fetchall()
            else:
                data = db.execute('SELECT name FROM tracks ORDER BY name COLLATE NOCASE').fetchall()

        else:
            if per_page is not None and page is not None:
                data = db.execute('SELECT name FROM tracks WHERE AlbumId IN (SELECT AlbumId FROM albums '
                                  'WHERE ArtistId IN (SELECT ArtistId FROM artists WHERE Name = ?)) '
                                  'ORDER BY name COLLATE NOCASE LIMIT ? OFFSET ?'
                                  , (artist, per_page, (page - 1) * per_page)).fetchall()
            else:
                data = db.execute('SELECT name FROM tracks WHERE AlbumId IN (SELECT AlbumId FROM albums '
                                  'WHERE ArtistId IN (SELECT ArtistId FROM artists WHERE Name = ?)) '
                                  'ORDER BY name COLLATE NOCASE', (artist, )).fetchall()

        data = [elem[0] for elem in data]
        return json.jsonify(data)
    if request.method == 'POST':
        new_track = request.get_json(force=True)
        for tkey in tracks_keys:
            if tkey not in new_track.keys():
                return '', 400
        db = get_db()
        trackId = db.execute('SELECT MAX(TrackId) FROM tracks').fetchone()
        trackId = trackId[0] + 1
        data_to_insert = (trackId, new_track['name'], new_track['album_id'], new_track['media_type_id'],
                          new_track['genre_id'], new_track['composer'], new_track['milliseconds'],
                          new_track['bytes'], new_track['price'])
        db.execute('INSERT INTO tracks (TrackId, Name, AlbumId, MediaTypeId, GenreId, Composer, Milliseconds, '
                   'Bytes, UnitPrice) VALUES (?, ?, ?, ?, ?, ?,?,?,?)', data_to_insert)
        return json.jsonify(new_track), 200

if __name__ == '__main__':
    app.run(debug=True)
