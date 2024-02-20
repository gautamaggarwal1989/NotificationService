''' Fetches the incoming notification on kafka and logs them
into database. We can use mysql or cassandra for this.

This will be used to display information related to notification.
We will expose apis in fastapi to show this information to a dashboard.

Note: Each of the faust application can run on a seperate container or
machine to scale horizonatally.
'''
import sys
sys.path.append('..')
