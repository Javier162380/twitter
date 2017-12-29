# twitter
This repository aims to capture and clean data from the twitter API in order to perform a sentiment analysis on an EMR cluster.
To achieve this result, first we create an twitter class to perform some useful methods with the twitter api, in this case we are 
going to use the streaming api and store the results in AmazonS3(search.py it is just an example).
we are going to use MRjob python library to perform the mapreduce job, and EMR to perform the analysis.
