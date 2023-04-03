#!/usr/bin/env python3

import globus_sdk

CLIENT_ID = "ed8b9705-b6d4-44d5-aab5-5f0dc6d73dc5"
CLIENT_SECRET = "siBtBlacTEb9Y2xMgT7H2cmN+S2xrqJO0KtYBED2LIs="


def get_authorizer(scope):
    # Substitute your values here:
    # ENDPOINT_ID = "74c9d48c-3d1b-11ed-ba4d-d5fb255a47cc"

    # The authorizer manages our access token for the scopes we request
    authorizer = globus_sdk.ClientCredentialsAuthorizer(
        # The ConfidentialAppAuthClient authenticates us to Globus Auth
        globus_sdk.ConfidentialAppAuthClient(
            CLIENT_ID,
            CLIENT_SECRET
        ),
        f"{scope}"
        # f"urn:globus:auth:scope:{ENDPOINT_ID}:manage_collections"
    )

    print(f'access_token: {authorizer.access_token}')
    return authorizer
    # The access token is stored in authorizer.access_token
