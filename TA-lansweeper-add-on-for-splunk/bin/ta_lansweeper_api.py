import splunk.rest as rest
import requests
import json
import sys
import time
import ta_lansweeper_utils as utils


class Lansweeper:
    def __init__(self, client_id, client_secret, access_token, refresh_token, proxy_settings, logger, session_key):
        """
        Initialization of the Lansweeper properties
        :param client_id: Client ID of the Lansweeper Account
        :param client_secret: Client Secret of the Lansweeper Account
        :param access_token: Access Token of the Lansweeper Account
        :param refresh_token: Refrest Token of the Lansweeper Account
        :param proxy_settings: Proxy settings configured by the user
        :param logger: Logger object
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.proxy_settings = proxy_settings
        self.session_key = session_key
        #for Lansweeper V1
        #self.graphql_url = 'https://api.lansweeper.com/api/integrations/graphql' 
        #For Lansweeper V2
        self.graphql_url = 'https://api.lansweeper.com/api/v2/graphql'
        self.auth_url = 'https://api.lansweeper.com/api/integrations/oauth/token'
        self.logger = logger
        self.logger.debug("Lansweeper class initialized.")

    def get_refresh_token(self):
        """
        Refreshes the access token once it is expired
        return status code of the API call and the response
        """
        self.logger.info('Refreshing the access token to get the fresh token')

        data = {"client_id": self.client_id, "client_secret": self.client_secret,
                "grant_type": "refresh_token", "refresh_token": self.refresh_token}
        headers = {'x-ls-integration-id': utils.HEADER_X_LS_INTEGRATION_ID,
                   'x-ls-integration-version': utils.get_conf_stanza(self.session_key, 'app', 'launcher')[0]["content"]["version"]}
        try:
            response = requests.post(
                url=self.auth_url, data=data, headers=headers, proxies=self.proxy_settings)
            # self.logger.info(response.text)
            if response.status_code == 200:
                response_json = response.json()
                return 200, response_json
            self.logger.debug("Non 200 status code while getting refresh token. status_code={}, response={}".format(response.status_code, response.text))
            return response.status_code, response
        except Exception as exception:
            self.logger.exception(
                'Error while refreshing the access token, error={}'.format(exception))
            sys.exit(1)

    def get_site_id(self, site_name):
        """
        Fetches the site_id of the site based on it's site name
        param site_name: Site name associated with the Lansweeper account
        return list of sites containing a list of dict of site_name:site_id
        """
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + self.access_token,
                   'x-ls-integration-id': utils.HEADER_X_LS_INTEGRATION_ID,
                   'x-ls-integration-version': utils.get_conf_stanza(self.session_key, 'app', 'launcher')[0]["content"]["version"]}
        query = """{
        me{
            username
            profiles{
            site{
                id
                name
            }
            }
        }
        }"""
        try:
            self.logger.debug("Request for site-id: query:{}".format(query))
            response = requests.post(self.graphql_url, json={
                                     'query': query}, headers=headers, proxies=self.proxy_settings)
            status_code = response.status_code
            self.logger.debug("Getting site-id: status_code:{}, response_text:{}".format(status_code, response.text))

            if status_code != 200:
                self.logger.warning('Error while fetching the site id for site={} status code= {}'.format(
                    site_name, status_code))
                return status_code, response
        except Exception as exception:
            self.logger.exception(
                'Error while fetching the site id for site={}, error={}'.format(site_name, exception))
            sys.exit(1)

        try:
            response_json = response.json()
            if site_name == '*':
                self.logger.debug("Site-id found in the response: {}".format(response_json['data']))
                return 200, response_json['data']['me']['profiles']

            sites = []
            for profile in response_json['data']['me']['profiles']:
                self.logger.debug("Multiple site-id found in the response: {}".format(response_json['data']))
                if profile['site']['name'] in site_name:
                    sites.append(
                        {profile['site']['name']: profile['site']['id']})
            return 200, sites
        except Exception as exception:
            self.logger.exception(
                'Error while parsing the response for the site id for site={}, error={}'.format(site_name, exception))
            sys.exit(1)

    def is_token_expired(self, status_code, response):
        """
        Checks if the access token is
        param status_code: status code of the API response
        param response: Response text of the API response
        return Refreshed access_token and the refresh_token in case the token is expired, and false otherwise
        """
        try:
            response = json.loads(response)
            self.logger.info('Checking if the access token is expired')

            if status_code == 400 or status_code == 401:
            #  and ((response.get('errors', [])[0].get('extensions', {}).get('code') == 'UNAUTHENTICATED') or (response.get('errors', [])[0].get('extensions', {}).get('extensions', {}).get('code') == 'UNAUTHENTICATED')):
                self.logger.info(
                    'Access token is expired. Calling the refresh token API')
                status, response = self.get_refresh_token()

                if status != 200:
                    self.logger.error(
                        'Error while refreshing the access token, status code={} response={}'.format(status, response.text))
                    return False

                self.logger.info('Successfully refreshed the access token.')
                # Do not uncomment below line
                # self.logger.debug("access_token: {}".format(response.get('access_token')))
                return {'access_token': response.get('access_token')}
            else:
                self.logger.warning("Non 400/401 status code. status_code={}, response={}".format(status_code, response))
        except Exception as exception:
            self.logger.exception(
                'Error while checking if the access token is expired, error={}'.format(exception))
        return False

    def get_asset_info(self, site_id, cursor, page):
        """
        Fetches the assets information for the sites
        param site_id: Site ID of the site for which the assets information needs to be collected
        param cursor: cursor from which point to collect the data
        param page: page parameter of the API query
        return True, cursor, asset_data in case of successful collection of the assets, and False, status_code and response otherwise
        """
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + self.access_token,
                   'x-ls-integration-id': utils.HEADER_X_LS_INTEGRATION_ID,
                   'x-ls-integration-version': utils.get_conf_stanza(self.session_key, 'app', 'launcher')[0]["content"]["version"]}
        query = """query getAssetResources{ 
            site(id: "%s"){
            assetResources(pagination:{ 
                limit: 500
                cursor: "%s"
                page: %s
            }, fields: [
            "assetCustom.stateName",
            "assetCustom.serialNumber",
            "assetCustom.model",
            "assetCustom.manufacturer",
            "assetBasicInfo.name",
            "assetBasicInfo.type",
            "assetBasicInfo.firstSeen",
            "assetBasicInfo.lastChanged",
            "assetBasicInfo.lastSeen",
            "assetBasicInfo.fqdn",
            "assetBasicInfo.ipAddress",
            "assetBasicInfo.mac",
            "assetBasicInfo.userDomain",
            "assetBasicInfo.userName",
            "assetBasicInfo.domain",
            "assetBasicInfo.lsAgentVersion",
            "assetBasicInfo.lastLsAgent",
            "assetBasicInfo.description",
            "assetGroups.name",
            "operatingSystem.buildNumber",
            "operatingSystem.buildRevNumber",
            "operatingSystem.version",
            "operatingSystem.totalVisibleMemorySize",
            "processors.type",
            "processors.name",
            "operatingSystem.caption",
            "ipLocation.ipLocation",
            "antiviruses.name",
            "antiviruses.enabled"
            ]){
            total
            items
                pagination {
                limit
                next
                page
                }
            }}
            }""" % (site_id, cursor, page)

        '''
        Lansweeper API V1
        -----------------
        Query : 

        query = """query getAssetResources{ 
            site(id: "{%s}"){
            assetResources(pagination:{ 
                limit: 100
                cursor: "%s"
                page: %s
            }, fields: [
            "assetCustom.stateName",
            "assetCustom.serialNumber",
            "assetCustom.model",
            "assetCustom.manufacturer",
            "asset.assetId",
            "asset.assetName",
            "asset.assetTypeName",
            "asset.assetGroups.groupName",
            "asset.buildNumber",
            "asset.version",
            "asset.osCodeId",
            "asset.firstSeen",
            "asset.lastChanged",
            "asset.lastSeen",
            "asset.fqdn",
            "asset.ipAddress",
            "asset.mac",
            "asset.userDomain",
            "asset.userName",
            "asset.assetDomain",
            "asset.memory",
            "asset.processor",
            "asset.serviceVersion",
            "asset.lsAgentVersion",
            "asset.lastLsAgent",
            "asset.description",
            "macOsInfo.systemVersion",
            "linuxSystem.osRelease",
            "operatingSystems.caption",
            "asset.ipLocation.ipLocation"
            ]){
            total
            items
                pagination {
                limit
                next
                page
                }
            }}
            }""" % (site_id, cursor, page)


        Information about fields of assets
        -----------------------------------
        Note - We are not fetching all the fields as of now as currently the API has limitation where maximum of 30 fields can be retrieved.

        "asset.assetName" - Name
        "asset.assetTypeName" - Type
        "asset.assetGroups.groupName" - Asset Group
        "asset.buildNumber" - Build number (Not sure, if this will going to be useful)
        "assetCustom.serialNumber" - Serial number
        "asset.version" - Version number (Not sure, if this will going to be useful)

        "asset.osCodeId" - Has some key, does not seem to be directly useful
        "asset.osCodeId" - Has version number for the OS

        "asset.firstSeen" - First Seen
        "asset.lastChanged" - Last changed
        "asset.lastSeen" - Last seen

        "asset.fqdn" - FQDN
        "asset.ipAddress" - IP address
        "asset.mac" - Mac address

        "asset.userDomain" - User domain
        "asset.userName" - Username

        "asset.countAntiVirus" - Discussed with Lansweeper team, if the database has null value in the field, the field will not be returned by the API

        "errors.errorText" - Not working for now, as discussed with Lansweeper team (Though, no errors)
        
        Below fields are not added due to fields limit but can be added as per the usecase
        "asset.lastTried"
        "assetCustom.dnsName"
        "assetCustom.lastPatched"
        ==================================================================

        Lansweeper API V2
        -----------------
        Query : 

        query = """query getAssetResources{ 
            site(id: "{%s}"){
            assetResources(pagination:{ 
                limit: 100
                cursor: "%s"
                page: %s
            }, fields: [
            "assetCustom.stateName",
            "assetCustom.serialNumber",
            "assetCustom.model",
            "assetCustom.manufacturer",
            "assetBasicInfo.name",
            "assetBasicInfo.type",
            "assetBasicInfo.firstSeen",
            "assetBasicInfo.lastChanged",
            "assetBasicInfo.lastSeen",
            "assetBasicInfo.fqdn",
            "assetBasicInfo.ipAddress",
            "assetBasicInfo.mac",
            "assetBasicInfo.userDomain",
            "assetBasicInfo.userName",
            "assetBasicInfo.domain",
            "assetBasicInfo.lsAgentVersion",
            "assetBasicInfo.lastLsAgent",
            "assetBasicInfo.description",
            "assetGroups.name",
            "operatingSystem.buildNumber",
            "operatingSystem.buildRevNumber",
            "operatingSystem.version",
            "operatingSystem.totalVisibleMemorySize",
            "processors.type",
            "processors.name",
            "operatingSystem.caption",
            "ipLocation.ipLocation"
            ]){
            total
            items
                pagination {
                limit
                next
                page
                }
            }}
            }""" % (site_id, cursor, page)

        Information about fields of assets
        -----------------------------------
        Note - We are not fetching all the fields as of now as currently the API has limitation where maximum of 30 fields can be retrieved.

        "assetCustom.stateName" -  Asset is active or not
        "assetCustom.serialNumber" - serialNumber
        "assetCustom.model" -  Model
        "assetCustom.manufacturer" - Manufacturer 
        "assetBasicInfo.name" - Name
        "assetBasicInfo.type" - Type
        "assetBasicInfo.firstSeen" - FirstSeen 
        "assetBasicInfo.lastChanged" - LastChanged
        "assetBasicInfo.lastSeen" - Lastseen
        "assetBasicInfo.fqdn" - FQDN
        "assetBasicInfo.ipAddress" - IPAddress
        "assetBasicInfo.mac" - Mac Address
        "assetBasicInfo.userDomain" - User Domain
        "assetBasicInfo.userName" - User Name
        "assetBasicInfo.domain" - Asset Domain
        "assetBasicInfo.lsAgentVersion" - Lansweeper Agent version
        "assetBasicInfo.lastLsAgent" - Lansweeper Agent Last Run
        "assetBasicInfo.description" - Asset Description
        "assetGroups.name" - Asset Group Name
        "operatingSystem.buildNumber" - BuildNumber
        "operatingSystem.buildRevNumber" - Not sure what it represents
        "operatingSystem.version" - Operating system version for Windows
        "operatingSystem.totalVisibleMemorySize" - Total Memory Size in KB
        "processors.type" - Processor Type
        "processors.name" - Processor Name
        "operatingSystem.caption" - Operating system name
        "ipLocation.ipLocation" - IPlocation 

        Changes from V1 to V2
        ---------------------

        "asset.serviceVersion",                 --> No details in v2
        "asset.assetId",                        --> Not exists            --> in V2 there is a field called id
        "macOsInfo.systemVersion",              --> Need to check again   --> "operatingSystem.version"
        "linuxSystem.osRelease",                --> Need to check again   --> "operatingSystem.caption"
        "asset.memory",                         --> Need to check again   --> "operatingSystem.totalVisibleMemorySize"
        "asset.processor",                      --> Need to check again   --> "processors{}.name"
        "asset.buildNumber",                    --> Need to check again   --> "operatingSystem.buildRevNumber"
        "asset.assetName",                      --> field changed to      --> "assetBasicInfo.name"    
        "asset.assetTypeName",                  --> field changed to      --> "assetBasicInfo.type"
        "asset.assetGroups.groupName",          --> field changed to      --> "assetGroups.name"
        "asset.version",                        --> field changed to      --> "operatingSystem.version"
        "asset.osCodeId",                       --> field changed to      --> "operatingSystem.buildNumber"
        "operatingSystems.caption",             --> field changed to      --> "operatingSystem.caption"
        "asset.ipLocation.ipLocation"           --> field changed to      --> "ipLocation.ipLocation"
        "asset.firstSeen",                      --> field changed to      --> "assetBasicInfo.firstSeen"
        "asset.lastChanged",                    --> field changed to      --> "assetBasicInfo.lastChanged"
        "asset.lastSeen",                       --> field changed to      --> "assetBasicInfo.lastSeen"
        "asset.fqdn",                           --> field changed to      --> "assetBasicInfo.fqdn"
        "asset.ipAddress",                      --> field changed to      --> "assetBasicInfo.ipAddress"
        "asset.mac",                            --> field changed to      --> "assetBasicInfo.mac"
        "asset.userDomain",                     --> field changed to      --> "assetBasicInfo.userDomain"
        "asset.userName",                       --> field changed to      --> "assetBasicInfo.userName"
        "asset.assetDomain",                    --> field changed to      --> "assetBasicInfo.assetDomain"
        "asset.lsAgentVersion",                 --> field changed to      --> "assetBasicInfo.lsAgentVersion"
        "asset.lastLsAgent",                    --> field changed to      --> "assetBasicInfo.lastLsAgent"
        "asset.description",                    --> field changed to      --> "assetBasicInfo.description"
        "assetCustom.stateName",                --> No change
        "assetCustom.serialNumber",             --> No change
        "assetCustom.model",                    --> No change
        "assetCustom.manufacturer",             --> No change
        '''

        try:
            self.logger.debug("Request for assets_info: query:{}".format(query))
            response = requests.post(self.graphql_url, json={
                                     'query': query}, headers=headers, proxies=self.proxy_settings)
            self.logger.debug('Fetching assets: Status={}'.format(response.status_code))
            # self.logger.debug('Fetching assets: Response={}'.format(response.text))
            if response.status_code != 200 or response.json().get('errors'):
                # save checkpoint
                return False, response.status_code, response
            assets = []
            response_json = response.json()
            items = response_json['data']['site']['assetResources']['items']
            cursor = response_json['data']['site']['assetResources']['pagination']['next']
            for item in items:
                asset = item
                if '_id' in asset:
                    asset['id'] = item['_id']
                    del asset['_id']
                else:
                    asset['id'] = item['key']
                for i in asset.get('antiviruses', []):
                # If antivirus item does not have enabled key then set it to unknown
                    if "enabled" not in i:
                        i["enabled"] = "unknown"
                assets.append(asset)
            return True, cursor, assets
        except Exception as exception:
            raise exception

    def export_data(self):
        """
        Lansweeper API does not allows to get more than 15 fields. To get more than 15 fields in a query exportFilteredAssets need to be used.
        This method is not being used, its just for information.
        """

        query1 = """mutation export {
        site(id: "<site-id>") {
            exportFilteredAssets {
            asset{
                asset.adUser.adUserKey
                "asset.osCodeId",
                "asset.version",
                "asset.windowsOperatingSystem.windowsOperatingSystemKey",
                "assetCustom.stateName",
                "asset.assetName",
                "asset.assetTypeName",
                "asset.firstSeen",
                "asset.fqdn",
                "asset.ipAddress",
                "asset.lastChanged",
                "asset.lastSeen",
                "asset.mac",
                "asset.osCodeKey",
                "asset.userDomain",
                "asset.userName",
                "asset.assetGroups.groupName",
                "assetCustom.manufacturer",
                "assetCustom.model",
                "assetCustom.serialNumber",
            }
            exportId
            }
        }
        }"""

        query2 = """{
        site(id: "<site-id>") {
            exportStatus(exportId: "600b0a731746b5f6aa60e25b") {
            exportId
            progress
            url
            }
        }
        }"""

        # Do query1 to post a request to export the data
        # make query2 to get status of export
        # Once status is completed/success than url will be returned in the response of query2
        # Making the request to the url returned, will provide the zip file, then by extracting the zip file and reading the file will allow access to data
