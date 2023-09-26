from auth0.authentication import GetToken

# token = GetToken('my-domain.us.auth0.com', 'my-client-id', client_secret='my-client-secret')

# token.login(username='user@domain.com', password='secr3t', realm='Username-Password-Authentication')

# from auth0.authentication import GetToken

domain = 'dev-imyvrykl8sls808t.us.auth0.com'
non_interactive_client_id = '5CRA1lfyOJLN1bIW6hBqC1WOnVrYLzcn'
non_interactive_client_secret = 'Ufd0v-QdcJaUrGlHZtnLENLIRhDzhCDba186TYwkiOaptlnxgT_oEoNX3seB8xmd'

get_token = GetToken(domain, non_interactive_client_id, client_secret=non_interactive_client_secret)
token = get_token.client_credentials('https://{}/api/v2/'.format(domain))
mgmt_api_token = token['access_token']

print(mgmt_api_token)