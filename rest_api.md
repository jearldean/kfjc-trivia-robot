**KFJC Trivia Robot REST API**
----
Fetch serveral kinds of json dumps from the trivia database.

<br>

***1. Get Playlist by kfjc_playlist_id:***

Find out when a DJ played a show.

* **URL**

   * ` /playlists/kfjc_playlist_id=<integer> `

* **Method:**
  
  < `GET` >
  
*  **URL Params**

   There are about 66,000 shows collected going back to 1995.

   **Required:**
 
   `kfjc_playlist_id=[integer]`

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** 
    ```
    {
        "start_time": "2022-02-13T15:01:06",
        "end_time": "2022-02-13T19:01:31",
        "dj_id": 177,
        "kfjc_playlist_id": 66582,
        "air_name": "Spliff Skankin"
    }
 
* **Error Response:**

  TODO

* **Sample Call:**

  * `curl -v http://0.0.0.0:5000/playlists/66582`

<br><br><br>
TODO: Added an API: Playlist Tracks
# http://0.0.0.0:5000/playlist_tracks/66582
# http://0.0.0.0:5000/playlist_tracks/66581
Lists the songs played during a show.

<br><br><br>


TODO:
New schema:
# http://0.0.0.0:5000/dj_favorites/album/dj_id=255
# http://0.0.0.0:5000/dj_favorites/artist/dj_id=255
# http://0.0.0.0:5000/dj_favorites/track/dj_id=255 */

Also, dropped support for air_name. Could be added back later as a nice-to-have.

***2. Get Most Plays by dj_id or air_name:***

Find out what artists/albums/songs a DJ plays the most.

* **URL**

   * ` /dj_favorites/<integer> `
   * ` /dj_favorites/<string> `

* **Method:**
  
  < `GET` >
  
*  **URL Params**

dj_ids go up to ~450. air_names are case-sensitive (for now) and URLs require exempting spaces with '%20'

   **Required:**
 
   `dj_id=[integer]`<br>
   OR<br>
   `air_name=[string]`<br>

* **Success Response:**

  * **Code:** 200 <br />
    **Content:**
    ```
    [
        {
            "artist": "Bob Marley & the Wailers",
            "plays": 1244
        },
        {
            "artist": "Sun Ra",
            "plays": 944
        },
        {
            "artist": "Burning Spear",
            "plays": 780
        },
        {
            "artist": "bob marley & the wailers",
            "plays": 724
        }, ... 
    ]
 
* **Error Response:**

  TODO

* **Sample Call:**

  * `curl -v http://0.0.0.0:5000/dj_favorites/177`<br>
  * `curl -v http://0.0.0.0:5000/dj_favorites/Robert%20Emmett`<br>


* **Error Response:**

  TODO


* **Notes:**

  If DJ Spliff Skankin's top play is not "Bob Marley & the Wailers",
  this program is **broken**.

<br><br><br>

***3. Get Last Plays by Artist, Album or Track:***

Find out when an artist/album/track was last played.

* **URL**

   * ` /last_played/artist=<string> `
   * ` /last_played/album=<string> `
   * ` /last_played/track=<string> `

* **Method:**
  
  < `GET` >
  
*  **URL Params**

    Params are not case-sensitive and will do a wild card search.
    URLs require exempting spaces with '%20'.

   **Required:**
 
   `artist=[string]`<br>
   OR<br>
   `album=[string]`<br>
   OR<br>
   `track=[string]`<br>


* **Success Response:**

  * **Code:** 200 <br />
    **Content:**
    ```
    [
        {
            "air_name": "Howard Beale",
            "artist": "Pink Floyd",
            "album_title": "Ummergummer",
            "track_title": "C.W.T.A.E.",
            "time_played": "1995-10-09T22:00:00"
        },
        {
            "air_name": "Phillip Morris",
            "artist": "Pink Floyd",
            "album_title": "Meddle",
            "track_title": "Fearless",
            "time_played": "1995-10-11T02:00:00"
        },...
    ]
 
* **Error Response:**

  TODO

* **Sample Call:**

  * `curl -v http://0.0.0.0:5000/last_played/artist=Pink%20Floyd`<br>
  * `curl -v http://0.0.0.0:5000/last_played/album=Dark%20Side%20of%20the%20Moon`<br>
  * `curl -v http://0.0.0.0:5000/last_played/track=eclipse`<br>

<br><br><br>

***4. Get Top Plays by Artist, Album or Track:***

Create your own 'KFJC Top 40' for any time frame.

* **URL**

   * ` /top_plays/top=<integer>&order_by=<string>&start_date=<date>&end_date=<date> `

