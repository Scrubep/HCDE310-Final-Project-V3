import string
import urllib.parse, urllib.request, urllib.error, json
import collections
import keys

# Creates json data. Is used for both RAWG and steam data below.
def create_json_data(base_url, parameters):
    param_str = urllib.parse.urlencode(parameters)
    request_url = base_url + "?" + param_str
    f = urllib.request.urlopen(request_url)
    json_url = ''
    for line in f:
        json_url += line.decode()
    json_data = json.loads(json_url)
    return json_data

def strip_word_punctuation(word):
    # Note - this function is far from comprehensive, and so some punctuation may
    # still make it through
    word = word.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&")
    return word.strip("&=.,()<>\"\\'~?!;*:[]-+_/`\u2014\u2018\u2019\u201c\u201d\u200b").replace("\"","\"\"")

# Converts name into something that is readable by RAWG.
def name_convert(name):
    name = name.lower().replace(" ", "-").replace(":", "").replace("'", "")
    parenth_index = name.find("(")
    if parenth_index > -1:
        name = name[0:parenth_index - 1]
    return name

# Finds the info of individual games using RAWG.
def individual_game_data(name):
    if " " in name:
        name = strip_word_punctuation(name_convert(name))
    base_url = "https://api.rawg.io/api/games/" + name
    return create_json_data(base_url, {"key": keys.RAWG_key})

# Is used to find data based on a person's steam account.
# This specifically just gives the game name and hours played by the user.
def create_steam_data(steam_id):
    # Checks to see if the steam_id is valid
    steam_id.replace(" ", "")
    steam_id.translate(str.maketrans('', '', string.punctuation))
    if len(steam_id) != 17 or any(c.isalpha() for c in steam_id):
        return None

    base_url = " http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001"
    parameters = {"key": keys.steam_key, "steamid": steam_id, "include_appinfo": "True",
                  "include_played_free_games": "True"}
    try:
        create_json_data(base_url, parameters)
    except urllib.error.HTTPError:
        return None

    return create_json_data(base_url, parameters)


# Creates a dictionary where the key is the game name and the value is the playtime.
# Makes it easier to parse through video games for finding other things.
# Sorting the list will let us see what the most played games of the user are.
def sort_playtimes(owned_games):
    playtimes = {}
    for game in owned_games["response"]["games"]:
        playtimes[game["name"]] = game["playtime_forever"]

    sorted_playtimes = sorted(playtimes.items(), key=lambda item: item[1], reverse=True)
    final_playtimes = collections.OrderedDict(sorted_playtimes)

    return final_playtimes

# Gets the most played genres of the user based on their user statistics.
# Based on their 5 most played games (subject to change).
def most_played_genres(steam_id):
    genres_list = []
    data = create_steam_data(steam_id)

    # Checks to see if the steam_id is valid
    if data is None or len(data["response"]) == 0:
        return genres_list

    steam_data = sort_playtimes(data)
    counter = 0;
    for game in steam_data:
        if counter < 5:
            game_info = individual_game_data(game)
            # Checks if the game can be rerouted to the correct slug.
            if "redirect" in game_info and game_info["redirect"] is True:
                game_info = individual_game_data(game_info["slug"])
            # If the game results in a not found error, go to the next game immediately.
            if "detail" in game_info and game_info["detail"] == "Not found.":
                continue
            for genre in game_info["genres"]:
                genre_name = genre["name"]
                if genre_name not in genres_list:
                    genres_list.append(genre_name)
        else:
            break
        counter += 1

    if "Action" in genres_list:
        genres_list.remove("Action")
    if "Adventure" in genres_list:
        genres_list.remove("Adventure")

    genres = genres_list[0]
    genres_list.remove(genres_list[0])
    for genre in genres_list:
        genres += "," + genre

    return genres

# Recommendations based on a person's steam data. Returns a list of games that are rated
# highly on metacritic of their most played genres. To read steam data, the account must
# have its inventory set to public.
def find_recommendations_steam(steam_id, page_size=10):
    genres = most_played_genres(steam_id)

    # Checks to see if the steam_id is valid
    if len(genres) == 0:
        return []

    base_url = "https://api.rawg.io/api/games"
    parameters = {"key": keys.RAWG_key, "page_size": page_size, "genres": genres.lower(), "ordering": "metacritic-"}
    RAWG_data = create_json_data(base_url, parameters)

    game_list = []
    for game in RAWG_data["results"]:
        game_info = individual_game_data(game["slug"])
        game_list.append(game_info)

    return game_list

# def advanced_search():
# The idea of this would be a potential extension of the website that allows users to either
# search for games themselves or sort the games they get into different categories.
# This would most likely be done by getting a list of the user's chosen options for the
# advanced search and then filter games based on that.

# Tests
#
# list = find_recommendations_steam("76561199105520418") # Anonymous K
# list = find_recommendations_steam("76561199388773489") # Anonymous J
# list = find_recommendations_steam("76561199202887189") # Anonymous L
# list = find_recommendations_steam("76561197960434622") # Random dude
# print("----------------------------")
# for game in list:
#     print(game.title)