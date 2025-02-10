from os import write

import pika
import base64
import os
import importlib.util

# Directory to store the new settings file
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, r"app/tools")

SETTINGS_FILE = f"{files_dir}/settings.py"
SIGNAL_FILE = f"{files_dir}/signal"

# Ensure the directory exists


def reload_settings():
    """Dynamically reload the settings.py module"""
    spec = importlib.util.spec_from_file_location("settings", SETTINGS_FILE)
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)
    print("🔄 Settings reloaded successfully!")
    return settings  # Return updated settings module


def receiver():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='file_queue')

    def callback(ch, method, properties, body):
        decoded_file = base64.b64decode(body)

        # Save the new settings file
        with open(SETTINGS_FILE, "wb") as file:
            file.write(decoded_file)

        print(f"✅ File received and saved as {SETTINGS_FILE}")
        with open(SIGNAL_FILE, 'w') as signal:
            pass
        # Reload the settings dynamically
        settings = reload_settings()

        # Print new settings
        print(f"🔹 New Settings:\nSYMBOL={settings.SYMBOL}\nINTERVAL={settings.INTERVAL}\n"
              f"ADX_PERIOD={settings.ADX_PERIOD}\nSHORT_EMA={settings.SHORT_EMA}\n"
              f"LONG_EMA={settings.LONG_EMA}\nATR_PERIOD={settings.ATR_PERIOD}\n"
              f"TAKE_PROFIT_ATR={settings.TAKE_PROFIT_ATR}\nSTOP_LOSS_ATR={settings.STOP_LOSS_ATR}\n"
              f"ATR={settings.ATR}")

    channel.basic_consume(queue='file_queue', on_message_callback=callback, auto_ack=True)
    print("📩 Waiting for new settings file...")
    channel.start_consuming()


if __name__ == "__main__":
    receiver()