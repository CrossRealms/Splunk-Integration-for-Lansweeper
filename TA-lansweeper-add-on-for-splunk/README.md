# Lansweeper Add-on for Splunk

### Download from Splunkbase
https://splunkbase.splunk.com/app/5418/


OVERVIEW
--------
The Lansweeper Add-on for Splunk is a Splunk App that allows users to collect information (assets) from Lansweeper (Cloud or On-prem (On-prem support added from version 1.1.0)) into Splunk. It consists of python scripts to collect the data alongside configuration pages in UI to configure the data collection.

Use the <a href="https://splunkbase.splunk.com/app/5419/">Lansweeper App for Splunk</a> to visualize the data on the dashboards.

* Author - CrossRealms International Inc.
* Creates Index - False
* Compatible with:
   * Splunk Enterprise version: 9.1, 9.0, 8.2
   * OS: Platform Independent
   * Browser: Google Chrome, Mozilla Firefox, Safari

## What's inside the Add-on

* No of XML Dashboards: **3**
* No of Custom Inputs: **1**



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
* The Add-on does not have any external dependencies if you want to collect data from Lansweeper cloud.
* If you wish to collect data from on-prem database, you need <a href="https://splunkbase.splunk.com/app/2686/">Splunk DB Connect</a> to collect data. See `DATA COLLECTION & CONFIGURATION FROM ON-PREM` for more information about on-prem data collection.


INSTALLATION
------------------------------------------------------------
The Lansweeper Add-on needs to be installed on the Search Head and heavy forwarder.  

* From the Splunk Web home screen, click the gear icon next to Apps. 
* Click on `Browse more apps`.
* Search for `Lansweeper Add-on for Splunk` and click Install. 
* Restart Splunk if you are prompted.


DATA COLLECTION & CONFIGURATION FROM CLOUD
------------------------------------------------------------
### Lansweeper API Documentation ###
* https://docs.lansweeper.com/docs/api/intro-to-graphql


### Configuration Required on Lansweeper Cloud ###
* Reference - https://docs.lansweeper.com/docs/api/authenticate


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



DATA COLLECTION & CONFIGURATION FROM ON-PREM
------------------------------------------------------------
### Lansweeper Database Documentation ###
* To see Lansweeper database structure and more information refer to Lansweeper on-prem UI.


### Configuration Required for Lansweeper Database ###
1. To connect Splunk with on-prem Lansweeper database, the Lansweeper database need to be migrated to some that supports remote connection.
    * Default database for Lansweeper is LocalDB which does not support remote connection.
    * Refer to Lansweeper Documentation to migrate the existing database.
      * To migrate LocalDB to SQL Server - https://www.lansweeper.com/knowledgebase/localdb-to-sql-server/
2. Create a new user to Lansweeper database for Splunk to use. Use a separate read-only user for security reasons.
3. Make sure you have following things about the database handy for Splunk connection:
    * Lansweeper database server IP address
    * Lansweeper database remote connection port (Make sure if the Splunk Heavy forwarder is on remote machine, firewall allows this connection.)
    * Username and Password for the the user that you just created in above step no. 2.
4. Contact to Lansweeper administrator for above discussion.


### Configure Splunk DB Connect for Data Collection ###
1. Make sure you install `Lansweeper Add-on for Splunk` on the server where you are configuring `Splunk DB Connect`.
    * You can download Splunk DB Connect App from <a href="https://splunkbase.splunk.com/app/2686/">here</a>.
2. Add required driver to Splunk DB Connect App as per the lansweeper Database.
    * You can follow this <a href="https://docs.splunk.com/Documentation/DBX/3.4.2/DeployDBX/ConfigureDBConnectsettings?ref=hk#Drivers_tab">link</a>.
4. Go to `Splunk DB Connect` on Splunk Heavy Forwarder.
5. Go to `Configuration` on the navigation of the DB Connect App.
6. Go to identities and create a new identity.
    * Identity Name - Unique name of identity
    * Username - Username for the Lansweeper database
    * Password - Password for the Lansweeper database
7. Go to `Configuration > Connections` and create a new connection.
    * Connection Name - Unique name for the database connection
    * Identify - Select the identity created in previous step.
    * Connection Type - Select appropriate database connection type
    * Timezone - Timezone of database server
    * Host - Hostname of IP Address of database server
    * Port - Port number of database connection (Refer to `Configuration Required for Lansweeper Database` section above.)
    * Default Database - Use `lansweeper_db`


### Configure Data Input ###
* To create input use `db_inputs.conf.template` file from `default` directory of the App.
* If you wish to create the input from DB Connect UI, refer the `db_inputs.conf.template` file for reference.


UNINSTALL APP
-------------
To uninstall app, user can follow below steps:
* SSH to the Splunk instance.
* Go to folder apps($SPLUNK_HOME/etc/apps).
* Remove the `TA-lansweeper-add-on-for-splunk` folder from `apps` directory.
* Remove the DB Connect Identity, Connection and Inputs that you have created.
* Restart Splunk.


RELEASE NOTES
-------------
Version 1.3.5 (December 2024)
* Splunk-python-sdk updated to the latest version.

Version 1.3.4 (March 2024)
* Fixed configuration for timestamp extraction.
* Made field name changes as per the API changes.

Version 1.3.3 (Jan 2024)
* Updated the API headers.
* To improve the data collection performance, increased the assets per page limit from 100 to 500.

Version 1.3.2 (Oct 2023)
* Fixed the token expired issue
    * What was the issue?: The access token was not getting renewed because the Lansweeper API now returns 401 status code when token is not valid. Earlier it was returning 400 status code.
    *  Account reconfiguration is required only if the data collection does not auto resume after addon upgrade.

Version 1.3.1 (Sep 2022)
* Handled the Lansweeper API issue.
    * What was the issue?: As recently noticed (Sep 2022) Lansweeper API removed the field "_id" from the API response. The Lansweeper API Document still does not mention anything about this change on it.
    * But the Add-on now handles the situation gracefully by using the "key" field in the absence of "_id" field.
* Updated splunklib to the latest version (v1.7.2) to resolve the App-Inspect Failure.

Version 1.3.0 (Apr 2022)
* Added support to collect antivirus details in both DB Connect input and API input.
* Added props/field-extraction for the Antivirus fields.
* Updated Add-on to use the latest UCC version (5.10.2) to resolve the App-Inspect Failure.

Upgrade Guide from Version 1.2.x to 1.3.0
* The API input will collect the antivirus details from Lansweeper without any manual intervention.
* The DB Connect input will require updating the SQL query of the input. Find the new query in the `db_inputs.conf.template` file.

Version 1.2.3 (Dec 2021)
* Fixed the data collection stopped working (due to token expire) issue. (Root Cause: Change in the API response format.)
* Added more debug logs in data-collection input code.

Version 1.2.2 (Nov 2021)
* Cloud compatibility issue (Missing trigger in app.conf) fixed.

Version 1.2.1 (June 2021)
* Changing SourceType for API V2 to sourcetype=lansweeper:asset:v2

Version 1.2.0 (May 2021)
* Changing Lansweeper API from V1 to V2

Version 1.1.0 (April 2021)
* On-prem Lansweeper Support added (with database connection).
* Added more fields collection for cloud data collection.


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
* Bhavik Bhalodia


SUPPORT
-------
* Contact - CrossRealms International Inc.
  * US: +1-312-2784445
* License Agreement - https://cdn.splunkbase.splunk.com/static/misc/eula.html
* Copyright - Copyright CrossRealms Internationals, 2024
