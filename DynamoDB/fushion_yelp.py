import requests
import json
import glob

# Define a business ID
business_id = '4AErMBEoNzbk7Q8g45kKaQ'
unix_time = 1546047836

# Define my API Key, My Endpoint, and My Header
API_KEY = 'TeiHfl8ONXsnLZDYOJroAqrEjHdbYkDj7uddgVcbA43VEfUZGPrIvND__yEtT1I8_0q-MjXqQ_vGAlPO0hufzuZZvHJHIgDjYItGc7kGAiELwSel4yLMW2kKDMyDX3Yx'
#ENDPOINT = 'https://api.yelp.com/v3/businesses/{}/reviews'.format(business_id)
ENDPOINT='https://api.yelp.com/v3/businesses/search'
HEADERS = {'Authorization': 'bearer %s' % API_KEY}

# Define my parameters of the search
# BUSINESS SEARCH PARAMETERS - EXAMPLE
OFFSET=50
final=[]
for i in range(20):

#offset is : (1,2,...)*limit

    PARAMETERS = {'term': 'Mexican',
                  'limit': 50,
                  'offset': 50*i,
                  #'radius': 10000,
                  'location': 'New York'}

    # BUSINESS MATCH PARAMETERS - EXAMPLE
    #PARAMETERS = {'name': 'Peets Coffee & Tea',
    #              'address1': '7845 Highland Village Pl',
    #              'city': 'San Diego',
    #              'state': 'CA',
    #              'country': 'US'}

    # Make a request to the Yelp API
    response = requests.get(url = ENDPOINT,
                            params = PARAMETERS,
                            headers = HEADERS)

    # Conver the JSON String

    business_data = response.json()
    #print(type(business_data))
    final.append(business_data)
    print(len(business_data["businesses"]))
#print(len(business_data.keys()))

#    with open('data.json\_i', 'w') as f:
#        json.dump(business_data, f)
# print the response
dall={}
for i in final:
    #dall.update(i)
    for k, v in i.items():  # d.items() in Python 3+
        dall.setdefault(k, []).append(v)
#print(type(dall["businesses"][0]))


#for i in final:
#    dall.update(i)
#print("final: ",final[0]["businesses"])
#print(type(final[1]))
#print("\n")
#print(dall)


#temp={}
#for i in dall:
#    for j in i:
#        for k,v in j.items():
#            temp.setdefault()
    

d_temp={}
print("len(dall) is: ",len(dall["businesses"]))
#print(type(dall["businesses"][0][0]))



#for biz in dall["businesses"]:
#    #d_temp[""]
#    for item in biz:
#        print(item["id"])
#        print(item["name"])
#        print("\n")
#    print(biz)
#    print("\n")
#print(len(dall.keys()))

#input_dict = json.loads(input_json)
#output_dict = [x for x in input_dict if x['businesses'][] == '']
#d_temp={}
#d_temp["restaurant"]
#for restaurant in dall:
#    d_temp["id"]=dall["id"]
#print(dall["businesses"])

with open('Mexican.json', 'w') as f:
    
    
    json.dump(dall, f)
    #json.dump(d_temp,f)
#print(len(dall["businesses"]))
#print(len(business_data.keys()))
print(len(final))
#print(json.dumps(business_data, indent = 3))







