# Lansweeper Add-on for Splunk

### Download from Splunkbase
The Splunkbase link is not available yet.


OVERVIEW
--------
The Lansweeper Add-on for Splunk is an Splunk App that allows user to collect information (assets) from Lansweeper Cloud into Splunk. It consist of python scripts to collect the data along side configuration pages in UI to configure the data collection.

Use `Lansweeper App for Splunk` to visualize the data on the dashboards.


* Author - CrossRealms International Inc.
* Version - 1.0.1
* Build - 1
* Creates Index - False
* Compatible with:
   * Splunk Enterprise version: 8.1, 8.0
   * OS: Platform Independent
   * Browser: Google Chrome, Mozilla Firefox, Safari



TOPOLOGY AND SETTING UP SPLUNK ENVIRONMENT
------------------------------------------
This app can be set up in two ways: 
  1. Standalone Mode: 
     * Install the `Lansweeper Add-on for Splunk`.
  2. Distributed Mode: 
     * Install the `Lansweeper Add-on for Splunk` on the search head. The Add-on configuration is not required on the search head.
     * Install the `Lansweeper Add-on for Splunk` on the heavy forwarder. Configure the Add-on to collect the required information from the Lansweeper on the heavy forwarder.
     * The Add-on do not support universal forwarder as it requires python modular inputs to collect the data from Lansweeper.
     * The Add-on do not require on the Indexer.


DEPENDENCIES
------------------------------------------------------------
* The Add-on does not have any external dependencies.


INSTALLATION
------------------------------------------------------------
The Lansweeper Add-on needs to be installed on the Search Head and heavy forwarder.  

* From the Splunk Web home screen, click the gear icon next to Apps. 
* Click on `Browse more apps`.
* Search for `Lansweeper Add-on for Splunk` and click Install. 
* Restart Splunk if you are prompted.


DATA COLLECTION & CONFIGURATION
------------------------------------------------------------
### Lansweeper API Documentation ###
* https://www.lansweeper.com/kb-category/api/index.html


### Configuration Required on Lansweeper Cloud ###
* Reference - https://www.lansweeper.com/kb-category/api/auth.html


### Configure Account ###
* Navigate to `Lansweeper Add-on for Splunk` > `Configuration` > `Account` on Splunk UI.
* Click on `Add`.
* Add below parameters:

| Parameter | Description |
| --- | --- |
| Account name | Any unique name to distinguish this client-id and secret from other in case of multiple accounts configured in the Add-on. |
| Client Id | Client id received from Lansweeper. |
| Client Secret | Client secret received from Lansweeper. |
| Redirect url | This field will be auto-populated. Do not make any changes. |

* Click on `Add`.
* If you see time-out issue while saving the account, retry. The time-out is set to 30 seconds.


### Configure Data Input ###
* Navigate to `Lansweeper Add-on for Splunk` > `Input` on Splunk UI.
* Click on `Create New Input`.
* Add below parameters:

| Parameter | Description |
| --- | --- |
| Name | An unique name for the Input. |
| Interval | Interval in seconds, at which the Add-on should collect latest data from Lansweeper API. Ideal value is between 3600 (1 hour) to 14400 (4 hour). |
| Index | Select/Type the index name in which lansweeper data will be stored in Splunk. The index name by default supported by `Lansweeper App for Splunk` is `lansweeper`. |
| Account Name | Select the account name configured in the Configuration page, which you want to use for data collection. |
| Site | Select the site names from Lansweeper for which you want to collect the data. |

* Click on `Save`.


UNINSTALL APP
-------------
To uninstall app, user can follow below steps:
* SSH to the Splunk instance.
* Go to folder apps($SPLUNK_HOME/etc/apps).
* Remove the `TA-lansweeper-add-on-for-splunk` folder from `apps` directory.
* Restart Splunk.


RELEASE NOTES
-------------
Version 1.0.1 (Feb 2021)
* Resolved App-Inspect Failure (nested App present in the package).


Version 1.0.0 (Jan 2021)
* Created Add-on by UCC Splunk-Python library.
* Added Add-on configuration pages.



OPEN SOURCE COMPONENTS AND LICENSES
------------------------------
* The Add-on is built by UCC framework (https://pypi.org/project/splunk-add-on-ucc-framework/).


CONTRIBUTORS
------------
* Vatsal Jagani
* Usama Houlila
* Preston Carter


SUPPORT
-------
* Contact - CrossRealms International Inc.
  * US: +1-312-2784445
* License Agreement - https://d38o4gzaohghws.cloudfront.net/static/misc/eula.html
* Copyright - Copyright CrossRealms Internationals, 2021
