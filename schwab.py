import webbrowser
import requests

# Your Schwab API credentials
client_id = "YEtcahvfjgTwA84YWR7MsGOMvKGKkWpq"
client_secret = "vR3VFc6H8ZAR29zF"
redirect_uri = "https://127.0.0.1"  # Must match Schwab registration

# Authorization URL
auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?response_type=code&client_id={client_id}&scope=readonly&redirect_uri={redirect_uri}"

print("Opening browser for authorization...")
print(f"Full auth URL: {auth_url}")
webbrowser.open(auth_url)

# Ask for the authorization code
auth_code = input("Paste the FULL redirected URL or just the 'code' parameter from the browser here: ").strip()

# If user pasted the full URL, extract the code
if "code=" in auth_code:
    auth_code = auth_code.split("code=")[1].split("&")[0]
print(f"Using authorization code: {auth_code}")

# Token exchange
token_url = "https://api.schwabapi.com/v1/oauth/token"  # Corrected endpoint

payload = {
    "grant_type": "authorization_code",
    "code": auth_code,
    "redirect_uri": redirect_uri,
    "client_id": client_id,
    "client_secret": client_secret
}

headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

try:
    print(f"Sending request to: {token_url}")
    print(f"Payload: {payload}")
    response = requests.post(token_url, data=payload, headers=headers)
    print("\nResponse Status Code:", response.status_code)
    print("Response Text:", response.text)

    try:
        tokens = response.json()
        access_token = tokens.get("access_token")
        if access_token:
            print("\nAccess Token:", access_token)
        else:
            print("\nFailed to retrieve access token. Check error message above.")
    except requests.exceptions.JSONDecodeError:
        print("\nError: Could not decode JSON response. Raw response:", response.text)
except requests.exceptions.RequestException as e:
    print(f"\nError making request: {e}")