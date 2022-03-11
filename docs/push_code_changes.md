**How to push code changes to Production.**
----
According the the instructions on :
https://fellowship.hackbrightacademy.com/materials/serpt5/lectures/aws/
<br>
The secret is in the aws.pem file, not in this document.

* laptop $ `ssh -i ~/.ssh/aws.pem ubuntu@44.227.66.155`

* ubuntu@aws:~$ `cd kfjc-trivia-robot`

* ubuntu@aws:~/kfjc-trivia-robot$ `git pull`

* ubuntu@aws:~/kfjc-trivia-robot$ `pip3 install -r requirements.txt`

* ubuntu@aws:~/kfjc-trivia-robot$ `sudo systemctl restart flask`
