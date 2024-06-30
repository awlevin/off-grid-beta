# Off Grid Beta

This is a WIP app. The intent is to allow users to send SMS messages over satellite, when they lack regular cell service, and receive important updates (weather, fire risk, traffic, etc.) without using data.


## Setup

This is a typical Python/Flask application.

### Setup virtual env

```sh
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

#### Python dependencies:

```sh
pip install -r requirements.txt
```

#### Ngrok

You'll need this during development if you want to handle received text messages from Twilio instead of using mocked data/API calls. You can [download ngrok here](https://ngrok.com/download).

### Launch Server

```sh
python app.py
```

You can use Ngrok to expose your local server to Twilio and handle actual webhook events triggered by text messages. Make sure your Flask server is running, and run `ngrok http 5000`.

### Deactivate virtual env

```sh
deactivate
```
