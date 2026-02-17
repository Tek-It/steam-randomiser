import os
import datetime
import requests
vanity_url = "jiltedsnake"
KEY = os.environ.get("STEAM_API_KEY")
if not KEY:
    raise RuntimeError(
        "Steam Web API key environment variable not set. "
        "Please set STEAM_API_KEY and restart your shell before running."
    )

from steamwebapi import profiles
import traceback


def normalize_user_identifier(inp: str) -> str:
    """Strip a full URL or accept a vanity/steamid directly."""
    inp = inp.strip()
    if inp.startswith(("http://", "https://")):
        from urllib.parse import urlparse
        parsed = urlparse(inp)
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2 and parts[0] in ("id", "profiles"):
            return parts[1]
        return parts[-1]
    return inp

def get_player_name(steamid: str) -> str:
    """Retrieve the player name (persona) for a given SteamID."""
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    params = {
        "key": KEY,
        "steamids": steamid
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data['response']['players'][0]['personaname'] if data['response']['players'] else "Unknown Player"

def printfriendslist():
    try:
        user_profile = profiles.get_user_profile(
            normalize_user_identifier(vanity_url),
            steam_api_key=KEY,
        )
        
    except SystemExit as se:
        print(f"Steam API request failed (exit code {se.code}).\n"
            "Check your network connection and API key.")
        user_profile = None
    except Exception as exc:
        print("Unexpected error while retrieving Steam data:", exc)
        traceback.print_exc()
        user_profile = None

    if user_profile is not None:
        # steamwebapi library has a typo: method should be "GetFriendList",
        # not "GetFriendsList".  The built-in helper emits the wrong URL which
        # causes a 404 and triggers the generic "Error Retrieving Data from
        # Steam" behavior.  Work around by constructing the request ourselves.
        def get_friend_list(steam_user_obj, steamid, relationship="friend"):
            """Return friends list JSON using the corrected API method name."""
            params = {"steamid": steamid, "relationship": relationship}
            url = steam_user_obj.create_request_url(
                steam_user_obj.interface, "GetFriendList", 1, params
            )
            data = steam_user_obj.retrieve_request(url)
            return steam_user_obj.return_data(data, format="json")

        try:
            steam_user = profiles.ISteamUser(steam_api_key=KEY)
            steamid = user_profile.steamid
            friends_list = get_friend_list(steam_user, steamid, relationship="friend")
            response = friends_list
            friends = response['friendslist']['friends']

    # Loop through each friend and print information
            for friend in friends:
                steamid = friend['steamid']
                friend_since_timestamp = friend['friend_since']
                friend_since_date = datetime.datetime.utcfromtimestamp(friend_since_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                player_name = get_player_name(steamid)
                print(f"Steam ID: {player_name}")
                print(f"Friend Since: {friend_since_date}")
                print("-" * 30)

        except SystemExit as se:
            print(f"Steam API request failed (exit code {se.code}) when fetching friends list.")
        except Exception as exc:
            print("Unexpected error while retrieving friends list:", exc)
            traceback.print_exc()

def get_owned_games(steamid: str) -> str:
    """Get the list of games owned by the user."""
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        "key": KEY,
        "steamid": steamid,
        "include_appinfo": 1,  # Include game name and logo information
        "format": "json"
    }

    # Make the GET request to the API
    response = requests.get(url, params=params)
    
    # Check for a successful response
    if response.status_code == 200:
        data = response.json()
        
        # Check if games data is available
        if "response" in data and "games" in data["response"]:
            games = data["response"]["games"]
            game_names = [game["name"] for game in games]  # List of game names
            return game_names
        else:
            return "No games found or profile is private."
    else:
        return f"Error: Unable to fetch data (Status Code: {response.status_code})"

def printownedgames():
    """Retrieve and print the owned games of a user."""
    try:
        # Retrieve user profile using the provided vanity URL
        user_profile = profiles.get_user_profile(
            normalize_user_identifier(vanity_url),
            steam_api_key=KEY,
        )
    except SystemExit as se:
        print(f"Steam API request failed (exit code {se.code}).\n"
              "Check your network connection and API key.")
        user_profile = None
    except Exception as exc:
        print("Unexpected error while retrieving Steam data:", exc)
        traceback.print_exc()
        user_profile = None

    # If user profile was successfully retrieved, fetch and print their owned games
    if user_profile is not None:
        try:
            steamid = user_profile.steamid
            # Fetch the list of owned games
            games_list = get_owned_games(steamid)
            if isinstance(games_list, list):  # If it's a list of games, print them
                print(f"Owned Games for SteamID {steamid}:")
                for game in games_list:
                    print(f"- {game}")
                    
            else:
                # Print the error message
                print(games_list)
        except Exception as e:
            print(f"Unexpected error while retrieving owned games: {e}")
            traceback.print_exc()

def randomly_select_game(games_list=get_owned_games(profiles.get_user_profile(normalize_user_identifier(vanity_url),steam_api_key=KEY,).steamid)):
    """Randomly select a game from the list of owned games."""
    import random
    if isinstance(games_list, list) and games_list:
        selected_game = random.choice(games_list)
        print(f"Randomly Selected Game: {selected_game}")
    else:
        print("No games available to select from.")

if __name__ == "__main__":
    randomly_select_game()