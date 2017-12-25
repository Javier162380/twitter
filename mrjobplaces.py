import json
from mrjobplaces.job import MRJob
from mrjobplaces.step import MRStep
import logging
import diccionaries as dic
import gmaps

class MRJOB(MRJob):
    """We are going to perform just some Map Reduce methods. MRJOB"""
    MRJob.SORT_VALUES = True

    @staticmethod
    def _filter_decode_tweets(line):
        try:
            tweet_object = json.loads(line, encoding='utf-8')
            return tweet_object
        except ValueError:
            logging.warning('JSON object bad format')
            return None

    def mapper_english(self, _, line):
        tweet_object = MRJOB._filter_decode_tweets(line)
        if tweet_object is not None and 'text' in tweet_object:
            #we are just going to analyze english tweets.
            if 'lang' in tweet_object and tweet_object['lang'] == 'en':
                tweet_value=0
                for word in tweet_object['text'].split():
                    #we get the value of each word.
                    value = dic.word_dict_english.get(word.upper(), 0)
                    tweet_value += value
                if tweet_value !=0 and tweet_object['place'] is not None:
                    country=tweet_object['place']['country']
                    yield (country, tweet_value)
                elif tweet_value !=0 and tweet_object['user']['location'] is not None:
                    try:
                        country=tweet_object['user']['location']
                        yield (country, tweet_value)
                    except:
                        pass
                else:
                    pass

    def combiner(self, key, value):
        yield (key, sum(value))

    def reducer(self, key, value):
        yield (sum(value), key)

    def steps(self):
        return [
            MRStep(mapper=self.mapper_english,
                   combiner=self.combiner,
                   reducer=self.reducer)
        ]


if __name__ == '__main__':
    MRJOB.run()






