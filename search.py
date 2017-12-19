from twitter import twitter
from sys import argv

api_key=argv[1]
api_secret=argv[2]
api_token=argv[3]
api_token_secret=argv[4]

twitter = twitter(api_key,api_secret,api_token,api_token_secret)
#we are going to retrieve data about #ElClasico.
twitter.streamingapi(['#ELclasico','#ElClasico','#ElClásico','#elclasico'], 'football','twitterjavierllorente'
                     ,1,
                     ['in_reply_to_status_id_str','favorite_count','in_reply_to_user_id_str','in_reply_to_status_id',
                      'possibly_sensitive','in_reply_to_user_id','timestamp_ms',
                      'is_quote_status','filter_level','favorited','quote_count','id_str','in_reply_to_screen_name',
                      'source'])
