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


import faust

from config import BOOTSTRAP_SERVERS


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


class NotificationValidator:
    ''' Notification validator class.
    Validation1: Channel should be one of predefined value.
    Validation2: Source should be one of predefined value.
    Validation3: UUID should not repeat.
    Validation4: Type should be one of predefined value.
    Validation5: Timestamp should be valid.
    Validation6: Priority should be a valid value.

    If the notification validation fails, put them on a seperate
    kafka topic so that logging service can update the db.
    '''



@app.agent(value_type=Notification)
async def validate(notification):
    ''' Validates and prioritize the message against given
    rate limiting conditions.
    Uses redis for buffering as well as rate limiting.

    Messages which qualifies the validation and pass the rate limiting
    should be moved to process kafka topic to be processed by corresponding
    consumers for that channel. For example, messages with channel set to
    mobile should be processed by a consumer subscribed to mobile topic.
    '''
    