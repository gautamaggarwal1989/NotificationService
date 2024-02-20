''' Validates the incoming notifications according
to predefined criteria and then prioritizes the notifications
against rate limiting for a user.
{
    priority: '',
    message: '',
    channel: '', # This will be used as topic in kafka.
    source: '' , # Sent by cart or registration etc. Not required
    uuid: '',
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
from datetime import datetime

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

def timestamp_valid(timestr, format=TIMESTAMP_FORMAT):
    ''' validates if a given timestamp is of given format
    and is a valid timestamp object.
    '''
    try:
        timestamp_object = datetime.strptime(timestr, format)

        return True
    except ValueError:
        return False


def validate_data(data):
    ''' Notification validator class.
    Validation1: Channel should be one of predefined value.
    Validation2: TimeStamp should be valid
    Validation3: Priority should be low, medium or high
    '''
    try:
        data = json.loads(data)

        if data['channel'] not in NOTIFICATION_CHANNELS:
            raise Exception('Invalid channel name!')
        
        if timestamp_valid(data['timestamp']):
            raise Exception('Invalid timestamp!')
        
        if data['priority'] not in ['low', 'medium', 'high']:
            raise Exception('Invalid Priority setting!')

    except Exception as e:
        print('Write the logic to log the failed request to db.')


@app.agent(value_type=Notification)
async def filter_stream(notification):
    ''' Validates and prioritize the message against given
    rate limiting conditions.
    Uses redis for buffering as well as rate limiting.

    Messages which qualifies the validation and pass the rate limiting
    should be moved to process kafka topic to be processed by corresponding
    consumers for that channel. For example, messages with channel set to
    mobile should be processed by a consumer subscribed to mobile topic.
    '''
    
    