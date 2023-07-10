# Project Description
In this MAD1 final project I have to create a local hosting web application, Flashcard, can be used for memory training. In this application, a user can create his/her own decks. In each deck, the user can add his/her own double-sided cards. The front side of the card will contain user provided question/word and the backside will contain the answer inserted by the user. For memory training, the user can take a quiz that will show a random user-given card one at a time, and for each selected card user will be awarded particular marks. Also, users can update or delete the cards and the decks.
# Local Setup
- Clone the project
- Run `pip install requirements.txt` in your shell.

# Local Development Run
- If you run `python main.py`or  `python3 main.py` will start the flask app in `development`. Suited for local development

# Replit run
- Go to shell and run
    `pip install --upgrade poetry`
- Click on `main.py` and click button run
- Sample project is at https://replit.com/@thejeshgn/flask-template-app
- The web app will be availabe at https://flask-template-app.thejeshgn.repl.co
- Format https://<replname>.<username>.repl.co

# Folder Structure
- `main.py` is where our application code is
- `static` - default `static` files folder. It serves at '/static' path. More about it is [here](https://flask.palletsprojects.com/en/2.0.x/tutorial/static/).
- `templates` - Default flask templates folder

