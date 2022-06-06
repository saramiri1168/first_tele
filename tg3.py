import logging
import constants
import database
from pathlib import Path
import utility
import datetime
import time


UPDATE_LOCK = Path(__file__).parent / ".update.id"
UPDATE_LOCK.touch(exist_ok=True)




def process_message(message):
    chat_id = str(message['chat']['id'])
    msg = message['text']
    msg_id = message["message_id"]
    try:
        first_name = message["from"]["first_name"]
    except KeyError:
        first_name = ''

    try:
        last_name = message["from"]["last_name"]
    except KeyError:
        last_name = ''

    ans, domain = utility.validation_url(msg)

    if ans:
        database.users(first_name, last_name, chat_id)
        database.domain(domain)
        ok = database.sites(chat_id, domain, msg_id)
        if not ok:
            utility.telegram_req("sendMessage",
                                 chat_id=chat_id,
                                 text=" your link is duplicate",
                                 replay_to_message_id=msg_id)

    else:
        utility.telegram_req("sendMessage",
                             chat_id=chat_id,
                             text='it seems wrong',
                             reply_to_message_id=msg_id)


def process_update(update):
    UPDATE_LOCK.write_text(str(update["update_id"]))

    if "message" in update:
        process_message(update["message"])


def long_polling():

    while True:
        try:
            try:
                offset = int(UPDATE_LOCK.read_text()) + 1

            except (ValueError, TypeError):
                offset = None

            updates = utility.telegram_req("getUpdates", offset=offset)
            if updates and updates["ok"]:
                for update in updates["result"]:
                    process_update(update)

        finally:
            time.sleep(5)


def main():

    created_tables = database.create_table()
    if not created_tables:
        print("table not created")
        exit()

    try:
        long_polling()
    except KeyboardInterrupt:
        pass
    finally:
        print("Bye")


if __name__ == "__main__":
    main()
