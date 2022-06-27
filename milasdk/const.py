""" Mila constants """

AUTH_BASE_URL = "https://id.milacares.com"
AUTH_OIDC_TOKEN_ENDPOINT = AUTH_BASE_URL + "/auth/realms/prod/protocol/openid-connect/token"
AUTH_HEADER = "Authorization"
AUTH_CLIENT_ID = "prod-ui"
AUTH_SCOPES = "email profile"
AUTH_HEADER = "Authorization"

API_BASE_URL = "https://api.milacares.com/graphql"
API_DEFAULT_429_WAIT = 30
