from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import json
ACCESS_KEY = "AKIASSU25CC7XDFGOM47"
SECRET_ACCESS_KEY = "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"
credentials = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_ACCESS_KEY).get_credentials()

region = 'us-east-1'
service = 'es'
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'search-restaurants-iaj2jyd6dd5ucckfib7fw7jdaq.us-east-1.es.amazonaws.com'

print(awsauth)

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

#
# document = {
#     "title": "Moneyball",
#     "director": "Bennett Miller",
#     "year": "2011"
# }

data = {}
with open("/Users/admin/Desktop/assignment_1/export.json", "r") as data_file:
    data = json.load(data_file)

i = 1
#biz=data["businesses"]

#for biz in data["businesses"]:
for element in data["Items"]:
    cuisine= "cuisine is not provided by Yelp." if "cuisine" not in element else element["cuisine"]["S"]
    
#    print("element_1:",element["cuisine"])
#    print("element_2:", element["cuisine"]["S"])
    
    item = {
        "id": element["id"]["S"],
        "cuisine": cuisine
    }
    
    es.index(index="restaurants", doc_type="Restaurant", id=i, body=item)
    i += 1

    #print(es.get(index="restaurants", doc_type="Restaurant", id="5"))
    #print(es.search(q='chinese'))
# print(es.get(index="restaurants", doc_type="Restaurant", id="1"))
