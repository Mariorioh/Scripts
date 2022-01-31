import ujson
from alibabacloud_sas20181203 import models as sas_20181203_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_sas20181203.client import Client as Sas20181203Client
from alibabacloud_tea_util.client import Client as UtilClient
from Tea.core import TeaCore

import os
import argparse


class AlibabaCaller:
    def __init__(self, script_path):
        with open(script_path + "/config.json", "r") as f:
            access_key_pair = ujson.load(f)
        self.access_id = access_key_pair.get("ali_api_access_id")
        self.access_key = access_key_pair.get("ali_api_access_secret_key")
        self.debug_file = script_path + '/ali_caller_debug.log'
        self.output_file = script_path + '/ali_caller.log'
        self.vulnerability_map = {1: "Not Repaired",
                                  2: "Repair Failed",
                                  3: "Rollback Failed",
                                  4: "Repair in Progress",
                                  5: "Rollback in Progress",
                                  6: "Verification in Progress",
                                  7: "Repair Successful",
                                  8: "Repair Successful - Pending Restart",
                                  9: "Rollback Successful",
                                  10: "Ignored",
                                  11: "Rollback Successful - Pending Restart",
                                  12: "Vulnerability Does Not Exist",
                                  20: "Disabled"}

    @staticmethod
    def describe_instances_param_builder(instance_name: str = '',
                                         intranet_ip: str = '',
                                         clt_stat: str = '',
                                         pg_sz: int = 0,
                                         cur_pg: int = 0) -> dict:
        parameter = {}
        criteria_str = ''

        if instance_name != '':
            criteria_str += '"name": "instanceName", "value": "' + instance_name + '"'
        if clt_stat != '':
            criteria_str += AlibabaCaller.comma_str(criteria_str) + \
                            '"name": "clientStatus", "value": "' + clt_stat + '"'
        if intranet_ip != '':
            criteria_str += AlibabaCaller.comma_str(criteria_str) + \
                            '"name": "intranetIp", "value": "' + intranet_ip + '"'

        if criteria_str != '':
            parameter.update({"criteria": "[{" + criteria_str + "}]"})

        if pg_sz != 0:
            parameter.update({"page_size": pg_sz})
        if cur_pg != 0:
            parameter.update({"current_page": cur_pg})

        return parameter

    @staticmethod
    def comma_str(criteria_str):
        return '' if criteria_str == '' else ','

    def describe_instances(self, param: dict) -> dict:

        client = self.get_sas_config()

        request = sas_20181203_models.DescribeCloudCenterInstancesRequest(**param)

        try:
            response = client.describe_cloud_center_instances(request)
        except Exception as e:
            log_to_file(self.debug_file,
                        "param: {}\n".format(str(param)))
            log_to_file(self.debug_file,
                        "Alibaba Connection Failed. {}\n".format(str(e)))
            print("Alibaba Connection Failed. {}\n".format(str(e)))
            response = ''

        if response == '':
            response_json = dict()
        else:
            response_json = ujson.loads(UtilClient.to_jsonstring(TeaCore.to_map(response)))

        return response_json

    def get_sas_config(self):
        config = open_api_models.Config(
            access_key_id=self.access_id,
            access_key_secret=self.access_key,
            endpoint='tds.aliyuncs.com'
        )
        client = Sas20181203Client(config)
        return client

    @staticmethod
    def describe_vul_param_builder(uuid: str = '', vul_type: str = 'cve') -> dict:
        parameter = {'uuids': uuid, 'type': vul_type}

        return parameter

    def describe_vul(self, param: dict) -> dict:

        client = self.get_sas_config()

        request = sas_20181203_models.DescribeVulListRequest(**param)

        try:
            response = client.describe_vul_list(request)
        except Exception as e:
            log_to_file(self.debug_file,
                        "param: {}\n".format(str(param)))
            log_to_file(self.debug_file,
                        "Alibaba Connection Failed. {}\n".format(str(e)))
            print("Alibaba Connection Failed. {}\n".format(str(e)))
            response = ''

        if response == '':
            response_json = dict()
        else:
            response_json = ujson.loads(UtilClient.to_jsonstring(TeaCore.to_map(response)))

        return response_json

    def get_vul_list(self, instance_name: str, intranet_ip: str, vul_status: int = 0) -> list:
        uuid, client_status, vul_count = self.get_uuid(instance_name=instance_name, intranet_ip=intranet_ip)

        vul_list = []
        if uuid == 'not found':
            return vul_list

        describe_vul_param = self.describe_vul_param_builder(uuid, vul_type='cve')
        vul_info_json = self.describe_vul(describe_vul_param)

        # print(ujson.dumps(vul_info_json, indent=4, ensure_ascii=False).encode('utf-8').decode())  # testing

        # log_to_file(self.debug_file,
        #             ujson.dumps(vul_info_json, indent=4, ensure_ascii=False).encode('utf-8').decode())
        if bool(vul_info_json):
            if vul_info_json.get('body').get('TotalCount') != 0:
                for vulnerability in vul_info_json.get('body').get('VulRecords'):
                    # if not (vul_status != 0 and vul_status == vulnerability.get('Status')):
                    #     continue
                    if vul_status == 0 or vul_status == vulnerability.get('Status'):
                        vul_list.append({"InstanceName": instance_name,
                                         "uuid": uuid,
                                         "name": vulnerability.get('Name'),
                                         "alias_name": vulnerability.get('AliasName'),
                                         "tag": vulnerability.get('Tag'),
                                         "type": vulnerability.get('Type'),
                                         "status": vulnerability.get('Status'),
                                         "result_message": vulnerability.get('ResultMessage')}
                                        )
                    # "level": vulnerability.get('Level')})
                    # print(ujson.dumps(vulnerability, indent=4, ensure_ascii=False))

        # print(ujson.dumps(vul_list, indent=4, ensure_ascii=False))
        return vul_list

    @staticmethod
    def modify_operate_vul_param_builder(type: str = '',
                                         operate_type: str = 'vul_fix',
                                         uuid: str = '',
                                         vul_name: str = '',
                                         vul_tag: str = '') -> dict:
        # Info parameter format:
        # '[{"name":"<vulnerabilit name>","uuid":"<server uuid>","tag":"<vulnerability tag>"}]'
        # Example value:
        # name = oval:com.redhat.rhsa:def:xxxxxxxx
        # uuid = inet-9e92e9dd-9195-4144-a4a2-e4807a8xxxxx
        # tag = oval

        info_str = '[{"name":"' + vul_name + '","uuid":"' + uuid + '","tag":"' + vul_tag + '"}]'

        parameter = {'type': type,
                     'operate_type': operate_type,
                     'info': info_str}
        return parameter

    def modify_operate_vul(self, param: dict) -> dict:
        client = self.get_sas_config()
        request = sas_20181203_models.ModifyOperateVulRequest(**param)

        try:
            response = client.modify_operate_vul(request)
        except Exception as e:
            log_to_file(self.debug_file,
                        "modify_operate_vul() param: {}\n".format(str(param)))
            log_to_file(self.debug_file,
                        "Alibaba Connection Failed. {}\n".format(str(e)))
            # print("Alibaba Connection Failed. {}\n".format(str(e)))
            response = ''

        if response == '':
            response_json = dict()
        else:
            response_json = ujson.loads(UtilClient.to_jsonstring(TeaCore.to_map(response)))

        return response_json

    def get_uuid(self, instance_name: str, intranet_ip: str):

        server_info_param = self.describe_instances_param_builder(instance_name=instance_name,
                                                                  intranet_ip=intranet_ip)
        servers_info_json = self.describe_instances(server_info_param)

        uuid = 'not found'
        client_status = 'server not found'
        vul_count = 0
        if not bool(servers_info_json):
            return uuid, client_status, vul_count

        # print(ujson.dumps(servers_info_json, indent=4, ensure_ascii=False).encode('utf-8').decode())
        total_count = servers_info_json.get('body').get('PageInfo').get('TotalCount')

        if total_count <= 0:
            return uuid, client_status, vul_count

        server = servers_info_json.get('body').get('Instances')

        for instance in server:
            client_status = instance.get('ClientStatus')
            vul_count = instance.get('VulCount')
            if client_status == 'online':
                break

        if total_count > 1:
            # then handle this manually
            uuid = 'please handle manually'
        else:
            uuid = server[0].get('Uuid')

        # print('uuid: ', uuid)
        return uuid, client_status, vul_count


