**The KFJC Trivia Robot**
----
<br>


***How to play***

* **Make an account**

  * Put in a username, first name and secret password.
  * The username is a unique name within the system.
  * Your password is encrypted and stored. 

* **Answer Questions**

  * There are 16 types of questions over 26 years of radio station data.
  * The quiz isn't meant for anyone to get 100%.

    It's just a way to know more about your favorite DJs, discover new music or just read some funny DJ and track names.


* **Check your Score**
  * The My Score button in the footer will show you your passes, fails, skips, total questions and percent correct.

* **Check the Leaderboard**
  * It's like checking all the scores.

* **Ask the Robot!**
  * Unlike other quizzes, the answers here are not a secret. It's just a game for fun. So, if you want to search the library or find the history of your favorite DJ or design your own Top40 between any 2 dates, check out the Ask link in the footer.
  * Why do some DJs have ♡ hearts ♡ around their names? The silent_mic boolean allows us to honoring those DJs who have departed this mortal plane.


***How to use***

Here's how to install the robot from scratch.

* **First, get a radio station.**
  Let's pretend there's another radio station out there with a SQL database matching KFJC's schema. This describes we could install a new working instance based on their data set.

* **Import their data from CSVs.**
  Create CSVs of the station data:

  |csv file|purpose|
  |---|---|
  |playlist.csv|A playlist is one radio show. A 3-hour effort by a DJ|
  |playlist_track.csv|Each row is one song in one playlist|
  |user.csv|from here we get official DJ Names and silent_mic.|
  |album.csv|album data.|
  |coll_track.csv|track data with an artist field.|
  |track.csv|track data with no artist field.|

  Put them in the station_data folder.


* **Run the Seed Database Program**

  * Could take hours but unless there are major conflicts, it should go straight through.
  * Do it at night while you're asleep.


* **View Data in DataGrip (Optional)**

  * Optional, but here are connection settings to the local data just imported:
    * Host: localhost
    * Port: 5432
    * Authentication: None
    * Database: trivia
    * URL: jdbc:postgresql://localhost:5432/trivia


* **Test it locally**
  * Run it: ` python3 server.py `
  * Hit it: http://0.0.0.0:5000


* **Deploy to your server**
   * I did it on AWS Lightsail but maybe your have your own server.
