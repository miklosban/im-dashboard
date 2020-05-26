class Settings:
    def __init__(self, config):
        self.toscaDir = config['TOSCA_TEMPLATES_DIR'] + "/"
        self.toscaParamsDir = config.get('TOSCA_PARAMETERS_DIR') + "/"
        self.imUrl = config['IM_URL']
        self.oidcUrl = config['OIDC_BASE_URL']
        self.tempSlamUrl = config.get('SLAM_URL') if config.get('SLAM_URL') else ""
        self.imConf = {'im_url': config.get('IM_URL')}
        self.external_links = config.get('EXTERNAL_LINKS') if config.get('EXTERNAL_LINKS') else []
        self.oidcGroups = config.get('OIDC_GROUP_MEMBERSHIP')
        self.cred_db_url = config.get('CRED_DB_URL')
        self.analytics_tag = config.get('ANALYTICS_TAG')
        self.static_sites = config.get('STATIC_SITES')
        self.static_sites_url = config.get('STATIC_SITES_URL')
