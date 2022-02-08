# -*- coding: utf-8 -*-

from Tea.core import TeaCore
from Tea.exceptions import UnretryableException

from alibabacloud_sas20181203.client import Client as Sas20181203Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_sas20181203 import models as sas_20181203_models
from alibabacloud_tea_util.client import Client as UtilClient

from MangoBot import MangoBot
from AccessKeyPair import AccessKeyPair
import ujson
import html2text
# from pathlib import Path  # for testing purposes
import time
from threading import Thread
from os import path

script_path = path.dirname(path.abspath(__file__)) + "/"
verbose = True


class DescribeSuspEvents:
    # test_flip = True  # for testing purposes

    debug_file = script_path + 'AegisAlertBeeperDebug.log'
    output_file = script_path + 'AegisAlertBeeper.log'

    def __init__(self):
        pass

    @staticmethod
    def get_suspected_events():  # -> tuple[set, str, list]:

        alerts_formatted_str_list = []
        alerts_formatted_str = ''
        alerts = set()

        response_json = DescribeSuspEvents.ali_sas_get_alerts({"dealed": "N", "from_": "sas"})

        # For testing purposes:
        # if DescribeSuspEvents.test_flip:
        #     response_json = ujson.load(open(
        #         str(Path("C:\\Users\\Coiosep\\Documents\\Scripts_dump\\DescribeSuspEventsSampleOutput_resp_json.json")),
        #         "r", encoding='utf-8'))
        # else:
        #     response_json = ujson.load(open(
        #         str(Path("C:\\Users\\Coiosep\\Documents\\Scripts_dump"
        #                  "\\DescribeSuspEventsSampleOutput_resp_json_noresult.json")),
        #         "r", encoding='utf-8'))
        # ~~~For testing purposes

        if response_json is not None:
            if response_json.get('body') is not None:
                if response_json.get('body').get('TotalCount') <= 0:
                    # tmp = 'No alerts for now.'
                    alerts_formatted_str = ''
                else:
                    log_to_file(DescribeSuspEvents.debug_file,
                                ujson.dumps(response_json, indent=4, ensure_ascii=False).encode('utf-8').decode() +
                                '\n\n')

                    alerts, alerts_formatted_str, alerts_formatted_str_list = DescribeSuspEvents.get_alert_info(
                        response_json)

        # send_msg(alerts_str)
        # print(alerts_str)

        # return a set of each alerts found using AlarmUniqueInfo key and its formatted output
        return alerts, alerts_formatted_str, alerts_formatted_str_list

    @staticmethod
    def get_alert_info(response_json):
        are_there_ignored_servers = False
        alert_info_str = ''
        alert_info_str_list = []
        alert_set = set()  # a set of 'AlarmUniqueInfo' strings

        for alert in response_json.get('body', '').get('SuspEvents', ''):
            alert_info = ''
            if is_server_ignored(str(alert.get('InstanceName')),
                                 str(alert.get('IntranetIp'))):
                are_there_ignored_servers = True
            else:
                handled = str(alert.get('EventStatus')) != '1'  # 1 means PENDING (to be processed)
                if not handled:
                    emoji = '🔥🔥🔥'
                else:
                    emoji = '✅✅✅'

                alert_set.add(alert.get('AlarmUniqueInfo'))
                alert_info += '{}SKG aegis alert:\n'.format(emoji) + \
                                  '描述: ' + str(alert.get('Desc')) + '\n' + \
                                  '实例名称: ' + str(alert.get('InstanceName')) + '\n' + \
                                  '互联网IP: ' + str(alert.get('InternetIp')) + '\n' + \
                                  '内网IP: ' + str(alert.get('IntranetIp')) + '\n'

                alert_info += DescribeSuspEvents.get_alert_details(alert)

                if handled:
                    alert_info += '\n' + DescribeSuspEvents.get_alert_handling_details(alert)

                alert_info_str += alert_info
                alert_info_str_list.append(alert_info)

        if are_there_ignored_servers:
            # alert_info_str += "\nThere are unhandled ignored servers."
            log_to_file(DescribeSuspEvents.debug_file, "There are unhandled ignored servers.\n")

        return alert_set, alert_info_str, alert_info_str_list

    @staticmethod
    def create_client(
            access_key_id: str,
            access_key_secret: str,
    ) -> Sas20181203Client:
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret
        )
        config.endpoint = 'tds.aliyuncs.com'
        return Sas20181203Client(config)

    @staticmethod
    def get_alert_details(susp_events):
        alert_details_str = ''

        alert_details = susp_events.get('Details')
        if alert_details is not None:
            for detail in alert_details:
                alert_details_str += detail.get('NameDisplay') + ': '

                if detail.get('Type') == 'html':
                    # html = detail.get('ValueDisplay')
                    # alert_details_str += html2text.html2text(html)
                    alert_details_str += DescribeSuspEvents.get_string_from_html(
                        str(detail.get('ValueDisplay'))).strip()
                else:
                    alert_details_str += str(detail.get('ValueDisplay')).strip()
                    alert_details_str += '\n'

        if alert_details_str == '':
            alert_details_str = '--Alert has no details--'

        return alert_details_str

    @staticmethod
    def get_alert_handling_details(susp_events):

        str_operate_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(susp_events.get('OperateTime') / 1000))
        str_detail = DescribeSuspEvents.get_string_from_html(str(susp_events.get('MarkMisRules'))).strip()
        str_status = str_operate_error_code = str(susp_events.get('OperateErrorCode'))

        if not (str_detail == '' or str_detail is None):
            str_detail = '\n详细内容: ' + str_detail

        if str_operate_error_code == 'advance_mark_mis_info.Success':
            str_status = '添加白名单'  # Add Whitelist
        if str_operate_error_code == 'ignore.Success':
            str_status = '已忽略'  # Ignored
        if str_operate_error_code == 'manual_handled.Success':
            str_status = '我已手工处理'  # I have processed manually

        return '警报已处理\n' + \
               '处理时间: ' + str_operate_time + '\n' + \
               '状态: ' + str_status + \
               str_detail + '\n'

    @staticmethod
    def get_string_from_html(input_html_text) -> str:
        html = html2text.HTML2Text()
        html.ignore_emphasis = True
        html_text = input_html_text.replace('<strong>', '') \
            .replace('<\\/strong>', '') \
            .replace('</strong>', '') \
            .replace(';', '') \
            .replace('&nbsp', '&nbsp;') \
            .replace('<code>', '') \
            .replace('<\\/code>')
        return html.handle(html_text)

    @staticmethod
    def ali_sas_get_alerts(request_parameters: dict) -> dict:
        access_key_pair = AccessKeyPair()

        client = DescribeSuspEvents.create_client(access_key_pair.get_access_id(),
                                                  access_key_pair.get_access_key())

        request = sas_20181203_models.DescribeSuspEventsRequest(**request_parameters)

        try:
            response = client.describe_susp_events(request)
        except UnretryableException:
            if verbose:
                print("Alibaba Connection Timeout")
            log_to_file(DescribeSuspEvents.debug_file,
                        "Alibaba Connection Timeout.{}\n".format(str(UnretryableException)))
            response = ''
        except Exception as e:
            if verbose:
                print("Alibaba Connection failed. {}".format(str(e)))
            log_to_file(DescribeSuspEvents.debug_file, "Alibaba Connection Failed.{}\n".format(str(e)))
            response = ''

        response_json = ujson.loads(UtilClient.to_jsonstring(TeaCore.to_map(response)))

        return response_json


