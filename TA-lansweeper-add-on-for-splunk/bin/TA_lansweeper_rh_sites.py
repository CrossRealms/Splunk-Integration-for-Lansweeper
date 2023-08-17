import import_declare_test
import json
import logging
import sys

import splunk.admin as admin
import splunk.rest as rest
from splunktaucclib.rest_handler.error import RestError

from logger_manager import setup_logging
from ta_lansweeper_utils import get_account_details, get_log_level, get_proxy_settings, update_access_token
from ta_lansweeper_api import Lansweeper

logger = setup_logging("rh_sites")
logger.setLevel(logging.INFO)


class LansweeperSites(admin.MConfigHandler):
    """REST Endpoint of getting token by OAuth2 in Splunk Add-on UI Framework.
    This class is used to connect with server endpoints test connectivity with server.
    """

    def setup(self):
        """
        Sets the input arguments
        :return:
        """
        try:
            if self.requestedAction == admin.ACTION_LIST:
                for arg in ['account_name']:
                    self.supportedArgs.addReqArg(arg)
            return
        except Exception as e:
            logger.error(str(e))

    def handleList(self, conf_info):
        """
        Handling the input request and populating the different security policies
        :param conf_info: The conf_info is used to pass the data from python handler to the javascript
        :return:
        """
        session_key = self.getSessionKey()
        log_level = get_log_level(session_key, logger)
        logger.setLevel(log_level)

        try:
            account_name = self.callerArgs.data["account_name"][0]
            account_details = get_account_details(
                session_key, account_name, logger)
            proxy_settings = get_proxy_settings(session_key, logger)
            # logger.info("Account details={}".format(account_details))

            client_id = account_details.get('client_id')
            client_secret = account_details.get('client_secret')
            access_token = account_details.get('access_token')
            refresh_token = account_details.get('refresh_token')
            site_name = '*'
            site_id = []

            lansweeper = Lansweeper(client_id=client_id, client_secret=client_secret, access_token=access_token,
                                    refresh_token=refresh_token, proxy_settings=proxy_settings, logger=logger)
            try:
                status_code, response = lansweeper.get_site_id(site_name)
                if status_code != 200:
                    is_expired_response = lansweeper.is_token_expired(
                        status_code, response.text)
                    if is_expired_response:
                        lansweeper.access_token = is_expired_response['access_token']
                        lansweeper.refresh_token = is_expired_response['refresh_token']
                        # Updating the access token and refresh token in the conf files
                        try:
                            update_access_token(access_token=is_expired_response['access_token'], refresh_token=is_expired_response[
                                                'refresh_token'], client_secret=client_secret, session_key=session_key, stanza_name=account_name)
                            logger.info(
                                'Successfully updated the new access token and refresh token in the conf file')
                        except Exception as exception:
                            logger.warning(
                                'Error while updating the access token and refresh token in the conf file, error={}'.format(exception))

                        status_code, response = lansweeper.get_site_id(
                            site_name)
                        if status_code != 200:
                            logger.error('Error while fetching the site id for site={}, status code={} response={}'.format(
                                site_name, status_code, response))
                            raise RestError(
                                409, "Error while fetching the sites for the account. Please enter the site names manually")
                        else:
                            logger.info(
                                'Successfully fetch the site code for site={}'.format(site_name))
                            site_id = response
                    else:
                        logger.error('Error while fetching the site id for site={}, status code={} response={}'.format(
                            site_name, status_code, response))
                        raise RestError(
                            409, "Error while fetching the sites for the account. Please enter the site names manually")
                else:
                    logger.info(
                        'Successfully fetch the site code for site={}'.format(site_name))
                    site_id = response
            except Exception as exception:
                logger.exception(
                    'Error while fetching the site id for site={}'.format(site_name))
                raise RestError(
                    409, "Error while fetching the sites for the account. Please enter the site names manually")

            sites = []
            for profile in site_id:
                conf_info[profile['site']['name']].append(
                    'value', profile['site']['id'])

            logger.info('Returning sites={}'.format(sites))
        except Exception as e:
            logger.exception(
                "Error while getting the sites, error={}".format(e))
            raise RestError(
                409, "Error while fetching the sites for the account. Please enter the site names manually")


if __name__ == "__main__":
    admin.init(LansweeperSites, admin.CONTEXT_APP_AND_USER)
