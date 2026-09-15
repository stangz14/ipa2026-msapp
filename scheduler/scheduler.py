import os
import time

from bson import json_util

from database import get_router_info
from producer import produce_many


INTERVAL = 10.0
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")


def current_time_string():
    now = time.time()
    date_time = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(now),
    )
    milliseconds = int((now % 1) * 1000)

    return f"{date_time}.{milliseconds:03d}"


def scheduler():
    next_run = time.monotonic()
    count = 0

    while True:
        print(
            f"[{current_time_string()}] run #{count}",
            flush=True,
        )

        try:
            routers = list(get_router_info())

            bodies = [
                json_util.dumps(router).encode("utf-8")
                for router in routers
            ]

            # จะประกาศ queue แม้ bodies ไม่มีข้อมูล
            sent = produce_many(
                RABBITMQ_HOST,
                bodies,
            )

            print(
                f"router records: {len(routers)}, "
                f"messages sent: {sent}",
                flush=True,
            )

        except Exception as error:
            print(
                f"scheduler error: {type(error).__name__}: {error}",
                flush=True,
            )

        count += 1
        next_run += INTERVAL

        delay = max(
            0.0,
            next_run - time.monotonic(),
        )
        time.sleep(delay)


if __name__ == "__main__":
    scheduler()