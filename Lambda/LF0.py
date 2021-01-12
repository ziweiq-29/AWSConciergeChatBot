import json
from datetime import *
import boto3
import os

def lambda_handler(event, context):
    #send client request to lex chatbot
    client = boto3.client('lex-runtime')
    
    # print("check json ", json.dumps(event))
     
#      {
#     "messages": [
#         {
#             "type": "unstructured",
#             "unstructured": {
#                 "text": "hello"
#             }
#         }
#     ]
# }
    
    # str1 = event['messages']
    # print("str1:", str1)
    
    # str2 = event['messages'][0]
    # print("str2:", str2)
    
    str3 = event['messages'][0]['unstructured']
    #print("str3:", str3)
    
    str4 = event['messages'][0]['unstructured']['text']
    #print("str4:", str4)
   

    #check below link to learn botName, botAlias, and userId
    #https://docs.aws.amazon.com/lex/latest/dg/API_runtime_PostText.html
    #to access lex chatbot, add permission to lambda's IAM role
    #Permissions -> Role name -> Attach Policies -> AmazonLexFullAccess
    response = client.post_text(
        botName ='DiningConciergeChatbot',
        botAlias ='chatbot',
        userId = 'Changhanxie',
        
        # sessionAttributes={
        #     'string': 'string'
        # },
        # requestAttributes={
        #     'string': 'string'
        # },
        
        inputText = str4
    )
    
    reply = response["message"]

    response = {"type": "unstructured",
                "unstructured": {
                'id': context.aws_request_id, 
                'text': reply,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
    
    return {
        'statusCode': 200,
        'headers': { 
            "Access-Control-Allow-Origin": "*" 
        },
        'messages': [response]
    }
    