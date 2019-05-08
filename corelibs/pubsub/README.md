# Google PUBSUB base classes

## Requirements
- Python (2.7, 3.4, 3.5, 3.6, 3.7)

## Setup
Update environment variables:
```
export GOOGLE_CLOUD_PROJECT='project_id'
export GOOGLE_PUBSUB_TOPIC_DEAD_LETTER='dead-letters'
export REDIS_HOST='127.0.0.1'
export REDIS_PORT='6379'
export FAIL_LIMIT='5'
```

## Example
subscriber.py
```
from corelibs.pubsub.subscriber import Subscriber


class TestSubscriber(Subscriber):

    def handle_data(self, data):
        # Handle data from subscription
        print(data)


if __name__ == '__main__':
    test_sub = TestSubscriber('test-subscription')
    test_sub.subscribe()
    while True:
        pass
```

publisher.py
```
from corelibs.pubsub.publisher import Publisher


if __name__ == '__main__':
    data = {'key': 'value'}
    test_pub = Publisher('test')
    test_pub.publish(data)
```
