''' Module abstracting the functionality to move the
api validated notification message on the kafka queue with
ack=all and retrying in case it fails.
'''

class NotificationProducer:
    '''
    Producer class for notification messages.
    '''