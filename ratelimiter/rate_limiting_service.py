''' Validates the incoming notifications according
to predefined criteria and then prioritizes the notifications
against rate limiting for a user.
{
    priority: '',
    message: '',
    channel: '', # This will be used as topic in kafka.
    source: '' , # Sent by cart or registration etc. Not required
    uuid: '', # User id through which user will be identified
    tags: [],
    type: '', # Alert, Marketing, etc.
    timestamp: ''
}

If the priority of message is HIGH, It will bypass the rate limiting.
If the priority is medium or low, the messages compete against the
rate limiting. Medium priority messages in the given time frame are sent
first and then the lower priority are sent. So some sort of buffering is
required. We will use redis for this purpose and ratelimiting as well.

(number of notifications per user per minute. This setting can be
changed in config.py)

Note: Each of the faust application can run on a seperate container or
machine to scale horizonatally.
'''
import json
import datetime
import sys
sys.path.append('..')

import faust

from config import BOOTSTRAP_SERVERS, NOTIFICATION_CHANNELS, TIMESTAMP_FORMAT


class Notification(faust.Record):
    priority: str
    message: str
    channel:  str
    source:  str
    uuid: str
    tags: list[str]
    type: str
    timestamp: str

app = faust.App(
    'RateLimiter',
    broker=[
        f'kafka://{server}' for server in BOOTSTRAP_SERVERS
    ]
)


class FilterStreamMixin:
    ''' Use this class along with BaseRateLimiterMixin for a generic
    rate filtering strategy.

    Rewrite this mixin for a specific filtering strategy.
    '''
    
        


class BaseRateLimiterMixin:
    ''' Validates and prioritize the message against given
    rate limiting conditions.
    Uses redis for buffering as well as rate limiting.

    Messages which qualifies the validation and pass the rate limiting
    should be moved to process kafka topic to be processed by corresponding
    consumers for that channel. For example, messages with channel set to
    mobile should be processed by a consumer subscribed to mobile topic.


    This is the base class. Inherit this to write logic for developing seperate logic
    for ratelimiting strategy.
    '''

    def __init__(self, app, topic):
        self.app = app
        self.topic = topic

    def timestamp_valid(self, timestr, format=TIMESTAMP_FORMAT):
        ''' validates if a given timestamp is of given format
        and is a valid timestamp object.
        '''
        try:
            datetime.strptime(timestr, format)

            return True
        except ValueError:
            return False

    def validate_data(self, data):
        '''
        Validation1: Channel should be one of predefined value.
        Validation2: TimeStamp should be valid
        Validation3: Priority should be low, medium or high
        '''
        try:
            data = json.loads(data)

            if data['channel'] not in NOTIFICATION_CHANNELS:
                raise Exception('Invalid channel name!')
            
            if self.timestamp_valid(data['timestamp']):
                raise Exception('Invalid timestamp!')
            
            if data['priority'] not in ['low', 'medium', 'high']:
                raise Exception('Invalid Priority setting!')

        except Exception as e:
            print('Write the logic to log the failed request to db.')
            return False, {}

        return True, data
    
    @app.agent(value_type=Notification)
    async def (self, notifications):
        '''
        Filter the stream and put it on the next stream in line
        for processing by corresponding channel handler.
        '''
        async with notifications.transaction():
            async for notification in notifications:
                is_valid, notification = self.validate_data(notification)

                if is_valid:
                    
                else:
                    ''' Ignore the notification that has been rejected'''
                    pass
