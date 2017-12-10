import requests
from requests_oauthlib import OAuth1
from os import path, makedirs
import json
from time import sleep


class twitter(object):
    """Perform some useful methods from the twitter api"""

    def __init__(self, api_key, api_secret, api_token, api_token_secret):
        """we need this four arguments to create an instance"""
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
        """This method it´s just perform to test our API connection"""
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
            raise "El formato escogido no esta soportado en esta clase."
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

    def streamingapi(self,query, filename):

        file = open(str(filename), 'w')
        count = 1
        req = self.session.post('https://stream.twitter.com/1.1/statuses/filter.json?track='+str(query))
                                , auth=self.connection, stream=True)
        try:
            if req.status_code == 420:
                sleep(60 * count)
                count += 1
            elif req.status_code == 200:
                for line in req.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        file.write(str(json.loads(decoded_line)))
        finally:
            file.close()
