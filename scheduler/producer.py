import os

import pika


EXCHANGE_NAME = "jobs"
QUEUE_NAME = "router_jobs"
ROUTING_KEY = "check_interfaces"


def get_connection(host):
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    username = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")

    credentials = pika.PlainCredentials(
        username=username,
        password=password,
    )

    parameters = pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=credentials,
        heartbeat=60,
        blocked_connection_timeout=30,
    )

    return pika.BlockingConnection(parameters)


def declare_topology(channel):
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type="direct",
        durable=True,
    )

    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True,
    )

    channel.queue_bind(
        queue=QUEUE_NAME,
        exchange=EXCHANGE_NAME,
        routing_key=ROUTING_KEY,
    )


def produce_many(host, bodies):
    connection = get_connection(host)

    try:
        channel = connection.channel()

        # สร้าง exchange และ queue เสมอ แม้ bodies จะว่าง
        declare_topology(channel)

        sent = 0

        for body in bodies:
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=ROUTING_KEY,
                body=body,
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=pika.DeliveryMode.Persistent,
                ),
            )
            sent += 1

        return sent
    finally:
        if connection.is_open:
            connection.close()


def produce(host, body):
    return produce_many(host, [body])


if __name__ == "__main__":
    test_body = b'{"router_ip": "192.168.1.44"}'
    produce("rabbitmq", test_body)
    print("Test message published", flush=True)