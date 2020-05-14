import requests
import xmltodict
from urllib.parse import urlparse

APPDB_URL = "https://appdb.egi.eu"

def appdb_call(path, retries=3):
    """
    Basic AppDB REST API call
    """
    data = None
    cont = 0
    while data == None and cont < retries:
        cont + 1
        resp = requests.request("GET", APPDB_URL + path, verify=False)
        if resp.status_code == 200:
            data = xmltodict.parse(resp.text.replace('\n', ''))['appdb:appdb']

    return data

def get_vo_list():
    vos = []
    data = appdb_call('/rest/1.0/vos')
    if data:
        for vo in data['vo:vo']:
            vos.append(vo['@name'])
    return vos

def check_supported_VOs(site, vo):
    if not vo:
        return True

    if 'provider:image' in site:
        for os_tpl in site['provider:image']:
            if '@voname' in os_tpl and vo in os_tpl['@voname']:
                return True
    return False

def _get_services(vo=None):
    appdburl = '/rest/1.0/sites'
    if vo:
        appdburl += '?flt=%%2B%%3Dvo.name:%s&%%2B%%3Dsite.supports:1' % vo

    data = appdb_call(appdburl)

    if not data or 'appdb:site' not in data:
        return []

    if isinstance(data['appdb:site'], list):
        sites = data['appdb:site']
    else:
        sites = [data['appdb:site']]

    services = []
    for site in sites:
        if 'site:service' in site:
            if isinstance(site['site:service'], list):
                services.extend(site['site:service'])
            else:
                services.append(site['site:service'])

    return services

def get_sites(vo=None):
    providersID = [service['@id'] for service in _get_services(vo)]

    # Get provider metadata
    endpoints = {}
    for ID in providersID:
        data = appdb_call('/rest/1.0/va_providers/%s' % ID)
        site = data['virtualization:provider']
        if check_supported_VOs(site, vo):
            if ('provider:url' in site and site['@service_type'] == 'org.openstack.nova'):
                provider_name = site['provider:name']
                critical = ""
                if '@service_status' in site and site['@service_status'] == "CRITICAL":
                    critical = "CRITICAL"
                provider_endpoint_url = site['provider:url']
                url = urlparse(provider_endpoint_url)
                endpoints[provider_name] = ("%s://%s" % url[0:2], critical)

    return endpoints


def get_images(name, vo):
    oss = []
    for service in _get_services(vo):
        try:
            va_data = appdb_call('/rest/1.0/va_providers/%s' % service['@id'])
            if ('provider:url' in va_data['virtualization:provider'] and
                va_data['virtualization:provider']['@service_type'] == 'org.openstack.nova' and
                va_data['virtualization:provider']['provider:name'] == name):
                for os_tpl in va_data['virtualization:provider']['provider:image']:
                    try:
                        if '@voname' in os_tpl and vo in os_tpl['@voname'] and os_tpl['@archived'] == "false":
                            oss.append(os_tpl['@appcname'])
                    except:
                        continue
        except:
            continue

    return oss