## -*- coding: utf-8 -*-
#"""
#Yelp Fusion API code sample.
#This program demonstrates the capability of the Yelp Fusion API
#by using the Search API to query for businesses by a search term and location,
#and the Business API to query additional information about the top result
#from the search query.
#Please refer to http://www.yelp.com/developers/v3/documentation for the API
#documentation.
#This program requires the Python requests library, which you can install via:
#`pip install -r requirements.txt`.
#Sample usage of the program:
#`python sample.py --term="bars" --location="San Francisco, CA"`
#"""
#from __future__ import print_function
#
#import argparse
#import json
#import pprint
#import requests
#import sys
#import urllib
#
#
## This client code can run on Python 2.x or 3.x.  Your imports can be
## simpler if you only need one of those.
#try:
#    # For Python 3.0 and later
#    from urllib.error import HTTPError
#    from urllib.parse import quote
#    from urllib.parse import urlencode
#except ImportError:
#    # Fall back to Python 2's urllib2 and urllib
#    from urllib2 import HTTPError
#    from urllib import quote
#    from urllib import urlencode
#
#
## Yelp Fusion no longer uses OAuth as of December 7, 2017.
## You no longer need to provide Client ID to fetch Data
## It now uses private keys to authenticate requests (API Key)
## You can find it on
## https://www.yelp.com/developers/v3/manage_app
#API_KEY= 'TeiHfl8ONXsnLZDYOJroAqrEjHdbYkDj7uddgVcbA43VEfUZGPrIvND__yEtT1I8_0q-MjXqQ_vGAlPO0hufzuZZvHJHIgDjYItGc7kGAiELwSel4yLMW2kKDMyDX3Yx'
#
#
## API constants, you shouldn't have to change these.
#API_HOST = 'https://api.yelp.com'
#SEARCH_PATH = '/v3/businesses/search'
##SEARCH_PATH='https://api.yelp.com/v3/businesses/search'
#BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
#
#
## Defaults for our simple example.
#DEFAULT_TERM = 'Chinese'
#DEFAULT_LOCATION = 'New York, NY'
#SEARCH_LIMIT = 50
#
#
#def request(host, path, api_key, url_params=None):
#    """Given your API_KEY, send a GET request to the API.
#    Args:
#        host (str): The domain host of the API.
#        path (str): The path of the API after the domain.
#        API_KEY (str): Your API Key.
#        url_params (dict): An optional set of query parameters in the request.
#    Returns:
#        dict: The JSON response from the request.
#    Raises:
#        HTTPError: An error occurs from the HTTP request.
#    """
#    url_params = url_params or {}
#    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
#    headers = {
#        'Authorization': 'Bearer %s' % api_key,
#    }
#
#    print(u'Querying {0} ...'.format(url))
#
#    response = requests.request('GET', url, headers=headers, params=url_params)
#    business_data=response.json()
#    with open('data.json', 'w') as f:
#        json.dump(business_data, f)
#    return response.json()
#
#
#def search(api_key, term, location):
#    """Query the Search API by a search term and location.
#    Args:
#        term (str): The search term passed to the API.
#        location (str): The search location passed to the API.
#    Returns:
#        dict: The JSON response from the request.
#    """
#
#    url_params = {
#        'term': term.replace('  ', '+'),
#        'location': location.replace(' ', '+'),
#        'limit': SEARCH_LIMIT
#    }
#    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)
#
#
#def get_business(api_key, business_id):
#    """Query the Business API by a business ID.
#    Args:
#        business_id (str): The ID of the business to query.
#    Returns:
#        dict: The JSON response from the request.
#    """
#    business_path = BUSINESS_PATH + business_id
#
#    return request(API_HOST, business_path, api_key)
#
#
#def query_api(term, location):
#    """Queries the API by the input values from the user.
#    Args:
#        term (str): The search term to query.
#        location (str): The location of the business to query.
#    """
#    response = search(API_KEY, term, location)
#
#    businesses = response.get('businesses')
#
#    if not businesses:
#        print(u'No businesses for {0} in {1} found.'.format(term, location))
#        return
#
#    business_id = businesses[0]['id']
#
#    print(u'{0} businesses found, querying business info ' \
#        'for the top result "{1}" ...'.format(
#            len(businesses), business_id))
#    response = get_business(API_KEY, business_id)
#
#    print(u'Result for business "{0}" found:'.format(business_id))
#    pprint.pprint(response, indent=2)
#
#
#def main():
#    parser = argparse.ArgumentParser()
#
#    parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM,
#                        type=str, help='Search term (default: %(default)s)')
#    parser.add_argument('-l', '--location', dest='location',
#                        default=DEFAULT_LOCATION, type=str,
#                        help='Search location (default: %(default)s)')
#
#    input_values = parser.parse_args()
#
#    try:
#        query_api(input_values.term, input_values.location)
#    except HTTPError as error:
#        sys.exit(
#            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
#                error.code,
#                error.url,
#                error.read(),
#            )
#        )
#
#
#if __name__ == '__main__':
#    main()
