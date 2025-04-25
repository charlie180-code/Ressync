import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# Define the SCOPES for Gmail access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_credentials():
    # Create an OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret_874918143904-rm7kle90m1639r5basrfs0o332c3q1jh.apps.googleusercontent.com.json',
        scopes=SCOPES
    )
    
    # Specify the redirect URI (make sure it matches what you have in Google Console)
    flow.redirect_uri = 'http://127.0.0.1:5000/auth/login'  # Change this if needed
    
    # Get the authorization URL
    auth_url, _ = flow.authorization_url(access_type='offline')
    
    print("Please go to this URL: {}".format(auth_url))
    
    # Manually enter the authorization response URL
    code = input("Enter the authorization code: ")
    
    # Exchange the authorization code for credentials
    flow.fetch_token(code=code)

    # Create a Credentials object to access tokens
    creds = flow.credentials
    
    return creds

if __name__ == '__main__':
    credentials = get_credentials()
    print("Access Token:", credentials.token)  # This should work now
    print("Refresh Token:", credentials.refresh_token)
    print("Client ID:", credentials.client_id)
    print("Client Secret:", credentials.client_secret)
