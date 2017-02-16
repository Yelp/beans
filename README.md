# Beans

Beans is an internal networking tool to help employees connect with each other at work. Every week Beans helps match and schedule a short 30-minute 1:1 meeting for two employees at the office.

## System Dependencies
* [Node.js](https://nodejs.org/en/)
* [Python2.7](https://www.python.org/downloads/)
* [Google Cloud SDK](https://cloud.google.com/sdk/docs)
* [Python Component](https://cloud.google.com/sdk/docs/managing-components) `gcloud components install app-engine-python`
* [GoogleAppEngineLauncher](https://cloud.google.com/appengine/docs/python/download) scroll and click `Or, you can download the original App Engine SDK for Python.`

## Tech
=======
* [Google App-Engine](https://cloud.google.com/appengine/)
* [Python2.7](https://www.python.org/download/releases/2.7/)
* [Flask](http://flask.pocoo.org/)
* [Google API for emails](https://developers.google.com/gmail/api/)
* [Ndb data store](https://cloud.google.com/appengine/docs/python/ndb/)
* [S3 integration](https://aws.amazon.com/s3/)
* [Blossom algorithm](https://en.wikipedia.org/wiki/Blossom_algorithm)


## App Setup

 1. Head over to [SDK Download](https://cloud.google.com/sdk/docs/)
 2. Complete the optional steps 4
 3. For step 6 run `gcloud components install app-engine-python`
 3. Navigate to yelp-beans source
 4. make development
 5. source venv/bin/activate
   * Using fish? `. venv/bin/activate.fish`
 6. make test
   * No such file "client_secrets.json"? Feel free to create it. You will need
     to add keys for AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
     SENDGRID_API_KEY, and SENDGRID_SENDER
 7. make serve

## Google Appengine Setup
 1. add datastore secrets: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
