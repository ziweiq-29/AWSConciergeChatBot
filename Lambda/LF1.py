"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages reservations for hotel rooms and car rentals.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'BookTrip' template.
For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.

sorce code reference: https://github.com/amazon-archives/serverless-app-examples/blob/master/python/lex-book-trip-python/lambda_function.py
"""
from __future__ import print_function

import json
import datetime
import time
import os
import dateutil.parser
import logging
from botocore.vendored import requests
import sys
import urllib
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode


# Yelp Fusion no longer uses OAuth as of December 7, 2017.
# You no longer need to provide Client ID to fetch Data
# It now uses private keys to authenticate requests (API Key)
# You can find it on
# https://www.yelp.com/developers/v3/manage_app
API_KEY= "PvtaMvHVTDu0FbSc_3-vha60veyl7RU1DSjTPWR9Ncn3L0DqdNIzdQsJB_ErnzYpXJJ4PxAcvVZ1DZCqe7QloFkytzSIZTTglZpdTMHSo_wDF9hpyc_cZFQDnaeGX3Yx" 

API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.


def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(api_key, term, location):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)

# --- Helpers that build all of the responses ---


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


# --- Helper Functions ---


def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.
    Note that this function would have negative impact on performance.
    """
    try:
        return func()
    except KeyError:
        return None


def isvalid_city(city):
    valid_cities = ['new york', 'jersey city', 'newark', 'philadelphia', 'edgewater',
                    'nashville', 'manhattan', 'queens', 'brooklyn', 'flushing', 'elmhurst']
    return city.lower() in valid_cities


def isvalid_cuisine(cuisine):
    valid_cuisines = ['chinese', 'japanese', 'italian', 'mexican', 'indian']
    return cuisine.lower() in valid_cuisines


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def validate_requirement(slots):
    print("validate_requirement ", slots)
    location = try_ex(lambda: slots['Location'])
    cuisine = try_ex(lambda: slots['Cuisine'])
    dining_date = try_ex(lambda: slots['Date'])
    email = try_ex(lambda: slots['Email'])

    if location and not isvalid_city(location):
        return build_validation_result(
            False,
            'Location',
            '{} is not a valid destination. Please try a different city!'.format(location)
        )

    if cuisine and not isvalid_cuisine(cuisine):
        return build_validation_result(
            False,
            'Cuisine',
            '{} is not a valid cuisine. Please try a different cuisine?'.format(cuisine)
        ) 

    if dining_date:
        if not isvalid_date(dining_date):
            return build_validation_result(False, 'Date', 'I did not understand your date.  When would you like to have dinner?')
        if datetime.datetime.strptime(dining_date, '%Y-%m-%d').date() <= datetime.date.today():
            return build_validation_result(False, 'Date', 'Reservations must be scheduled at least one day in advance.  Can you try a different date?')

    if email and '@' not in email:
        return build_validation_result(
            False,
            'Email',
            '{} is not a valid email address. Please provide a valid email address.'.format(email)
        )

    return {'isValid': True}


""" --- Functions that control the bot's behavior --- """


def dining_suggestion(intent_request):
    """
    Performs dialog management and fulfillment for suggest a dinner.
    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """

    location = try_ex(lambda: intent_request['currentIntent']['slots']['Location'])
    cuisine = try_ex(lambda: intent_request['currentIntent']['slots']['Cuisine'])
    number_people = try_ex(lambda: intent_request['currentIntent']['slots']['PartySize'])
    date = try_ex(lambda: intent_request['currentIntent']['slots']['Date'])
    time = try_ex(lambda: intent_request['currentIntent']['slots']['Time'])
    email = try_ex(lambda: intent_request['currentIntent']['slots']['Email'])
    phone = try_ex(lambda: intent_request['currentIntent']['slots']['Phone'])
    
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    # Load confirmation history and track the current reservation.
    suggestion = json.dumps({
        'location': location,
        'cuisine': cuisine,
        'number_people': number_people,
        'dining_date': date,
        'dining_time': time,
        'email': email,
        'phone': phone
    })
    print("suggestion 1: {}".format(suggestion))
        
    session_attributes['suggestion'] = suggestion

    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate_requirement(intent_request['currentIntent']['slots'])
        print("reach here 1")
        if not validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            slots[validation_result['violatedSlot']] = None
            print("reach here  2")
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )

        print("reach here  3")
        session_attributes['suggestion'] = suggestion
        return delegate(session_attributes, intent_request['currentIntent']['slots'])

    logger.debug('suggested 2: {}'.format(suggestion))
    
    # Send the requests from users to the SQS
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName = "DiningConciergeChatbotQueue") # get the URL of SQS
    if location and cuisine and number_people and date and time and email and phone:
        queue_response = queue.send_message(MessageBody = suggestion)
        print("SUCESSFULLY SENDING TO SQS")

    try_ex(lambda: session_attributes.pop('suggestion'))
    
    session_attributes['lastConfirmedReservation'] = suggestion

    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'You’re all set. Expect my suggestions shortly! Have a good day.'
        }
    )


def trivial_response(intent_request):
    pass


# --- Intents ---


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionIntent':
        return dining_suggestion(intent_request)
    elif intent_name == 'GreetingIntent' or intent_name == 'ThankYouIntent':
        return trivial_response(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


# --- Main handler ---


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
   

    return dispatch(event)