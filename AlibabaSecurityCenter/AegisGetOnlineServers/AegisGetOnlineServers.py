import ujson
from alibabacloud_sas20181203 import models as sas_20181203_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_sas20181203.client import Client as Sas20181203Client
from alibabacloud_tea_util.client import Client as UtilClient
from Tea.core import TeaCore
script_path = ""


class DescribeCloudCenterInstances:
    debug_file = 'dcci_debug.log'
    output_file = script_path + 'aegis_online_servers.csv'

    def __init__(self):
        with open(script_path + "config.json", "r") as f:
            access_key_pair = ujson.load(f)
        self.access_id = access_key_pair.get("ali_api_access_id")
        self.access_key = access_key_pair.get("ali_api_access_secret_key")

    def run(self, param: dict) -> dict:
        config = open_api_models.Config(
            access_key_id=self.access_id,
            access_key_secret=self.access_key,
            endpoint='tds.aliyuncs.com'
        )
        client = Sas20181203Client(config)

        # criteria_param = {str(param)}
        # criteria_param = {"criteria": str(criteria)}
        # criteria_param = {'criteria': '[{"clientStatus": "online"}]'}
        # print(str(param))

        request = sas_20181203_models.DescribeCloudCenterInstancesRequest(**param)

        try:
            response = client.describe_cloud_center_instances(request)
        except Exception as e:
            log_to_file(DescribeCloudCenterInstances.debug_file,
                        "param: {}\n".format(str(param)))
            log_to_file(DescribeCloudCenterInstances.debug_file,
                        "Alibaba Connection Failed.{}\n".format(str(e)))
            print("Alibaba Connection Failed.{}\n".format(str(e)))
            response = ''

        if response == '':
            response_json = dict()
        else:
            response_json = ujson.loads(UtilClient.to_jsonstring(TeaCore.to_map(response)))

        return response_json

    def get_servers_by_client_stat(self, clt_stat):
        page_size = 1000  # Arbitrarily defaulted to 1000
        parameters = self.param_builder(clt_stat, 1, 1)
        resp_json = self.run(parameters)

        if bool(resp_json):
            total_count = resp_json.get('body').get('PageInfo').get('TotalCount')
            request_count = (total_count // page_size) + 1
            print("Getting list of {} servers ({})...".format(clt_stat, total_count))
        else:
            total_count = request_count = 0

        # print("parameters: ", str(parameters))
        with open(self.output_file, 'w') as f:
            pass  # just clearing the file
        log_to_file(self.output_file, "InstanceName,IntranetIp,Ip\n")  # Adding header to csv file
        for current_page in range(1, request_count + 1):
            parameters = self.param_builder(clt_stat, page_size, current_page)

            # print("calling run with param: ", str(parameters))
            resp_json = self.run(parameters)

            for instance in resp_json.get("body").get("Instances"):
                log_to_file(self.output_file,
                            '{},{},{}\n'.format(str(instance.get("InstanceName")),
                                                str(instance.get("IntranetIp")),
                                                str(instance.get("Ip"))
                                                )
                            )
            # log_to_file(dcci.debug_file,
            #             ujson.dumps(resp_json, indent=4, ensure_ascii=False).encode('utf-8').decode() +
            #             '\n\n')

        if bool(resp_json):
            print("Done, list saved to '{}' file".format(self.output_file))

    @staticmethod
    def param_builder(clt_stat: str, pg_sz: int, cur_pg: int) -> dict:
        return {"criteria": '[{"name": "clientStatus", "value": "' + clt_stat + '"}]',
                "page_size": pg_sz,
                "current_page": cur_pg}


def log_to_file(filename, message):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(message)


if __name__ == '__main__':
    client_status = 'online'  # value can be 'online', 'offline', or 'pause'
    DescribeCloudCenterInstances().get_servers_by_client_stat(client_status)
