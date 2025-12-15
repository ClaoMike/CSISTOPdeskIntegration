from enum import Enum
from ConfigurationManager import ConfigurationManager

class RequestType(Enum):
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    GET = "GET"

class HttpResponseEvaluator:
    @staticmethod
    def announce_request(url, request_type: RequestType, json=None, params=None):
        print("\n## HTTP REQUEST ##")
        print(f"Performing a {request_type.value} request at {url}")
        if json is not None:
            print(f"Payload (json) {json}")
        if params is not None:
            print(f"Parameters (params) {params}")

    @staticmethod
    def evaluate(response, hide_response=False):
        if 200 <= response.status_code < 300:
            if hide_response:
                print(f"Request was successful ({response.status_code}): "
                      + f"{ConfigurationManager.hide_data(response.text)}")
            else:
                print(f"Request was successful ({response.status_code}): {response.text}")
            print("##################\n")
        else:
            print(f"Error {response.status_code}: {response.text}")
            print("##################\n")
            raise SystemExit