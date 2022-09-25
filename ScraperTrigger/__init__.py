import datetime
import logging
import re
import os

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from requests_html import HTMLSession

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    # Create a session and get the html data 
    session = HTMLSession()
    r = session.get('https://www.fitx.de/fitnessstudios/neuss-innenstadt')

    # Convert to text format
    text = r.text

    # Search the exact place we are interested in
    # WARNING: This might not work anymore in the furture if the website is restructured
    workload = re.findall('(s|data-current-day-data=")\[(.*?)\]', text)

    # Convert to a list 
    workload_numbers = workload[0][1]
    workload_list = [int(s) for s in workload_numbers.split(',')]

    # Write the numbers 
    blob_name = f"workload-{str(datetime.datetime.today().strftime('%Y-%m-%d %H-%M-%S'))}.txt"

    # Create blob service client and container client
    storage_account_url = "https://" + "scrapergroup8ec1" + ".blob.core.windows.net"
    credential = DefaultAzureCredential()
    client = BlobServiceClient(account_url=storage_account_url, credential=credential)

    blob_client = client.get_blob_client(container='function-results', blob=blob_name)
    blob_client.upload_blob(str(workload_list[-1]))