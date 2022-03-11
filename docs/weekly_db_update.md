**How to update the Database with the new weekly data.**
----
According the the instructions on :
https://fellowship.hackbrightacademy.com/materials/serpt5/lectures/aws/
<br>

***1. Get the Fresh Data Drop***

  * Wednesday nights around 10, Ken downloads the MySQL station database, Spidey.
  * I make 6 csv files from these tables:
    * album
    * coll_track
    * playlist
    * playlist_track
    * track
    * user
    
  * Archive off old files and put the new ones in the station_data folder.

***2. Wipe and Update Tables Locally***
    
  `python3 seed_database.py`
    
  This deletes old tables and imports new data:
    
  `>>> nuclear_option()`
    
  Go to bed. Takes 4.5 hours.

***3. Check the Imported Data***

  * Did it finish? Or did it stall? Where did it stall? Fix it and go back to Step 2.

  * Look over the tables.

    * Are all columns populated?

    * Do they look right?

    * Is the Profanity Filter Working?

  * Look over the questions.

    * Delete any questions where the answer doesn't make sense: "a", "___", 7, Side 1, nonsense strings...

    * Check answer pile. Is the correct answer the first item?

  * Look for evidence of things you fixed in the imported data. 

***4. Synchronize the Users and Answers Tables***

  Your local database just went through a wipe and import. Therefore, the Users and Answers Tables should be empty.

  Your server database contains PRODUCTION user accounts, hashed passwords, question responses that will be needed to compute Leaderboard and Scores.

  Here are the things I do and check:

    1. Copy all the remote users rows to your empty local users table.

    2. Copy all the remote answers rows to your empty local answers table.

    3. Wipe out the question_id for all answers and make it 1.

      * This means that returning users will never be offered question 1. A small price to pay, as seed_database creates hundreds of new, unique questions.

      * We need to do this or else, each users will be 'not offered' some different random question_id in the questions table. More numbers blocked off for more prolific players. Not fair!


***5. Dump Your Local Database to a .sql File***

  Send either of these commands from whichever folder is convenient:

  * laptop $ ` pg_dump --clean --no-owner trivia > ~/src/trivia.sql `

      OR

  * (venv) $ ` pg_dump --clean --no-owner trivia > ./trivia.sql `

***6. Upload and Install the Updated Database***

  The secret is in the aws.pem file, not in this document.

  * laptop $ `scp -i ~/.ssh/aws.pem /Users/jem/hb-dev/src/kfjc-trivia-robot/trivia.sql ubuntu@44.227.66.155:/tmp/`

  * laptop $ `ssh -i ~/.ssh/aws.pem ubuntu@44.227.66.155`

  * ubuntu@aws:~$ `cd kfjc-trivia-robot`

  * ubuntu@aws:~/kfjc-trivia-robot$ `git pull`

  * ubuntu@aws:~/kfjc-trivia-robot$ `sudo systemctl stop flask`

    * (Quit Local DataGrip App.)

  * ubuntu@aws:~/kfjc-trivia-robot$ `dropdb trivia`

  * ubuntu@aws:~/kfjc-trivia-robot$ `createdb trivia`

  * ubuntu@aws:~/kfjc-trivia-robot$ `psql trivia < /tmp/trivia.sql`

  * ubuntu@aws:~/kfjc-trivia-robot$ `sudo systemctl daemon-reload`

  * ubuntu@aws:~/kfjc-trivia-robot$ `sudo systemctl restart flask`

***7. Test the Server***

    http://jearldean.com

  * Make sure your original login works.

  * Try answering questions

  * Try asking things.