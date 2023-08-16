import util.request as request
import util.config as config


def get_fsu_token():
    url = 'https://meego.feishu.cn/open_api/authen/plugin_token'
    header = {'Content-Type': 'application/json'}
    payload = {
        "plugin_id": config.plugin_id,
        "plugin_secret": config.plugin_secret
    }
    result = request.post(url, header=header, payload=payload)
    token = result['data']['token']
    return token


def get_comm_header():

    header = {
        'X-User-Key': config.x_user_key,
        'Content-Type': 'application/json'
    }
    if get_fsu_token():
        plugin_token = {"X-Plugin-Token": get_fsu_token()}
        headers = dict(plugin_token, **header)
        return headers
    else:
        return None

