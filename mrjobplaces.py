import json
from mrjob.job import MRJob
from mrjob.step import MRStep
import diccionaries as dic
import states

class MRJOB(MRJob):
    """We are going to perform just some Map Reduce methods. MRJOB"""
    MRJob.SORT_VALUES = True

    @staticmethod
    def filter_decode_tweets(line):
        try:
            tweet_object = json.loads(line, encoding='utf-32')
            return tweet_object
        except ValueError:
            return None

    @staticmethod
    def point_in_polygon(x, y, poly):
        n = len(poly)
        inside = False
        p1x,p1y = poly[0]
        for i in range(n+1):
            p2x,p2y = poly[i % n]
            if y > min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x,p1y = p2x,p2y
        return inside

    def mapper_english(self, _, line):
        tweet_object = MRJOB.filter_decode_tweets(line)
        if tweet_object is not None and 'text' in tweet_object:
            #we are just going to analyze english tweets perform in the USA.
            if 'lang' in tweet_object and tweet_object['lang'] == 'en':
                tweet_value=0
                for word in tweet_object['text'].split():
                    #we get the value of each word.
                    value = dic.word_dict_english.get(word.upper(), 0)
                    tweet_value += value
                    #we are going to analyze the influence of elclasico in the USA states.
                if tweet_value !=0 and tweet_object['place'] is not None:
                    if tweet_object['place']['country_code'] == 'US':
                        try:
                            state=tweet_object['place']['full_name'].split(', ')[1]
                            yield (state, tweet_value)
                        except:
                            pass
                    else:
                        pass
                elif tweet_value !=0 and tweet_object['geo'] is not None:
                    if len(tweet_object['geo']['coordinates'])==2 and tweet_object['geo']['type']=='Point':
                        for state, polygon in states.statePolygons.items():
                            x = tweet_object['geo']['coordinates'][0]
                            y = tweet_object['geo']['coordinates'][1]
                            if (point_in_polygon(x, y, polygon)) == True:
                                yield (state,tweet_value)

                elif tweet_value != 0 and tweet_object['user']['location'] is not None:
                    for full_name in states.stateNames.keys():
                        if tweet_object['user']['location'].upper().find(full_name.upper()) != -1:
                            state=states.stateNames[full_name]
                            yield (state,tweet_value)
                else:
                    pass

    def combiner(self, key, value):
        yield (key, sum(value))

    def reducer(self, key, value):
        yield (sum(value), key)

    #def reducer_find_max_word(self, _, word_count_pairs):
    #    #this function will return the state where theclasico was best value.
    #    yield max(word_count_pairs)
    def steps(self):
        return [
            MRStep(mapper=self.mapper_english,
                   combiner=self.combiner,
                   reducer=self.reducer)
            #MRStep(reducer=self.reducer_find_max_word)
        ]


if __name__ == '__main__':
    MRJOB.run()