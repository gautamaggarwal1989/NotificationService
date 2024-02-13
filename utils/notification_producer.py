''' Module abstracting the functionality to move the
api validated notification message on the kafka queue with
ack=all and retrying in case it fails.
'''

import json
import sys
sys.path.append('..')

from kafka import KafkaProducer

from config import BOOTSTRAP_SERVERS


class InvalidNotificationFormat(Exception):
    '''Invalid format for the notification message'''


class NotificationProducer:
    '''
    Producer class for notification messages.
    Input json format: 
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
    '''

    def get_topic(self, message: str) -> str:
        '''
        Extracts the channel name from the input json.
        Channel name will be used as a topic.
        '''
        try:
            message = json.loads(message)
            channel = message['channel']
        except json.JSONDecodeError:
            raise InvalidNotificationFormat

        return channel

    def register_notification(self, message: str) -> None:
        '''
        Registers the message for further evaluation on the kafka
        broker.
        '''
        topic_name = self.get_topic(message)
        self.producer.send(topic_name, message)

    def __enter__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            # Serialize the json messages
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.producer.close()
