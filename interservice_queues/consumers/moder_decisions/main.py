import threading
import time
import signal
import sys

from interservice_queues.consumers.moder_decisions.moderation_decisions_consumer import (
    moderation_decisions_consumer,
)

def run_consumer():
    try:
        moderation_decisions_consumer.start()
    except KeyboardInterrupt:
        print("\n[*] Consumer interrupted. Stopping...")
    finally:
        moderation_decisions_consumer.stop()

def signal_handler(sig, frame):
    print("\n[!] Ctrl+C detected. Shutting down consumer...")
    moderation_decisions_consumer.stop()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


    consumer_thread = threading.Thread(target=run_consumer, daemon=True)
    consumer_thread.start()

    print(f"[*] Main thread running. Consumer started in background for queue '{moderation_decisions_consumer.queue_name}'.")
    print("    Press Ctrl+C to exit gracefully.")

    while True:
        time.sleep(1)
