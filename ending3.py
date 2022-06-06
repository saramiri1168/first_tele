import datetime
import traceback
import utility
import database
import requests
import logging


def sending_result(message, chat_id, replay_id):
    utility.telegram_req("sendMessage", chat_id=chat_id, text=str(message), reply_to_message_id=replay_id)


def url_request(url):
    url = "http://" + url
    print(url, ".....")
    try:
        return requests.get(url).status_code
    except:
        return 500


def time_checking():
    print("start")
    while 1:
        domain_status = {}
        p_time = datetime.datetime.now() - datetime.timedelta(seconds=60)
        ok, domain_items = database.receive_data('SELECT * FROM domain WHERE d_lastcheck < :d_lastcheck',
                                                 d_lastcheck=p_time)
        for item in domain_items:
            update_time = database.send_data("UPDATE domain SET d_lastcheck=? WHERE d_id=?",
                                             (datetime.datetime.now(), item[0]))
            if url_request(item[1]) >= 500:
                domain_status[item[0]] = "its down"
            else:
                domain_status[item[0]] = "its up"
        for d_id, status in domain_status.items():
            print(d_id)
            ok, chat_replay_id = database.receive_data("select u_chat_id , s_replay_id from users join sites "
                                                       "on users.u_id=sites.s_u_id and s_d_id = :s_d_id ",
                                                       s_d_id=d_id)

            print(chat_replay_id)

            sending_result(status, chat_replay_id[0][0], chat_replay_id[0][1])




            '''for ids in sites_id:
                u_id, replay_id = ids

                ok, chat_id = database.receive_data("select u_chat_id from users where u_id = :u_id",
                                                    u_id=u_id)
                chat_id = chat_id[0][0]
                sending_result(status, chat_id, replay_id)'''

def main():
    try:
        time_checking()
    except KeyboardInterrupt:
        pass
    finally:
        print("buy")


if __name__ == "__main__":
    main()
