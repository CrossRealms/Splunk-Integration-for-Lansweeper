# Lansweeper App for Splunk

### Download from Splunkbase
The Splunkbase link is not available yet.


OVERVIEW
--------
The Lansweeper App for Splunk is an Splunk App that visualize the data collected by Lansweeper like assets, softwares and other information related to assets. It contains useful dashboards. 

The App is using data collected by the `Lansweeper Add-on for Splunk`.


* Author - CrossRealms International Inc.
* Version - 1.0.0
* Build - 1
* Creates Index - False
* Uses KV Store - True. This App uses Splunk KV Store for storing some of the lookup files
* App has some savedsearches to fill lookups
* Compatible with:
   * Splunk Enterprise version: 8.1, 8.0
   * OS: Platform Independent
   * Browser: Google Chrome, Mozilla Firefox, Safari



TOPOLOGY AND SETTING UP SPLUNK ENVIRONMENT
------------------------------------------
This app can be set up in two ways: 
  1. Standalone Mode: 
     * Install the `Lansweeper App for Splunk`.
  2. Distributed Mode: 
     * Install the `Lansweeper App for Splunk` on the search head.
     * App do not require on the Indexer or on the forwarder.


DEPENDENCIES
------------------------------------------------------------
* The App does not have any external dependencies.


INSTALLATION
------------------------------------------------------------
The Lansweeper App needs to be installed only on the Search Head.  

* From the Splunk Web home screen, click the gear icon next to Apps.
* Click on `Browse more apps`.
* Search for `Lansweeper App for Splunk` and click Install. 
* Restart Splunk if you are prompted.


DATA COLLECTION & CONFIGURATION
------------------------------------------------------------
### Update Index Macro Configuration

By default, the index name is `lansweeper` in the App. But if you have change the index of data from the `Lansweeper Add-on for Splunk` then you have to update the macro definition for macro name `lansweeper_data`.
1. Log in as administrator and select Settings > Advance search > Search Macros. 
2. Select `Lansweeper App for Splunk (lansweeper_app_for_splunk)` in the App drop-down. A list of available macros is displayed. 
3. Select and edit `lansweeper_data` macro and change the definition of macros with new index name.


UNINSTALL APP
-------------
To uninstall app, user can follow below steps:
* SSH to the Splunk instance.
* Go to folder apps($SPLUNK_HOME/etc/apps).
* Remove the `lansweeper_app_for_splunk` folder from `apps` directory.
* Restart Splunk.


RELEASE NOTES
-------------
Version 1.0.0 (Feb 2021)
* Created App Overview dashboard.
* Added Details/Forensics dashboard for investigating security issues.
* Added multiple security alerts with below categories.
  * Categories: Ransomware, Active Directory & Windows, Office 365, Endpoint Compromise, Network Compromise, Credential Compromise, Sophos and Palo Alto Firewall.
* Added below reports:
  * Active Directory & Windows
  * O365
  * Network Reports
  * Palo Alto
  * Globally Detected Malicious IPs
  * Sophos
  * VPN
  * Authentication
* Added App configuration dashboard.
* Added HoneyDB based blocked IP list and used that list to identify bad traffic.



SAVED-SEARCHES
---------------
* TODO - write list of saved-searches present in the App here
* 


LOOKUPS
-------
* TODO - write list of lookups present in the App here
* 



OPEN SOURCE COMPONENTS AND LICENSES
------------------------------
* N/A


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
