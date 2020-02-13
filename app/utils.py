import json, yaml, requests, os, io, ast, time
from flask import flash
from app import appdb, cred
from fnmatch import fnmatch
from hashlib import md5
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

SITE_LIST = {}
LAST_UPDATE = 0
CACHE_DELAY = 3600

def getUserAuthData(access_token):
    global SITE_LIST
    global LAST_UPDATE
    global CACHE_DELAY

    res = "type = InfrastructureManager; token = %s" % access_token
    now = int(time.time())
    if now - LAST_UPDATE > CACHE_DELAY:
        LAST_UPDATE = now
        SITE_LIST = appdb.get_sites()

    if not SITE_LIST:
        flash("Error retrieving site list", 'warning')

    cont = 0
    for site_name, (site_url, _) in SITE_LIST.items():
        cont += 1
        creds = cred.get_cred(site_name)
        res += "\\nid = ost%s; type = OpenStack; username = egi.eu; tenant = openid; auth_version = 3.x_oidc_access_token;" % cont
        res += " host = %s; password = '%s'" % (site_url, access_token)
        if creds and "project" in creds and creds["project"]:
            res += "; domain = %s" % creds["project"]

    return res

def format_json_radl(vminfo):
    res = {}
    for elem in vminfo:
        if elem["class"] == "system":
            for field, value in elem.items():
                if field not in ["class", "id"]:
                    if field.endswith("_min"):
                        field = field[:-4]
                    res[field] = value
    return res

def to_pretty_json(value):
    return json.dumps(value, sort_keys=True,
                      indent=4, separators=(',', ': '))

def avatar(email, size):
  digest = md5(email.lower().encode('utf-8')).hexdigest()
  return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)


def getIMVersion(im_url):
    url = im_url +  "/version"
    response = requests.get(url)
    return response.text


def loadToscaTemplates(directory):

   toscaTemplates = []
   for path, subdirs, files in os.walk(directory):
      for name in files:
           if fnmatch(name, "*.yml") or fnmatch(name, "*.yaml"):
               # skip hidden files
               if name[0] != '.':
                  toscaTemplates.append( os.path.relpath(os.path.join(path, name), directory ))

   return toscaTemplates


def extractToscaInfo(toscaDir, tosca_pars_dir, toscaTemplates):
    toscaInfo = {}
    for tosca in toscaTemplates:
        with io.open( toscaDir + tosca) as stream:
           template = yaml.full_load(stream)
    
           toscaInfo[tosca] = {
                                "valid": True,
                                "description": "TOSCA Template",
                                "metadata": {
                                    "icon": "https://cdn4.iconfinder.com/data/icons/mosaicon-04/512/websettings-512.png"
                                },
                                "enable_config_form": False,
                                "inputs": {},
                                "tabs": {}
                              }
    
           if 'topology_template' not in template:
               toscaInfo[tosca]["valid"] = False
    
           else:
    
                if 'description' in template:
                    toscaInfo[tosca]["description"] = template['description']
    
                if 'metadata' in template and template['metadata'] is not None:
                   for k,v in template['metadata'].items():
                       toscaInfo[tosca]["metadata"][k] = v
    
                if 'inputs' in template['topology_template']:
                   toscaInfo[tosca]['inputs'] = template['topology_template']['inputs']
    
                ## add parameters code here
                tabs = {}
                if tosca_pars_dir:
                    tosca_pars_path = tosca_pars_dir + "/"  # this has to be reassigned here because is local.
                    for fpath, subs, fnames in os.walk(tosca_pars_path):
                        for fname in fnames:
                            if fnmatch(fname, os.path.splitext(tosca)[0] + '.parameters.yml') or \
                                    fnmatch(fname, os.path.splitext(tosca)[0] + '.parameters.yaml'):
                                # skip hidden files
                                if fname[0] != '.':
                                    tosca_pars_file = os.path.join(fpath, fname)
                                    with io.open(tosca_pars_file) as pars_file:
                                        toscaInfo[tosca]['enable_config_form'] = True
                                        pars_data = yaml.full_load(pars_file)
                                        toscaInfo[tosca]['inputs'] = pars_data["inputs"]
                                        if "tabs" in pars_data:
                                            toscaInfo[tosca]['tabs'] = pars_data["tabs"]

    return toscaInfo

def exchange_token_with_audience(oidc_url, client_id, client_secret, oidc_token, audience):

    payload_string = '{ "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange", "audience": "'+audience+'", "subject_token": "'+oidc_token+'", "scope": "openid profile" }'
    
    # Convert string payload to dictionary
    payload =  ast.literal_eval(payload_string)
    
    oidc_response = requests.post(oidc_url + "/token", data=payload, auth=(client_id, client_secret), verify=False)
    
    if not oidc_response.ok:
        raise Exception("Error exchanging token: {} - {}".format(oidc_response.status_code, oidc_response.text) )
    
    deserialized_oidc_response = json.loads(oidc_response.text)
    
    return deserialized_oidc_response['access_token']
