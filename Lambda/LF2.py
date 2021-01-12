
from __future__ import print_function

import os
import json
import boto3
import urllib3
import requests
from botocore.exceptions import ClientError
import random
import logging
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
#from aws_requests_auth.aws_auth import AWSRequestsAuth


ES_HOST = 'https://search-restaurants-iaj2jyd6dd5ucckfib7fw7jdaq.us-east-1.es.amazonaws.com'
ES_INDEX = 'restaurants'
ES_TYPE = 'Restaurant'
ACCESS_KEY = 'AKIASSU25CC7SZYF63H3'
SECRET_ACCESS_KEY = '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'
REGION = 'us-east-1'
host = 'search-restaurants-iaj2jyd6dd5ucckfib7fw7jdaq.us-east-1.es.amazonaws.com'
URL = ES_HOST + '/' + ES_INDEX + '/' + ES_TYPE + '/_search'
SQS_URL = 'https://sqs.us-east-1.amazonaws.com/177492267199/DiningConciergeChatbotQueue'
SENDER = 'zq2047@nyu.edu'

### --- Establish connection to ES --- ### 

credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, REGION, 'es', session_token=credentials.token)

###  --- Get random restaurant recommendations --- ### 

logger = logging.getLogger()





def search_dynamodb(restaurants, req):
    dynamodb = boto3.client('dynamodb')
    
    cuisine = req["cuisine"].lower()
    rest_dic = {}
    name_list = []
    
    for item in restaurants:
        rest_id = item["_source"]["id"]
        rest_name = item["_source"]["cuisine"]
        
        #print(rest_id)
        #print(rest_name)
        
        response = dynamodb.get_item(
            TableName='yelp-restaurants',
            Key={
                
                # 'cuisine': {'S': "Indian"},
                # 'id': {'S': "0SqFgkdmfNWj9iUQgfghEA"}
                
                'cuisine': {'S': cuisine},
                'id': {'S': rest_id}
            }
        )
        #print("response11: ",response)
        #print("RESPONSE: {}".format(json.dumps(response)))

        address1=response["Item"]["address"]["M"]["address1"]["S"]
        rest_name1=response["Item"]["name"]["S"]
        if rest_name1 not in rest_dic:
            rest_dic[rest_name1] = address1
        
        
    number_people = req["number_people"]
    dining_date = req["dining_date"]
    dining_time = req["dining_time"]
    location = req["location"]
    
    for name in rest_dic:
        name_list.append(name)
    
    
    print("REST_DICT --- {}".format(rest_dic))
    print("NAME_LIST --- {}".format(name_list))
    
    reservation = 'Hello! Here are my {} restaurant suggestions for {} people, on {}, {} at {}: 1. {} located at {} 2. {} located at {} 3. {} located at {}. Enjoy your meal!'.format(cuisine, number_people, dining_date, dining_time, location, name_list[0], rest_dic[name_list[0]], name_list[1], rest_dic[name_list[1]], name_list[2], rest_dic[name_list[2]])
    
    return reservation

def get_url(es_index, es_type, cuisine):
    url = ES_HOST + '/' + es_index + '/' + es_type + '/_search'
    search_url = url + '?q=' + cuisine
    return search_url

def lambda_handler(event, context):
    sqs = boto3.client('sqs')
    receipt_handle = event["Records"][0]["receiptHandle"]

    # pulls a message from the SQS
    for record in event["Records"]:
        # req = record["body"]
        req = json.loads(record["body"])

    #print("REQ -- {}".format(json.dumps(req)))
    print("REQ --",json.dumps(req))
   
    # make the HTTP request
    
    cuisine = req["cuisine"].lower()
    
    es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)
    
    r_data = es.search(q=req["cuisine"].lower())
    #print("row data ",r_data)
    
    all_restaurants = r_data["hits"]["hits"] # list type

    # get Machine Learning recommendation from ElasticSearch
    if len(all_restaurants) < 3:
        r_data = es.search(q=req["cuisine"].lower())
        all_restaurants = r_data["hits"]["hits"] # list type

        # get randome restaurant recommendation from ElasticSearch
        restaurants = random.sample(all_restaurants, 3) # list type, [{}, {}, {}]
        # fetch more information form DynamoDB
        reservation = search_dynamodb(restaurants, req)

    else:
        restaurants = random.sample(all_restaurants, 3) # list type, [{}, {}, {}]
        #print("random restaurant: ", restaurants)
        reservation = search_dynamodb(restaurants, req)

    
    email = str(req["email"])

    # send SES message
    ses = boto3.client('ses', region_name=REGION)

    #print("EMAIL ADDRESS: {}".format(email))

    message = ses.send_email(
        Source=SENDER,
        Destination={
            'ToAddresses': [email]
        },
        Message={
            'Body': {
                'Text': {
                    'Data': reservation
                }
            },
            'Subject': {
                'Data': 'Restaurant Suggestions from Chatbot'
            }
        }
    )
    
    print("MESSAGE to email {}".format(message))
    
    
    # send SMS message
    sns = boto3.client('sns')
    
    phone = req['phone']
    
    response = sns.publish(
      PhoneNumber= phone,
      Message=reservation
      )
        

    # delete the finished request from SQS 
    
    sqs.delete_message(
        QueueUrl=SQS_URL,
        ReceiptHandle=receipt_handle
    )
    print("SUCCESSFULLY DETELE THE FINISHED MESSAGE FROM SQS")

    return {
        'statusCode': 200,
        'headers': { 
            "Access-Control-Allow-Origin": "*" 
        },
        'body': json.dumps(reservation)
    }