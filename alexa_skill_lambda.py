"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import time
import urllib
import json
import datetime
from time import mktime

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Starting your Pomodoro session of 25 mins. Stay Productive"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    #reprompt_text = "Please tell me your favorite color by saying, " \
                    #"my favorite color is red."
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}

def GetMeTime(intent, session):   
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    city = intent['slots']['city']['value']
    
    maps_url = "https://maps.googleapis.com/maps/api/geocode/json?"
    maps_key = ""
    maps_req = maps_url + "address=" + city + "&key=" + maps_key
    
    resp = urllib.urlopen(maps_req)
    r = json.load(resp)
    location = r['results'][0]['geometry']['location']
    latitude = location['lat']
    longitude = location['lng']
    timestamp = int(time.time())

    api_url = "https://maps.googleapis.com/maps/api/timezone/json?"
    loc = str(latitude) + "," + str(longitude)
    key = ""

    api_call = api_url + "location=" + str(loc) + "&timestamp=" + str(timestamp) + "&key=" + key
    resp = urllib.urlopen(api_call)
    t = json.load(resp)
    time_diff = t['rawOffset'] + t['dstOffset']
    dt = datetime.datetime.utcnow()
    sec_since_epoch = mktime(dt.timetuple()) + dt.microsecond/1000000.0
    current_time = time_diff + sec_since_epoch
    current_time = time.ctime(current_time)
    
    c_time_hr = str(current_time).split(':')[0]
    c_time_hr = c_time_hr.rsplit(" ")[3]
    c_time_min = str(current_time).split(':')[1]
    
    speech_output = "The current time in " + city + " is" + str(c_time_hr) + "hours and" + str(c_time_min) + "minutes"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, should_end_session))

def set_color_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Color' in intent['slots']:
        favorite_color = intent['slots']['Color']['value']
        session_attributes = create_favorite_color_attributes(favorite_color)
        speech_output = "I now know your favorite color is " + \
                        favorite_color + \
                        ". You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
        reprompt_text = "You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your favorite color is. " \
                        "You can tell me your favorite color by saying, " \
                        "my favorite color is red."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "favoriteColor" in session.get('attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        speech_output = "Your favorite color is " + favorite_color + \
                        ". Goodbye."
        should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "You can say, my favorite color is red."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetMeTime":
        return GetMeTime(intent, session)
    elif intent_name == "WhatsMyColorIntent":
        return get_color_from_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])

# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
    if event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
