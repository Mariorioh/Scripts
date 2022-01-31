import argparse

import requests
# import click
# from pprint import pprint
import ujson
import time
from os import path
script_path = path.dirname(path.abspath(__file__)) + "/"


class MangoBot:
    debug_file = script_path + 'MangoBotDebug.log'

    # output_file = 'MangoBot.log'

    def __init__(self):
        with open(script_path + "config.json", "r") as f:
            mango_json = ujson.load(f)
        self.bot_id = mango_json.get('mango_id')
        self.bot_token = mango_json.get('mango_token')
        self.group_room_id = mango_json.get('mango_group_room_id')
        self.base_send_url = mango_json.get('base_send_url')

        self.headers = {
            'Authorization': 'eXwdrXrvrjsHDs7F',
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }

    def send_msg(self, message):
        # print("mango bot message sent: " + message)

        send_msg_url = self.base_send_url + self.bot_id + ':' + self.bot_token + '/sendmessage_v2'
        payload = {
            "targetname": self.group_room_id,
            "text": message,
            "chatType": "2",
            "model": "1"
        }

        time_str = time.strftime("%m/%d/%Y %H:%M:%S", time.localtime())
        dbg_str = time_str + ': MangoBot sending message...\n' + \
                             'payload: ' + str(payload) + '\n' + \
                             'header: ' + str(self.headers) + '\n' + \
                             'send_msg_url: ' + send_msg_url + '\n'
        log_to_file(MangoBot.debug_file, dbg_str)

        rv = ''
        try:
            # rv = requests.post(send_msg_url, headers=self.headers, json=payload)
            rv = requests.post(send_msg_url, json=payload)
        except Exception as e:
            print('Sending mango message failed. {}'.format(str(e)))
            log_to_file(MangoBot.debug_file, 'Sending mango message failed. {}'.format(str(e)))

        # print(str(rv))
        log_to_file(MangoBot.debug_file, str(rv))


def log_to_file(filename, message):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--message', '-m', default='MangoBot Test', help='Enter message')
    args = parser.parse_args()
    message = args.message

    print('hello, mango bot')
    mango_bot = MangoBot()
    print('id: {}\ntoken: {}\nroom id: {}\n'.format(mango_bot.bot_id, mango_bot.bot_token, mango_bot.group_room_id))
    # mango_bot.send_msg('✅✅✅🔥🔥🔥')
    mango_bot.send_msg(message)


if __name__ == '__main__':
    main()
