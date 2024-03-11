import globus_sdk

from .auth import internal_auth_client, token_storage_adapter
from ..globus_auth import get_authorizer
from globus_sdk.scopes import SearchScopes

SEARCH_RESOURCE_SERVER = "search.api.globus.org"


def search_client(authenticated=True):
    storage_adapter = token_storage_adapter()
    as_dict = storage_adapter.read_as_dict()
    print("[search_client]")
    print(storage_adapter.dbname)
    authorizer = None
    if authenticated:
        authdata = as_dict[SEARCH_RESOURCE_SERVER]
        access_token = authdata["access_token"]
        print(f'[search_client] access_token={access_token}')
        refresh_token = authdata["refresh_token"]
        access_token_expires = authdata["expires_at_seconds"]
        authorizer = globus_sdk.RefreshTokenAuthorizer(
            refresh_token,
            internal_auth_client(),
            access_token,
            int(access_token_expires),
            on_refresh=storage_adapter.on_refresh,
        )

    return globus_sdk.SearchClient(authorizer=authorizer, app_name="searchable-files")


GLOBUS_AUTH_SCOPE_INGEST = "urn:globus:auth:scope:search.api.globus.org:ingest"


def app_search_client(authenticated=True):
    # CLIENT_ID = "ed8b9705-b6d4-44d5-aab5-5f0dc6d73dc5"
    # CLIENT_SECRET = "7/K6vfoUo7ONioH6QNedfyOq0mnHJocOnedtJGGggHA="

    # service account MetadataExtractor token
    CLIENT_ID = "0f657343-4e07-4c37-b203-ff3eec9d4b9f"
    CLIENT_SECRET = "MZi3nwu5tmK4XZhqazQDRYuAlFPVC18iZkTrSvpQKOc="

    client = globus_sdk.ConfidentialAppAuthClient(CLIENT_ID, CLIENT_SECRET)
    # scopes = "urn:globus:scopes:search.api.globus.org:all"
    scopes = SearchScopes.all
    cc_authorizer = globus_sdk.ClientCredentialsAuthorizer(client, scopes)
    return globus_sdk.SearchClient(authorizer=cc_authorizer, app_name="geoedf-portal")


