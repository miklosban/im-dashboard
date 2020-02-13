from app import app

toscaDir = app.config['TOSCA_TEMPLATES_DIR'] + "/"
toscaParamsDir = app.config.get('TOSCA_PARAMETERS_DIR')
imUrl = app.config['IM_URL']

oidcUrl = app.config['OIDC_BASE_URL']

tempSlamUrl = app.config.get('SLAM_URL') if app.config.get('SLAM_URL') else "" 

imConf = {
  'im_url': app.config.get('IM_URL'),
}

external_links = app.config.get('EXTERNAL_LINKS') if app.config.get('EXTERNAL_LINKS') else []

oidcGroups = app.config.get('OIDC_GROUP_MEMBERSHIP')


cred_db_url = app.config.get('CRED_DB_URL')