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


