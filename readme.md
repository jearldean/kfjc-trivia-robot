**The KFJC Trivia Robot**
----
<br>
A friendly robot will quiz you about the KFJC's eclectic music library and 26 years of playlist data. But the quiz answers aren't a secret - you can ask the robot questions on the Ask page!

<br>

***How to Play***

* **Make an Account**

  * Put in a username, first name and secret password.
  * Your password is encrypted and stored. 
  * The username is your unique identifier in the system.

* **Answer Questions**

  * There are 16 types of questions over 26 years of radio station data.
  * The quiz isn't meant for anyone to get 100%. It's just a way to
    * know more about your favorite DJs,
    * discover new music,
    * read some funny DJ and track names,
    * or just ponder the vastness of the probeable data set.


* **Check your Score**
  * The My Score button in the footer will show you your passes, fails, skips, total questions and percent correct.

* **Check the Leaderboard**
  * It's like checking the scores for all users, ranked by percent correct.

* **Ask the Robot!**
  * Unlike other quizzes, the answers here are not a secret. It's just a game for fun. So, if you want to search the library or find the history of your favorite DJ or design your own KFJC Top40 between any 2 dates, check out the Ask link in the footer.
  * Why do some DJs have ♡ hearts ♡ around their names?

    The silent_mic boolean allows us to honor those DJs who have served us and departed this mortal plane.

  * Things you can ask:
    * Use the DJ Pulldown to select a DJ. Their first show, last show and show count is displayed. 
    * After you select a DJ, you can use the Artist, Album and Track Radio buttons to view the top played artists, albums and tracks by that DJ.
    * To see the first show, last show and show count rankings for all DJs, select the statistic you want to see and press DJ Stats.
    * Check if some artist, album or track is in the KFJC Library. This wildcard search will even tell you which DJ last played it and the date played.
    * Design your own KFJC Top10 or KFJC Top40 by artist, album or track between any two dates. Keep in mind, there will be no results produced for ranges before September 1995.


***How to Use***

Here's how to install the robot from scratch.

* **First, get a radio station.**

  Let's pretend there's another radio station out there with a SQL database matching KFJC's schema. Schemas provided in
   * /docs/kfjc_trivia_robot_schema.dll.rtf
   * station_data/radio_station_schema.dll
   * Short example csv files in test_data/station_data
  
  This document shall describe how we could install a new working instance based on this new data set.

* **Import Data from CSVs.**

  Create CSVs of the station data:

  |csv file|purpose|
  |---|---|
  |playlist.csv|A playlist is one radio show. A 3-hour effort by a DJ|
  |playlist_track.csv|Each row is one song in one playlist|
  |user.csv|from here we get official DJ Names and silent_mic.|
  |album.csv|album data.|
  |coll_track.csv|track data with an artist field. (Collections)|
  |track.csv|track data with no artist field.|

  Put them in the kfjc-trivia-robot/station_data folder for import.


* **Run the Seed Database Program**

  * Run program:        $ ` python3 -i seed_database.py `
  * Trigger command:     >>> `nuclear_option()`

  * seed_database.py deletes any existing data. That's why just running 
  
    $ ` python3 seed_database.py ` won't do anything.
    We don't want any mistriggers.

  * Could take hours but unless there are major conflicts, it should go straight through. (KFJC's data set spans 26 years. Only playlist_tracks.csv is a REALLY BIG table at 2.5 million rows; one row for each song played since September 1995.)
    * On an old MacBook Pro (2.8 GHz Quad-Core Intel Core i7) it took 4.5 hours
    * On a new M1 MacMini it took 2 hours to import and seed new questions.
  * You could import data at night while you're asleep.


* **View Data in DataGrip (Optional)**

  * There are other SQL Viewer/Editors than Jet Brains' DataGrip.
  * Optional, but here are connection settings to the local data you just imported:
    * Host: localhost
    * Port: 5432
    * Authentication: None
    * Database: trivia
    * URL: jdbc:postgresql://localhost:5432/trivia


* **Test Your Server Locally**
  * Run it: $ ` python3 server.py `
  * Hit it: http://0.0.0.0:5000


* **Deploy to Your Host**
   * I did it on AWS Lightsail but maybe your have your own server.
