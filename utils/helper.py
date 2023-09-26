import uuid
import os
from django.conf import settings


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('uploads/logos', filename)


def generate_absolute_uri(request, url):
    return request.build_absolute_uri(url)


def get_view_permissions(request, view):
    required_permissions = view.get_required_permissions().value
    permissions = request.user.permission.all().values_list(
        "code_id", flat=True
    )
    return required_permissions, permissions


from auth0.authentication import GetToken

# get_token = GetToken(settings.AUTH_0_DOMAIN, settings.AUTH_0_CLIENT_ID, settings.AUTH_0_SECRET)
# token = get_token.client_credentials(settings.AUTH_0_AUDIENCE)
# mgmt_api_token = token['access_token']

# print("JYTGBJUHNIJM", mgmt_api_token)


from auth0.authentication.token_verifier import TokenVerifier, AsymmetricSignatureVerifier

from auth0.authentication.token_verifier import TokenValidationError


# domain = settings.AUTH_0_DOMAIN
# client_id = settings.AUTH_0_CLIENT_ID

# # After authenticating
# id_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjZUaXQ0dkpqbUU5NjlGeE1zTmRlViJ9.eyJpc3MiOiJodHRwczovL2Rldi1pbXl2cnlrbDhzbHM4MDh0LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiI1Q1JBMWxmeU9KTE4xYklXNmhCcUMxV09uVnJZTHpjbkBjbGllbnRzIiwiYXVkIjoiaHR0cHM6Ly9kZXYtaW15dnJ5a2w4c2xzODA4dC51cy5hdXRoMC5jb20vYXBpL3YyLyIsImlhdCI6MTY5NTczMjU4MSwiZXhwIjoxNjk1NzMyODgxLCJhenAiOiI1Q1JBMWxmeU9KTE4xYklXNmhCcUMxV09uVnJZTHpjbiIsImd0eSI6ImNsaWVudC1jcmVkZW50aWFscyJ9.lfr-d-0v2YzvdUym3N69DpDtEQlC774NGjMpUzp2EjkABAxU-QReh48fnStXdIbvckNiJmEXGQB54X1eV4psz0LxM8gs8AZMawQhDIfoga3Fzk4JwE10U5lGz3HKjhzfdh4eIeL1YMRGZ_ZuReNf0PN3wLLuCqCQJiXssSmETwYuhu_DwQmNV2eCVMUQqbkrnJB-GcQ7_LpmLDZWtzqyoLi-h9p9Fjz90sRHzib6_extO1wIYliEjESsqzbOO6PwU0vJYJfTtanSpjUdeZ9s4pSDOYhkjSr8r4Q-pNPnJRLsmKRzyTDf0FadaU0Xl23r2GIva4CiwcYdS8DvgaRZuw"

# jwks_url = 'https://{}/.well-known/jwks.json'.format(settings.AUTH_0_DOMAIN)
# issuer = 'https://{}/'.format(settings.AUTH_0_DOMAIN)

# sv = AsymmetricSignatureVerifier(jwks_url)  # Reusable instance
# tv = TokenVerifier(signature_verifier=sv, issuer=issuer, audience=settings.AUTH_0_AUDIENCE)

# if tv.verify(str(id_token)):
#     print(tv.verify(str(id_token)))
#     print("JFBGNHKJJMNBVBHNM ")
# else:
#     print("HFHGNJ<:: Fail")
# print(tv.verify(str(id_token)))
# class Auth0JWTValidator(JWT):
#     def __init__(self, issuer, audience):
#         super().__init__()
#         self.issuer = issuer
#         self.audience = audience

#     def validate(self, token):
#         if not super().validate(token):
#             return False

#         if self.issuer != token.get('iss'):
#             return False

#         if self.audience != token.get('aud'):
#             return False

#         return True
