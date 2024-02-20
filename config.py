# Global settings the effect the functioning of the application.

# Change these servers for live installation.
# Create a cluster and add the brokers here.
BOOTSTRAP_SERVERS = [
    'localhost:9092',
    'localhost:9093',
    'localhost:9094'
]

# Add your custom channel here.
NOTIFICATION_CHANNELS = [
    'mobile',
    'email',
    'whatsapp',
    'app'
]

# All timestamps in the application will use this format
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
