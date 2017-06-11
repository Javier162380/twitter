
#python libraries we are going to use.

from requests import get
from requests_oauthlib import OAuth1
from sys import exit
from time import sleep
from pandas import DataFrame
from pandas.io import gbq
from bigquery import get_client
from datetime import time
from time import time

def main():
	### WE INSERT PARAMETERS ###
	
	#twitter credentials
	API_KEY=sys.argv[1]
	API_SECRET=sys.argv[2]
	API_TOKEN=sys.argv[3]
	API_TOKEN_SECRET=sys.argv[4]
	
	#results we want to retrieve the information
	RESULTS=sys.argv[5]
	
	#gbq credentials
	service_account=sys.argv[6]
	json_key_file=sys.argv[7]
	
	#table and project where we wanna insert all the data.
	#this script use a partition table to insert the data. 
	#we don t need to specify a schema previously because we are going to use dataframe to insert the data.
	project_id=sys.argv[8]
	table=sys.argv[9]
	
	#we insert the oath credentials
	auth=OAuth1(API_KEY,API_SECRET,API_TOKEN,API_TOKEN_SECRET)
	
	#verify credentials.
	credentials=get('https://api.twitter.com/1.1/account/verify_credentials.json', auth=auth)
	if str(credentials)!='<Response [200]>':
		print('Los Credenciales no son las adecuados')
		exit()
	else: 
		pass
	
	#extract data	
	search=get('https://api.twitter.com/1.1/search/tweets.json?q='+RESULTS+'&count=100', auth=auth)
	if str(credentials)!='<Response [200]>':
		print('La busqueda no encontro ningun resultado')
		exit()
	else: 
		pass
	
	data=[]
	results=search.json()
	if 'search_metadata' not in results:
		print('Se ha producido algun error {results}'.format(str(results)))
		exit()
	else:
		if 'next_results' not in results['search_metadata']:
			data=results['statuses']
		else:
			next_url=results['search_metadata']['next_results']
			data=results['statuses']
			while True:
				sleep(5)
				search=get('https://api.twitter.com/1.1/search/tweets.json'+str(next_url), auth=auth)
				results=search.json()
				if 'next_results' in results['search_metadata']:
					next_url=results['search_metadata']['next_results']
					data=data+results['statuses']
				else:
					break
	
	#create a DataFrame from a list of dict.
	dataframe=DataFrame.from_records(data)
	
	#authorize bigquery client
	client = get_client(project_id, service_account=service_account,json_key_file=json , readonly=False, swallow_results=False)
	
	#we create a partition in our gbq table for the value date of the inserction .
	today=time()
	partition=datetime.fromtimestamp(today).strftime('%Y%m%d')
	table=table+'$'+str(partition)
	
	#insert into gbq
	try:
		io.gbq.to_gbq(dataframe=data,destination_table=table,project_id=project_id,chunksize=5000,reauth=False,if_exists='append')
	except Exception as e:
		print('Durante la inserción en gbq se ha producido el siguiente error  {e}'.format(e))

if __name__ == '__main__':
	main()