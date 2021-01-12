  
from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
from datetime import *

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('yelp-restaurants')

with open("Chinese.json", 'r') as json_file:
    data = json.load(json_file, parse_float = decimal.Decimal)
    #print(type(data["businesses"]))
    for biz in data["businesses"]:
        #print(len(biz))
        for restaurant in biz:
            #print(restaurant)
            #print("\n")
            ID = restaurant["id"]
            name = restaurant["name"]
            # #         price = restaurant["price"]
            coord = "coordinates are not available" if "coordinates" not in restaurant else restaurant["coordinates"]
            location = "location is not available" if "location" not in restaurant else restaurant["location"]
            rating = "ratings are not available" if "categories" not in restaurant else restaurant["rating"]
            zip = "zip_codes are not available" if "categories" not in restaurant else restaurant["location"]["zip_code"]
            num_review = "review_count are not available" if "categories" not in restaurant else restaurant["review_count"]

            cuisine = "cuisine" if "cuisine" not in restaurant else restaurant["cuisine"]
            # ID = "id" if "id" not in restaurant else restaurant["id"]
            # name = "restaurant" if "name" not in restaurant else restaurant["name"]
            # price = "$" if "price" not in restaurant else restaurant["price"]
            # rating = 3 if "rating" not in restaurant else restaurant["rating"] 
            # review_count = 0 if "review_count" not in restaurant else restaurant["review_count"]
            # location = "location is not provided by Yelp." if "location" not in restaurant else restaurant["location"]
            # time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # table.put_item(
            # Item = {
            #     'cuisine': "Mexican",
            #     'id': ID,
            #     'rating': rating,
            #     'name': name,
            #     'zip_code': zip,
            #     'coordinates': coord,
            #     'address': location,
            #     #'categories': cate,
            #     'review_count':num_review,
            #     'insertedAtTimestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # }
            # )

            Item = {
                'cuisine': cuisine,
                'id': ID,
                #'name': name,
                #'price': price,
                #'rating': rating,
                #'reviewCount': review_count,
                #'location': location,
                #'insertedAtTimestamp': time
            }       
        print(Item)
            
            
            
            
            
            
            
            
            
            
#print(data)
