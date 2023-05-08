import globus_sdk

from .auth import internal_auth_client, token_storage_adapter
from ..globus_auth import get_authorizer

SEARCH_RESOURCE_SERVER = "search.api.globus.org"


def search_client(authenticated=True):
    storage_adapter = token_storage_adapter()
    as_dict = storage_adapter.read_as_dict()

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


def new_search_client(authenticated=True):
    authorizer = get_authorizer(GLOBUS_AUTH_SCOPE_INGEST)

    return globus_sdk.SearchClient(authorizer=authorizer, app_name="searchable-files")