* **Method:**
  
  < `GET` >
  
*  **URL Params**

   **Required:**
 
   * `top=[integer]` 10 for Top Ten, 40 for Top Forty...
   * `order_by=[string]` ['artist', 'artists', 'album', 'albums', 'track', 'tracks']
   * `start_date=[date]`
   * `end_date=[date]`

* **Success Response:**

  * **Code:** 200 <br />
    **Content:**
    ```
    [
        {
            "artist": "Satoko Fujii /Fonda Joe",
            "album_title": "Mizu",
            "plays": 6,
            "track_title": "Mizu"
        },
        {
            "artist": "Negativland",
            "album_title": "True False",
            "plays": 5,
            "track_title": "Destroying Anything"
        },...
    ]
 
* **Error Response:**

  TODO

* **Sample Call:**

  * `curl -v http://0.0.0.0:5000/top_plays/top=5&order_by=artist&start_date=2020-01-02&end_date=2020-01-10`<br>
  * `curl -v http://0.0.0.0:5000/top_plays/top=10&order_by=album&start_date=2020-01-02&end_date=2020-01-10`<br>
  * `curl -v http://0.0.0.0:5000/top_plays/top=40&order_by=track&start_date=2020-01-02&end_date=2020-01-10`<br>
  
<br><br><br>

***5. DJ Statistics:***

Get info about all DJs ranked alphabetically, by dj_id, by last appearance on the air, by first appearance on the air, and total shows.

* **URL**

   * ` /top_plays/top=<integer>&order_by=<string>&start_date=<date>&end_date=<date>order_by=air_name&reverse=1 `

* **Method:**
  
  < `GET` >
  
*  **URL Params**

   **Required:**
 
   * `order_by=[string]` [air_name, dj_id, showcount, firstshow, lastshow]
   * `reverse=[integer]` [0, 1]

* **Success Response:**

  * **Code:** 200 <br />
    **Content:**
    ```
        [
            {
                "air_name": "abacus finch", 
                "dj_id": 281, 
                "firstshow": "2011-06-01T02:06:14", 
                "lastshow": "2021-05-07T06:00:53", 
                "showcount": 355
            }, 
            {
                "air_name": "Abaza", 
                "dj_id": 364, 
                "firstshow": "2016-04-08T16:17:01", 
                "lastshow": "2019-02-11T02:00:13", 
                "showcount": 15
            }, ... 
        ]
 
* **Error Response:**

  TODO

* **Sample Call:**

  * `curl -v http://0.0.0.0:5000/dj_stats`<br>
  * `curl -v http://0.0.0.0:5000/dj_stats/order_by=air_name&reverse=1`<br>
  * `curl -v http://0.0.0.0:5000/dj_stats/order_by=air_name&reverse=0`<br>
  * `curl -v http://0.0.0.0:5000/dj_stats/order_by=dj_id&reverse=1`<br>
  * `curl -v http://0.0.0.0:5000/dj_stats/order_by=showcount&reverse=0`<br>
  * `curl -v http://0.0.0.0:5000/dj_stats/order_by=firstshow&reverse=0`<br>
  * `curl -v http://0.0.0.0:5000/dj_stats/order_by=lastshow&reverse=0`<br>
  
* **Notes:**
    * The DJs with the top shows are Robert Emmett and Spliff Skankin'.
    * To become a DJ, you need to take a class, complete a training excercise and 13 Grave Shifts. For that reason, a minimum of 14 playlist entries are required to be recognized as a KFJC DJ.

<br><br><br>

***6. Get Tracks on an Album:***

Show tracks on an album in the KFJC Library.

* **URL**

   * ` /album_tracks/<kfjc_album_id> `

* **Method:**
  
  < `GET` >
  
*  **URL Params**

    There are 868,000 albums in the KFJC Library.

   **Required:**

   `kfjc_album_id=[integer]`

* **Success Response:**

  * **Code:** 200 <br />
    **Content:**
    ```
    [
        {
            "artist": "Pink Floyd",
            "indx": 0,
            "title": "Speak to Me"
        },
        {
            "artist": "Pink Floyd",
            "indx": 0,
            "title": "Breathe"
        }, ...
    ]
 
* **Error Response:**

  TODO

* **Sample Call:**

  * `curl -v http://0.0.0.0:5000/album_tracks/497606`<br>
  

  TODO: Added Albums by an Artist:
# http://0.0.0.0:5000/artists_albums/artist=Pink%20Floyd
# http://0.0.0.0:5000/artists_albums/artist=Lee%20Press%20On
# http://0.0.0.0:5000/artists_albums/artist=Adam%20Ant