def log_to_file(filename, message):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(message)


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--instanceName', '-in', help='Enter Instance Name', default='')
    parser.add_argument('--intranetIP', '-ip', help='Enter intranet IP', default='')
    parser.add_argument('--outputFile', '-of', help='Enter output file name (default is server_list_uuid.csv)',
                        default='server_list_uuid.csv')
    parser.add_argument('--serverListFile', '-slf', help='Enter server list file name (default is server_list.csv)',
                        default='server_list.csv')
    parser.add_argument('--dir', '-d', help='Enter directory name',
                        default=os.path.dirname(os.path.abspath(__file__)))
    return parser.parse_args()


if __name__ == '__main__':
    args = get_arguments()

    script_dir = args.dir
    output_file = args.outputFile
    server_list_filename = script_dir + '/' + args.serverListFile
    inst_name = args.instanceName
    intra_ip = args.intranetIP

    if inst_name == '' and intra_ip == '':
        file_mode = True
    else:
        file_mode = False

    ali_caller = AlibabaCaller(script_dir)
    if not file_mode:
        print('uuid | client status | vul_count:  ', ali_caller.get_uuid(instance_name=inst_name, intranet_ip=intra_ip))

    else:
        # print('server_list_filename: ', server_list_filename)
        server_list_file = open(server_list_filename, 'r+')

        with open(output_file, 'w') as f:
            pass  # just clearing the file
        log_to_file(output_file,
                    "IntranetIp,InstanceName,Uuid,Link,HasVulnerability,ClientStatus\n")  # Adding header to csv file

        for line in server_list_file:
            intranet_ip, instance_name = line.strip().split(",")

            uuid, client_status, vul_count = ali_caller.get_uuid(instance_name=instance_name, intranet_ip=intranet_ip)

            print("Getting uuid of server:{} {} {} {}...".format(instance_name, intranet_ip, client_status, vul_count))
            link_str = ''
            if uuid != 'not found' and uuid != 'please handle manually':
                link_str = "https://yundun.console.aliyun.com/?p=sas#/assetsDetail/" + \
                           uuid + "-IP-" + intranet_ip + "/vul/0/cn-hangzhou"
            log_to_file(output_file,
                        '{},{},{},{},{},{}\n'.format(intranet_ip,
                                                     instance_name,
                                                     uuid,
                                                     link_str,
                                                     vul_count,
                                                     client_status
                                                     )
                        )
