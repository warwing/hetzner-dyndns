#!/usr/bin/python3


## Imports
import os
import json
import requests
import logging
import logging.handlers
import argparse
import smtplib
import ssl
from datetime import datetime


##
## Parse arguments
##
parser = argparse.ArgumentParser()
parser.add_argument(
	"-l",
	"--logLevel",
	default="info",
	help="Set a logging level")

parser.add_argument(
    "-c",
    "--configFile",
    default=f"{os.path.dirname(__file__)}/conf.json",
    help="Set the config file location")

options = parser.parse_args()

##
## Script exit function
##

def exit_script(code):

    if code == 0:
        warningText = "no errors"
    if code == 1:
        warningText = "one or more warnings"
    if code == 2:
        warningText= "one or more errors"
        
    # Write our summarizing log entry
    logger.info(f"Script has ended with {warningText}.")

    # If we haven't finished successfully, send out a mail
    if code > 0:
        send_warning_mail(warningText)

    logger.info("All done ✓")

    exit()

def send_warning_mail(warningText):

    # Send a warning mail
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(
            config['smtpServer'],
            config['smtpPort'],
            context=context) as server:

            # Log in to our server
            server.login(config["smtpUser"], config["smtpPassword"])

            # Send out a warning mail
            message = f"""From: Watchdog | zudrell.eu <watchdog@zudrell.eu>
To: Jakob Zudrell <jakob@zudrell.eu>
Subject: DynDns Warning

Warning the Hetzner-DynDns script has ended with {warningText}.\nTimestamp: {datetime.now()}
"""
            server.sendmail(config['smtpUser'], config['warningReceiver'], message)

            # Successfully sent our mail
            logger.info("Successfully sent out a warning mail ✓")

    except Exception as e:
        logger.error(f"Failed to send email: {repr(e)}")


levels = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warn': logging.WARNING,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}

level = levels.get(options.logLevel.lower())

if level is None:
	raise ValueError(f"log level given: {options.log}"
        f" -- must be one of: {' | '.join(levels.keys())}")

##
## Configure logger
##

LOG_FILENAME = f"{os.path.dirname(__file__)}/dyndns.log"

# Create logger
logger = logging.getLogger("hetzner-dyndns")
logger.setLevel(level)

# Rotating file handler
fh = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=5242880, backupCount=5)

# Create formatter
formatter = logging.Formatter("[%(asctime)s - %(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

# add formatter to console handler
fh.setFormatter(formatter)

# add ch to logger
logger.addHandler(fh)

logger.info("Executing script...")



##
## Configuration
##
configFile = options.configFile

# Check if we have a valid file given
if not os.path.exists(configFile):
    logger.error("Invalid config file location. Terminating script!")
    exit_script(2)

with open(configFile, "r") as configFile:
    config = json.load(configFile)
    logger.info(f"Config file successfully parsed ✓")

##
## Main
##

# Get the public IP
webRequest = requests.get("http://icanhazip.com")

# Outupt an error if getting the public IP failed
if webRequest.status_code != 200:
	logger.error(f"Getting public IP failed with code {webRequest.status_code}")
	exit_script(2)

# Read our public IP
publicIp = webRequest.text.strip()
logger.info(f"Public IP is {webRequest.text.strip()} ✓")

# Create our PUT request
headers = { "Content-Type": "application/json", "Auth-API-Token": config['apiKey']  }

updatedRecords = []
for updatedRecord in config['records']:
    updatedRecord["zone_id"] = config['zoneId']
    updatedRecord["value"] = publicIp
    updatedRecords.append(updatedRecord)

payload = '{ "records": ' + json.dumps(updatedRecords) + "}"

# Send our PUT request
apiPostRequest = requests.put(
    f"{config['apiBaseUrl']}/records/bulk",
    data=payload,
    headers=headers)

# Check for a 200 response
if apiPostRequest.status_code != 200:
	logger.error(f"Failed to update DNS record: {apiPostRequest.text.rstrip()}")
	exit_script(2)


# Check if any records failed
response = json.loads(apiPostRequest.text)
for failedRecord in response['failed_records']:
    logger.warning(f"Failed to update record '{failedRecord['name']}' with ID '{failedRecord['id']}'")

# Exit with warning if some records failed
if len(response['failed_records']) > 0:
    exit_script(1)
else:
    logger.info("All records updated successfully! ✓")

exit_script(0)