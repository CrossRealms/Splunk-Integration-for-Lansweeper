import import_declare_test
import sys
import json
from solnlib import log
from ta_lansweeper_utils import get_account_details, get_log_level, get_proxy_settings, write_event, update_access_token
from ta_lansweeper_api import Lansweeper

from splunklib import modularinput as smi

class LANSWEEPER_INPUT(smi.Script):

    def __init__(self):
        super(LANSWEEPER_INPUT, self).__init__()

    def get_scheme(self):
        scheme = smi.Scheme('lansweeper_input')
        scheme.description = 'Lansweeper Input'
        scheme.use_external_validation = True
        scheme.streaming_mode_xml = True
        scheme.use_single_instance = False

        scheme.add_argument(
            smi.Argument(
                'name',
                title='Name',
                description='Name',
                required_on_create=True
            )
        )
        
        scheme.add_argument(
            smi.Argument(
                'site',
                required_on_create=True,
            )
        )
        
        scheme.add_argument(
            smi.Argument(
                'account_name',
                required_on_create=True,
            )
        )
        
        return scheme

    def validate_input(self, definition):
        return

    def stream_events(self, inputs, ew):
        meta_configs = self._input_definition.metadata
        session_key = meta_configs['session_key']

        input_items = {}
        input_name = list(inputs.inputs.keys())[0]
        input_items = inputs.inputs[input_name]

        # Generate logger with input name
        _, input_name = (input_name.split('//', 2))
        logger = log.Logs().get_logger('ta_lansweeper_input_{}'.format(input_name))
        log_level = get_log_level(session_key, logger)
        logger.setLevel(log_level)

        logger.info("Modular input invoked.")

        account_name = input_items.get('account_name')
        account_details = get_account_details(session_key, account_name, logger)
        proxy_settings = get_proxy_settings(session_key, logger)
        client_id = account_details.get('client_id')
        client_secret = account_details.get('client_secret')
        access_token = account_details.get('access_token')
        refresh_token = account_details.get('refresh_token')
        site_name = input_items.get('site').split(',')
        logger.info("Site names: " + str(site_name))
        index = input_items.get('index')
        sites = []

        # Note - Do not uncomment below line in the production
        # logger.info('Access token={}, ||| Refresh token={}'.format(access_token, refresh_token))

        lansweeper = Lansweeper(client_id=client_id, client_secret=client_secret, access_token=access_token, refresh_token=refresh_token, proxy_settings=proxy_settings, logger=logger)
        #Get site id
        # logger.info('Refresh token={}'.format(lansweeper.refresh_token))
        try:
            status_code, response = lansweeper.get_site_id(site_name)
            if status_code != 200:
                is_expired_response = lansweeper.is_token_expired(status_code, response.text)
                if is_expired_response:
                    lansweeper.access_token = is_expired_response['access_token']
                    # Updating the access token and refresh token in the conf files
                    try:
                        update_access_token(access_token=is_expired_response['access_token'], refresh_token=refresh_token, client_secret=client_secret, session_key=session_key, stanza_name=account_name)
                        logger.info('Successfully updated the new access token and refresh token in the conf file')
                    except Exception as exception:
                        logger.warning('Error while updating the access token and refresh token in the conf file, error={}'.format(exception))
                    
                    status_code, response = lansweeper.get_site_id(site_name)
                    if status_code != 200:
                        logger.error('Error while fetching the site id for site={}, status code={} response={}'.format(site_name, status_code, response))
                        sys.exit(1)
                    else:
                        sites = response
                else:
                    logger.error('Error while fetching the site id for site={}, status code={} response={}'.format(site_name, status_code, response))
                    sys.exit(1)
            else:
                logger.info('Successfully fetch the site code for site={}'.format(site_name))
                sites = response
        except Exception as exception:
            logger.exception('Error while fetching the site id for site={}'.format(site_name))
            sys.exit(1)
        
        logger.info("Site id: {}".format(sites))

        #Get asset information for all the sites
        logger.info('Starting to fetch assets data')
        for site in sites:
            try:
                cursor = ''
                page = 'FIRST'
                is_data = True
                site_name = list(site.keys())[0]
                site_id = site[site_name]
                while is_data:
                    status, response_code, response = lansweeper.get_asset_info(site_id, cursor, page)
                    if not status:
                        is_expired_response = lansweeper.is_token_expired(response_code, response.text)
                        if is_expired_response:
                            lansweeper.access_token = is_expired_response['access_token']
                            # Updating the access token and refresh token in the conf files
                            try:
                                update_access_token(access_token=is_expired_response['access_token'], refresh_token=refresh_token, client_secret=client_secret, session_key=session_key, stanza_name=account_name)
                                logger.info('Successfully updated the new access token and refresh token in the conf file')
                            except Exception as exception:
                                logger.warning('Error while updating the access token and refresh token in the conf file, error={}'.format(exception))
                            
                            continue

                        else:
                            logger.error('Error while fetching the assets for site={}, status code={} response={}'.format(site_name, response_code, response.text))
                            break
                    else:
                        logger.info('Successfully fetch the assets for site={} page={}'.format(site_name, page))
                        cursor, asset_data = response_code, response
                    write_event(asset_data, site_name, ew, index, logger)
                    is_data = cursor
                    page = 'NEXT'
                    logger.info('Fetching the next group of assets for site={} cursor={}'.format(site_name, cursor))
            except Exception as exception:
                logger.exception('Error while fetching the assets for site={}'.format(site_name))
            
        logger.info('Completed the data collection for the input')

if __name__ == '__main__':
    exit_code = LANSWEEPER_INPUT().run(sys.argv)
    sys.exit(exit_code)