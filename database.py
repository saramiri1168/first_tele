import sqlite3
import traceback
import logging
import constants
import datetime


def send_data(sql, *args) -> bool:
    try:
        with constants.conn:
            cur = constants.conn.cursor()
            cur.execute(sql, *args)
            return True

    except sqlite3.Error:
        print(traceback.format_exc())
        return False
    except Exception:
        logging.critical("unknown error --> sending data", traceback.format_exc())
        return False


def receive_data(sql, **kwargs) -> (bool, sqlite3.Cursor | None):
    try:
        with constants.conn:
            cur = constants.conn.cursor()
            ans = cur.execute(sql, kwargs)
            return True, ans.fetchall()
    except sqlite3.Error:
        print(traceback.format_exc())
        return False, None
    except Exception:
        logging.critical("Unknown error --> receiving data", traceback.format_exc())
        return False, None


def users(first_name, last_name, chat_id):

    ok, u_details = receive_data('SELECT * FROM users '
                                 'WHERE u_chat_id = :u_chat_id ',
                                 u_chat_id=chat_id)
    if not ok:
        logging.critical("problem in/with selecting details of users")

    if len(u_details) == 0:

        insert_u_info = send_data("INSERT INTO users (u_fname, u_lname, u_chat_id) "
                                  "VALUES (?, ?, ?)",
                                  (first_name, last_name, chat_id))
        if not insert_u_info:
            logging.critical("we couldn't insert user information")


def domain(domain):
    ok, d_details = receive_data('SELECT * FROM domain '
                                 'WHERE d_domain = :d_domain ', d_domain=domain)
    if not ok:
        logging.critical("problem in/with selecting details of domain table")
    if len(d_details) == 0:
        insert_d_info = send_data("INSERT INTO domain (d_domain, d_lastcheck, d_usage) "
                                  "VALUES (?, ?, ?)",
                                  (domain, datetime.datetime.now(), 1))
        if not insert_d_info:
            logging.critical("we couldn't insert domain information")
    else:

        usage = d_details[0][3]
        update_usage = send_data("UPDATE domain SET d_usage=? WHERE d_domain=?",
                                 (usage + 1, domain))
        if not update_usage:
            logging.critical("updating usages had problem")


def sites(chat_id, domain, msg_id):
    ok, user_domain = receive_data("SELECT u_id, d_id FROM users, domain "
                                   "WHERE u_chat_id = :u_chat_id AND d_domain = :d_domain ",
                                    u_chat_id=chat_id, d_domain=domain)
    if not ok:
        logging.critical("")

    print(user_domain)
    u_id, d_id = user_domain[0][0], user_domain[0][1]

    ok, s_details = receive_data('SELECT * FROM sites '
                                 'WHERE s_u_id = :s_u_id '
                                 'AND s_d_id = :s_d_id ',
                                 s_u_id=u_id, s_d_id=d_id)
    if not ok:
        logging.critical("")

    # print(s_details)
    if len(s_details) == 0:
        insert_s_info = send_data("INSERT INTO sites (s_u_id, s_d_id, s_replay_id) "
                                  "VALUES (?, ?, ?)",
                                  (u_id, d_id, msg_id))
        if not insert_s_info:
            logging.critical("")

        return True
    return False


def create_table():

    create_user = send_data("""CREATE TABLE IF NOT EXISTS users
                                    (u_id integer primary key autoincrement,
                                    u_fname text,
                                    u_lname text,
                                    u_chat_id integer
                                    )""")

    create_domain = send_data("""CREATE TABLE IF NOT EXISTS domain
                                    (d_id integer primary key autoincrement,
                                    d_domain text,
                                    d_lastcheck integer,
                                    d_usage integer)""")

    create_sites = send_data("""CREATE TABLE IF NOT EXISTS sites
                                    (s_u_id integer,
                                    s_d_id integer,
                                    s_replay_id integer)""")
    if not create_user or not create_domain or not create_sites:
        return False
    return True


