from praw import Reddit

games = {}

with open("tokens/token_test.0", 'r') as f:
    test_token = f.read()

with open("tokens/token_test.0", 'r') as f:
    token = f.read()

with open("tokens/reddit_secret.0",'r') as f:
    reddit = Reddit(client_id="Ff908EpHV9mgag",
                 client_secret=f.read(),
                 user_agent='C-3PO Discord Bot')