def log_to_file(filename, message):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(message)


def is_server_ignored(instance_name: str, intranet_ip: str) -> bool:
    ignore = False
    if instance_name != '':  # and instance_name != 'None':
        if 'pino' in instance_name:
            ignore = True
    if intranet_ip != '':  # and intranet_ip != 'None':
        if '172.18' in intranet_ip:
            ignore = True

    return ignore


def pair_list_str(str_list: [str]):
    if not bool(str_list):
        return []

    list_length = len(str_list)
    paired_list_str = [str_list[i] + str_list[i + 1] for i in range(0, list_length - 1, 2)]
    if list_length % 2 == 1:
        paired_list_str.append(str_list[list_length - 1])

    # print(paired_list_str)
    return paired_list_str


def send_by_batch(str_list: [str]):  # Sends a mango message containing at most 4 alerts each
    paired_list = pair_list_str(str_list)
    quad_list = pair_list_str(paired_list)
    mango_bot = MangoBot()

    for msg in quad_list:
        Thread(target=mango_bot.send_msg, args=(msg,)).start()  # do sending to mango asynchronously


def main():
    alerts_now = set()
    alerts_last_time = set()
    mango_bot = MangoBot()

    while True:
        time_str = time.strftime("%m/%d/%Y %H:%M:%S", time.localtime()) + ": Checking for Alerts..."
        if verbose:
            print(time_str)
        log_to_file(DescribeSuspEvents.debug_file, time_str + '\n')

        alerts_now, alerts_str, alerts_str_list = DescribeSuspEvents.get_suspected_events()

        if verbose:
            print(alerts_str)
        log_to_file(DescribeSuspEvents.debug_file, alerts_str)
        if alerts_str != '':
            log_to_file(DescribeSuspEvents.output_file, alerts_str + '\n\n')
            # mango_bot.send_msg(alerts_str)
            send_by_batch(alerts_str_list)

        # show handled alerts one last time with additional details, i.e. those with status != 1
        alerts_handled = alerts_last_time.difference(alerts_now)

        for alarm in alerts_handled:

            param = {"from_": "sas", "alarm_unique_info": str(alarm)}
            resp_json = DescribeSuspEvents.ali_sas_get_alerts(param)

            log_to_file(DescribeSuspEvents.debug_file,
                        ujson.dumps(resp_json, indent=4, ensure_ascii=False).
                        encode('utf-8').decode() + '\n\n')

            the_same_alarm, tmp, tmp_list = DescribeSuspEvents.get_alert_info(resp_json)

            if verbose:
                print(tmp)
            log_to_file(DescribeSuspEvents.output_file, tmp)
            # mango_bot.send_msg(tmp)
            send_by_batch(tmp_list)
            # Thread(target=mango_bot.send_msg, args=(tmp,)).start()  # do sending to mango asynchronously

            alerts_last_time.remove(alarm)  # update the set items

        # add new alerts to existing set
        alerts_last_time.update(alerts_now.difference(alerts_last_time))

        dbg_tmp = "dbg: alerts_last_time: " + str(alerts_last_time) + '\n' + \
                  "dbg: alerts_handled: " + str(alerts_handled) + '\n' + \
                  "dbg: alerts_now: " + str(alerts_now) + '\n'
        log_to_file(DescribeSuspEvents.debug_file, dbg_tmp)

        # DescribeSuspEvents.test_flip = not DescribeSuspEvents.test_flip  # For testing purposes

        time.sleep(20 - time.time() % 20)  # get alerts every :00th, :20th and :40th second


if __name__ == '__main__':
    main()
