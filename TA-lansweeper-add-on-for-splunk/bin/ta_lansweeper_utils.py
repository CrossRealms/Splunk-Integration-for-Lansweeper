import splunk.rest as rest
import time
import copy
import os
import splunk
import json
import datetime
import os.path as op
import requests as rq
from solnlib import conf_manager
from splunklib import modularinput as smi
from solnlib.modular_input import checkpointer
import sys

APP_NAME = __file__.split(op.sep)[-3]

def get_account_details(session_key, account_name, logger):
    """
    This function retrieves account details from addon configuration file.
    :param session_key: session key for particular modular input.
    :param account_name: account name configured in the addon.
    :param logger: provides logger of current input.
    :return : account details in form of a dictionary.    
    """
    try:
        cfm = conf_manager.ConfManager(
            session_key, APP_NAME, realm='__REST_CREDENTIAL__#{}#configs/conf-ta_lansweeper_add_on_for_splunk_account'.format(APP_NAME))
        account_conf_file = cfm.get_conf('ta_lansweeper_add_on_for_splunk_account')
    except Exception as exception:
        logger.error("Failed to fetch account details from configuration, error={}".format(exception))
        sys.exit(1)

    logger.info("Fetched configured account details")
    return {
        "client_id": account_conf_file.get(account_name).get('client_id'),
        "client_secret": account_conf_file.get(account_name).get('client_secret'),
        "access_token": account_conf_file.get(account_name).get('access_token'),
        "refresh_token": account_conf_file.get(account_name).get('refresh_token')
    }

def update_access_token(access_token, refresh_token, client_secret, session_key, stanza_name):
    """
    Updates the latest access_token and refresh token in the ta_lansweeper_add_on_for_splunk_account.conf
    :param access_token: Access Token of the Lansweeper Account
    :param refresh_token: Refresh Token of the Lansweeper Account
    :param client_secret: Client Secret of the Lansweeper Account
    :param session_key: Splunk session key
    :param stanza_name: Stanza name of the account to be updated
    :return : True on successfully updating the account configurations
    """
    cfm = conf_manager.ConfManager(
            session_key, APP_NAME, realm='__REST_CREDENTIAL__#{}#configs/conf-ta_lansweeper_add_on_for_splunk_account'.format(APP_NAME))
    conf = cfm.get_conf('ta_lansweeper_add_on_for_splunk_account')
    conf.update(stanza_name,
                {'access_token': access_token, 'client_secret': client_secret, 'refresh_token': refresh_token},
                ['access_token', 'client_secret', 'refresh_token'])
    return True

def get_proxy_settings(session_key, logger):
    """
    This function fetches proxy settings
    :param session_key: session key for particular modular input.
    :param logger: provides logger of current input.
    :return : proxy settings
    """

    try:
        settings_cfm = conf_manager.ConfManager(
            session_key,
            APP_NAME,
            realm="__REST_CREDENTIAL__#{}#configs/conf-ta_lansweeper_add_on_for_splunk_settings".format(APP_NAME))
        lansweeper_settings_conf = settings_cfm.get_conf(
            "ta_lansweeper_add_on_for_splunk_settings").get_all()
    except Exception as exception:
        logger.error("Failed to fetch proxy details from configuration. {}".format(exception))
        sys.exit(1)

    proxy_settings = None
    proxy_stanza = {}
    for key, value in lansweeper_settings_conf["proxy"].items():
        proxy_stanza[key] = value

    if int(proxy_stanza.get("proxy_enabled", 0)) == 0:
        return proxy_settings
    proxy_port = proxy_stanza.get('proxy_port')
    proxy_url = proxy_stanza.get('proxy_url')
    proxy_type = proxy_stanza.get('proxy_type')
    proxy_username = proxy_stanza.get('proxy_username', '')
    proxy_password = proxy_stanza.get('proxy_password', '')

    if proxy_username and proxy_password:
        proxy_username = rq.compat.quote_plus(proxy_username)
        proxy_password = rq.compat.quote_plus(proxy_password)
        proxy_uri = "%s://%s:%s@%s:%s" % (proxy_type, proxy_username,
                                          proxy_password, proxy_url, proxy_port)
    else:
        proxy_uri = "%s://%s:%s" % (proxy_type, proxy_url, proxy_port)

    proxy_settings = {
        "http": proxy_uri,
        "https": proxy_uri
    }
    logger.info("Fetched configured proxy details.")
    return proxy_settings

def get_log_level(session_key, logger):
    """
    This function returns the log level for the addon from configuration file.
    :param session_key: session key for particular modular input.
    :return : log level configured in addon.
    """
    try:
        settings_cfm = conf_manager.ConfManager(
            session_key,
            APP_NAME,
            realm="__REST_CREDENTIAL__#{}#configs/conf-ta_lansweeper_add_on_for_splunk_settings".format(APP_NAME))

        logging_details = settings_cfm.get_conf(
            "ta_lansweeper_add_on_for_splunk_settings").get("logging")

        log_level = logging_details.get('loglevel') if (
            logging_details.get('loglevel')) else 'INFO'
        return log_level

    except Exception as exception:
        logger.error(
            "Failed to fetch the log details from the configuration taking INFO as default level, error={}".format(exception))
        return 'INFO'


def write_event(asset_data, site_name, ew, index, logger):
    """
    This function write events to the Splunk
    :param asset_data: list of assets
    :param site_name: Site name associated with the assets
    :param ew: Event Writer object
    :param index: Index on which data will be written
    :param logger: Logger object
    """

    sourcetype = 'lansweeper:asset:v2'
    try:
        logger.info('Writting assets data to Splunk for site={} asset_count={}'.format(site_name, len(asset_data)))
        for asset in asset_data:
            asset['site_name'] = site_name
            event = smi.Event(
                data=json.dumps(asset),
                sourcetype=sourcetype,
                index=index
            )
            ew.write_event(event)
        logger.info('Successfully indexed the asset data')
    except Exception as exception:
        logger.error("Error writing event to Splunk, error={}".format(exception))


def checkpoint_handler(checkpoint_name, session_key, logger):
    """
    This function handles checkpoint. This is not being used at this point but we will need this for future enhancements.
    :param checkpoint_name: represents checkpoint file name.
    :param session_key: session key for particular modular input.
    :param logger: provides logger of current input.
    :return : checkpoint object and start date of the query.
    """

    try:
        ck = checkpointer.KVStoreCheckpointer(
            checkpoint_name, session_key, APP_NAME)
        checkpoint_marker = ck.get(checkpoint_name)
        return ck, query_start_date
    except Exception as exception:
        logger.error("Error occurred while fetching checkpoint, error={}".format(exception))
        sys.exit(1)


def get_conf_stanza(session_key, conf_file, stanza):
    _, serverContent = rest.simpleRequest(
        "/servicesNS/nobody/{}/configs/conf-{}/{}?output_mode=json".format(APP_NAME, conf_file, stanza), 
        sessionKey=session_key
    )
    data = json.loads(serverContent)['entry']
    return data
