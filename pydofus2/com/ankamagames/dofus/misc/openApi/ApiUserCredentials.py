class ApiUserCredentials:
    def __init__(
        self, host_name, api_path, api_token, auth_token=None, user_id=-1, api_proxy_server_url="", proxy_path=None
    ):
        self.host_name = host_name
        self.api_token = api_token
        self.auth_token = auth_token
        self.user_id = user_id
        self.api_path = api_path
        self.api_proxy_server_url = api_proxy_server_url
        self.proxy_path = proxy_path
