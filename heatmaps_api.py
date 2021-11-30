"""
Module interfacing with the Swisscom API to get heatmap data
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

BASE_URL = "https://api.swisscom.com/layer/heatmaps/demo"
TOKEN_URL = "https://consent.swisscom.com/o/oauth2/token"
MAX_NB_TILES_REQUEST = 100
headers = {"scs-version": "2"}  # API version

# load environmental variables
load_dotenv()


def __get_credentials():
    # customer key in the Swisscom digital market place
    client_id = os.getenv("CLIENT_ID")
    # customer secret in the Swisscom digital market place
    client_secret = os.getenv("CLIENT_SECRET")
    return client_id, client_secret


def check_token_validity(api_handle):
    """Check the validity of the token

    :param api_handle: the oauth object to make requests
    """
    expire_timestamp = api_handle.token.get('expires_at')
    expire_date = datetime.fromtimestamp(expire_timestamp)
    formatted_expire = expire_date.strftime('%d %B %Y at %H:%M:%S')
    print(f'Token expires on: {formatted_expire}')


def get_api_handle():
    """Get the oauth request object with a valid authentication

    :return: oauth request object
    """
    # get access credentials
    client_id, client_secret = __get_credentials()

    # Fetch an access token
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    oauth.fetch_token(token_url=TOKEN_URL, client_id=client_id,
                      client_secret=client_secret)
    return oauth


def get_tile_ids_from_district(api_handle, district_nbr):
    """Get the tile ids for a district number

    :param api_handle: the oauth object to make requests
    :param district_nbr: the district to query
    :return: json response from the API
    """
    return api_handle.get(BASE_URL + "/grids/districts/{0}".format(district_nbr), headers=headers)


def get_dwell_density(api_handle, query_date, tiles):
    """Get dwell density for a specific date for a set of tiles (max 100)

    :param api_handle: the oauth object to make requests
    :param query_date: the date for which to query
    :param tiles: the tile ids (in list format) to query
    :return: json response from the API
    """
    url = BASE_URL + "/heatmaps/dwell-density/hourly/{0}".format(query_date.strftime('%Y-%m-%dT%H:%M'))
    return api_handle.get(url, headers=headers, params={"tiles": tiles})
