from twitter import twitter
from sys import argv

api_key=argv[1]
api_secret=argv[2]
api_token=argv[3]
api_token_secret=argv[4]

twitter = twitter(api_key,api_secret,api_token,api_token_secret)
#we are going to retrieve data about #ElClasico.
twitter.streamingapi(['Elclasico','elclásico','ElClasico','elclasico'], 'elclasico21102017'
                     ,'twitterjavierllorente',0.8)