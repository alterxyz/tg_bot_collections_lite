import json
import requests


def create_ph_account(short_name: str, author_name: str, author_url: str = None) -> str:
    """
    Creates a new account on the Telegra.ph platform or returns an existing access token.
    The token is stored in a local JSON file (token_key.json) along with other API keys.

    Args:
        short_name (str): The short name of the account.
        author_name (str): The name of the author.
        author_url (str, optional): The URL of the author's profile. Defaults to None.

    Returns:
        str: The access token for the account.

    Raises:
        requests.RequestException: If the API request fails.
        json.JSONDecodeError: If the API response is not valid JSON.
        KeyError: If the API response does not contain the expected data.
    """
    TELEGRAPH_API_URL = "https://api.telegra.ph/createAccount"
    TOKEN_FILE = "token_key.json"

    # Try to load existing token information
    try:
        with open(TOKEN_FILE, "r") as f:
            tokens = json.load(f)
        if "TELEGRA_PH_TOKEN" in tokens and tokens["TELEGRA_PH_TOKEN"] != "example":
            return tokens["TELEGRA_PH_TOKEN"]
    except FileNotFoundError:
        tokens = {}

    # If no existing valid token, create a new account
    data = {
        "short_name": short_name,
        "author_name": author_name,
    }
    if author_url:
        data["author_url"] = author_url

    # Make API request
    response = requests.post(TELEGRAPH_API_URL, data=data)
    response.raise_for_status()  # Raises an HTTPError for bad responses

    account = response.json()
    access_token = account["result"]["access_token"]

    # Update the token in the dictionary
    tokens["TELEGRA_PH_TOKEN"] = access_token

    # Store the updated tokens
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=4)

    return access_token


if __name__ == "__main__":
    create_ph_account("test", "Test User")
