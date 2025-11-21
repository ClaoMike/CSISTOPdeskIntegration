from ConfigurationManager import ConfigurationManager
from enum import Enum

class RequestType(Enum):
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    GET = "GET"

class HttpResponseEvaluator:
    @staticmethod
    def announce_request(url, request_type: RequestType,):
        print("\n## HTTP REQUEST ##")
        print(f"Performing a {request_type.value} request at {url}")

    @staticmethod
    def evaluate(response, hide_response=False):
        if 200 <= response.status_code < 300:
            if hide_response:
                print(f"Request was successful ({response.status_code}): {ConfigurationManager.hide_data(response.text)}")
            else:
                print(f"Request was successful ({response.status_code}): {response.text}")
            print("##################\n")
        else:
            print(f"Error {response.status_code}: {response.text}")
            print("##################\n")
            raise SystemExit