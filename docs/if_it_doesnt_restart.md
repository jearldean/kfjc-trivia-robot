**How to push code changes to Production.**
----
According the the instructions on :
https://fellowship.hackbrightacademy.com/materials/serpt5/lectures/aws/
<br>
The secret is in the aws.pem file, not in this document.

1. go to https://lightsail.aws.amazon.com/ls/webapp/home/instances?# and reboot your server.

Try again after a few moments: http://jearldean.com

2. go to https://lightsail.aws.amazon.com/ls/webapp/home/instances?# and stop and restart your server.

Try again after a few moments: http://jearldean.com

3. If your server still isn't starting:
    * Connect again: `ssh -i ~/.ssh/aws.pem ubuntu@44.227.66.155`
    * Tail the log: `tail -f ~/kfjc-trivia-robot/flask.log`
    * Find out why it can't start up. Fix it. Push to git again. Git pull. And try starting it up again.
    * Try again after a few moments: http://jearldean.com

4. Other Tricks and Traps:
    * Don't forget to restart your venv: `source venv/bin/activate`
    * And deploy your secret: `source secret.sh`
    * Maybe upgrade pip: `/home/ubuntu/kfjc-trivia-robot/venv/bin/python -m pip install --upgrade pip`
    * Maybe install requirements afresh: `pip3 install -r requirements.txt`