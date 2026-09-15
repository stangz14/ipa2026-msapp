import os
import time

import pika

from callback import callback


def consume():
    host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    user = os.getenv("RABBITMQ_USER", "admin")
    password = os.getenv("RABBITMQ_PASSWORD", "rabbitmq")

    for attempt in range(10):
        try:
            print(f"Connecting to RabbitMQ (try {attempt})...")
            credentials = pika.PlainCredentials(user, password)
            parameters = pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=credentials,
                heartbeat=60,
                blocked_connection_timeout=30,
            )
            conn = pika.BlockingConnection(parameters)
            break
        except Exception as e:
            print(f"Failed: {e!r}")
            time.sleep(5)
    else:
        print("Could not connect after 10 attempts")
        exit(1)

    ch = conn.channel()
    ch.queue_declare(queue="router_jobs", durable=True)
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue="router_jobs", on_message_callback=callback, auto_ack=True)
    ch.start_consuming()


if __name__ == "__main__":
    consume()
