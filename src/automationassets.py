from dotenv import load_dotenv
import os

def get_automation_variable(key: str) -> str:
    load_dotenv()
    return os.getenv(key)

def get_automation_credential(key: str) -> dict[str, str]:
    load_dotenv()
    if key == "CREDENTIAL_TOPDESK_API":
        cred = {}
        cred["username"] = get_automation_variable("TOPDESK_USERNAME")
        cred["password"] = get_automation_variable("TOPDESK_PASSWORD")

        return cred