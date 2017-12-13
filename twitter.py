import requests
from requests_oauthlib import OAuth1
from os import path, makedirs
import json
from time import sleep
import boto3
from datetime import datetime, timedelta


class twitter(object):
    """Perform some useful methods from the twitter api."""
    def __init__(self, api_key, api_secret, api_token, api_token_secret):
        """we need this four arguments to create an instance."""
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_token = api_token
        self.api_token_secret = api_token_secret
        try:
            self.connection = OAuth1(api_key, api_secret, api_token, api_token_secret)
        except Exception as e:
            raise ValueError("Error al crear una instancia a la api de twitter{0}"
                             .format(e))
        self.session = requests.session()
        self.formats = {'json': '.json', 'txt': '.txt'}

    def vercredentials(self):
        """This method it´s just perform to test our API connection."""
        request = self.session.get('https://api.twitter.com/1.1/account/verify_credentials.json'
                                   , auth=self.connection)
        if request.status_code == 200:
            return "La conexión es correcta"
        else:
            raise ConnectionError("No es posible establecer una conexion http.response {0}"
                                  .format(str(request.status_code)))

    def get_data(self, query, filename, extension, filepath=None):
        """This method it is perform to retrieve data from the twitter api."""
        if self.formats.get(extension, None) is None:
            raise ValueError("El formato escogido no esta soportado en esta clase.")
        else:
            extension = self.formats.get(extension, None)
            if filepath is not None:
                # we create a directory where we are going to save our file.
                if path.exists(filepath) is False:
                    try:
                        absolutepath = path.abspath(makedirs(filepath))
                    except OSError as e:
                        raise OSError("Encontramos el siguiente error al crear el directorio {0}"
                                      .format(str(e)))
                else:
                    absolutepath = path.abspath(filepath)
            else:
                # if the path is None we are going to save the file in the same directory where we run the script.
                absolutepath = path.dirname(path.realpath(__file__))
        # we perform the query.
        search = self.session.get('https://api.twitter.com/1.1/search/tweets.json?q=' + query +
                                  '&count=100', auth=self.connection)
        if search.status_code is not 200:
            raise ConnectionError("No es posible establecer una conexión http.response  {0}"
                                  .format(str(search.status_code)))
        else:
            pass
        # we get all the information.
        results = search.json()
        data = []
        if 'search_metadata' not in results:
            raise ValueError("Problemas al recibir los resultados")
        else:
            data = data + results['statuses']
            if 'next_results' not in results['search_metadata']:
                pass
            else:
                while 'next_results' not in results['search_metadata']:
                    next_url = results['search_metadata']['next_results']
                    search = self.session.get('https://api.twitter.com/1.1/search/tweets.json'
                                              + str(next_url), auth=self.connection)
                    results = search.json()
                    data = data + results['statuses']
        # we write the results into the choose extension.
        with open(str(absolutepath) + '/' + str(filename) + str(extension), 'w') as file:
            if extension is '.json':
                json.dump(data, file)
            elif extension is '.txt':
                file.write(str(data))
        return file

    def streamingapi(self, query, filename, bucket, number_of_days):
        """This method is perform to retrieve data in streaming for twitter. If you want to filter various tweets
        the query statement need to be introduce as a tuple. The results are going to be save in an amazon S3 bucket."""
        #we create the file
        s3file=str(filename)+'.txt'
        file = open(str(filename)+'.txt', 'w')
        #custom parameters to deal with the requests,
        count = 1
        max_sleep = 320
        custom_sleep = 5
        number_of_minutes=round(number_of_days*60)
        end_time = datetime.now() + timedelta(minutes=number_of_minutes)
        #we prepare the txt file.
        if type(query) is tuple:
            filtertweets = ','.join(i for i in query)
            url = 'https://stream.twitter.com/1.1/statuses/filter.json?track='+filtertweets
        elif type(query) is str:
            url = 'https://stream.twitter.com/1.1/statuses/filter.json?track='+query
        else:
            raise ValueError('Formato no adecuado, formato adecuado str o tupla de str.')
        #we initializa the loop.
        while datetime.now() <= end_time:
            try:
                req = self.session.post(url, auth=self.connection, stream=True)
                if req.status_code == 420:
                    sleep(60 * count)
                    count += 1
                elif req.status_code == 200:
                    for line in req.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            file.write(str(json.loads(decoded_line)))
                else:
                    sleep(min(custom_sleep,max_sleep))
                    custom_sleep += 5
            except Exception as e:
                sleep(60)
                self.session = requests.session()
        #we store all the data in S3.
        s3 = boto3.resource('s3')
        try:
            s3.Bucket(bucket).upload_file(s3file, s3file)
            print('Carga realizada con exito el archivo fue subido a S3.')
        except Exception as e:
            raise Exception('Error al subir el fichero a S3. Puedes comprobar el fichero en local.'
                            'Mensaje de Error {0}'.format(e))



