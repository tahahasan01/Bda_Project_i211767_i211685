from flask import Flask, render_template
from kafka import KafkaProducer, KafkaConsumer

app = Flask(__name__)

# Set up Kafka producer and consumer
producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
consumer = KafkaConsumer('user_playback_events', bootstrap_servers=['localhost:9092'])

@app.route('/')
def index():
    return render_template('index.html')

# Route for receiving user playback events
@app.route('/playback_event', methods=['POST'])
def playback_event():
    # Extract user playback event from request and send it to Kafka
    # Example: producer.send('user_playback_events', {'user_id': 123, 'track_id': 'xyz'})
    return 'Playback event received'

# Kafka consumer for processing recommendation requests
def recommendation_consumer():
    for message in consumer:
        # Process recommendation request using the trained model
        # Example: recommendations = get_recommendations(message.value['user_id'])
        # Send recommendations back to Kafka topic
        # Example: producer.send('recommendations', recommendations)

# Start Kafka consumer in a separate thread
import threading
consumer_thread = threading.Thread(target=recommendation_consumer)
consumer_thread.start()

if __name__ == '__main__':
    app.run(debug=True)
