from flask import Flask, render_template, request, session
from function import find_recommendations_steam, create_steam_data, sort_playtimes, individual_game_data

# The app will start at index.html

# After the form submission, it will lead to result
# In results, it will read a post request and process the data
# submitted by the user at the index. This will be game data that
# is displayed in results.html using find_recommendations_steam(steam_id)
# in functions.

# Clicking into any game will lead to game.html which will have a more descriptive
# summary of the game within it. I'll need to figure out how to link the different
# games to the different links.

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        steam_id = request.form['steam_id']
        data = create_steam_data(steam_id)
        playtimes = sort_playtimes(data)

        counter = 0
        top_playtimes = {}
        for game in playtimes:
            if (counter < 5):
                top_playtimes[game] = playtimes[game]
                counter += 1
            else:
                break

        list = find_recommendations_steam(steam_id, int(request.form['input_page']))

        return render_template('results.html', counter=0, playtimes=top_playtimes, game_list=list)

@app.route('/game', methods=['GET', 'POST'])
def game():
    if request.method == 'POST':
        input_game_slug = request.form['input_game']
        input_game = individual_game_data(input_game_slug)

        return render_template('game.html', input_game=input_game)