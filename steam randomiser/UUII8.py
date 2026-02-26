import tkinter as tk
import random
import time
from datetime import datetime
import steam_web_functions as swf
root = tk.Tk()
root.title("GAME DASHBOARD")
root.geometry("800x500")
swf.printfriendslist()
friends = swf.list_of_friends
game_library = (swf.get_owned_games(swf.profiles.get_user_profile(swf.normalize_user_identifier(swf.vanity_url),steam_api_key=swf.KEY,).steamid))
seconds_pasd = 0



def clear_output():
    output_text.delete(1.0, tk.END)

"""The timer that counts how long you have been playing"""
def update_timer():
    global seconds_pasd

    seconds_pasd += 1

    hours = seconds_pasd // 3600
    minutes = (seconds_pasd % 3600) // 60
    seconds = seconds_pasd % 60

    timer_label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")

    root.after(1000, update_timer)

"""The main Function"""
def show_games():
    clear_output()
    game_library = (swf.get_owned_games(swf.profiles.get_user_profile(swf.normalize_user_identifier(swf.vanity_url),steam_api_key=swf.KEY,).steamid)).__getitem__(0) # get the list of game names from the returned tuple
    output_text.insert(tk.END, "Currently Owned Games (Your Library):\n\n")

    for game in game_library:
        output_text.insert(tk.END, f"- {game}\n")


def show_random_game():
    clear_output()
    game_library = (swf.get_owned_games(swf.profiles.get_user_profile(swf.normalize_user_identifier(swf.vanity_url),steam_api_key=swf.KEY,).steamid).__getitem__(0))  # get the list of game names from the returned tuple
    if not game_library:
        output_text.insert(tk.END, "No games in your library.")
        return

    random_game = random.choice(game_library)

    output_text.insert(tk.END, f"Random Game Selected:\n\n{random_game}")


def show_friends():
    clear_output()
    output_text.insert(tk.END, "Friends List:\n\n")
    

    if friends == {}:
        output_text.insert(tk.END, "No friends added yet.\n")
        return
    for friend in friends:
        output_text.insert(tk.END, f"- {friend}\n" + "   Added on: " + friends[friend]["added_on"] + "\n\n")
    
        


def show_achievements():
    clear_output()
    output_text.insert(tk.END, "Achievements:\n\n")
    output_text.insert(tk.END, (swf.process_all_achievements()))
    


def show_steamusername():
    entry_name.pack(pady=5, padx=10)
    button_confirm.pack(pady=5, padx=10)


def confirm_add_username():
    swf.vanity_url = entry_name.get().strip()

    if swf.vanity_url == "": # if empty/no letter or words
        return

    swf.printfriendslist()
    
    entry_name.delete(0, tk.END)
    entry_name.pack_forget()
    button_confirm.pack_forget()

    clear_output()
    output_text.insert(tk.END, f"{swf.vanity_url} added successfully!")
    return game_library

#QUIT
def quit_app():
    root.destroy()


"""THE FRAMES/LAYOUT"""
# Timer
top_frame = tk.Frame(root)
top_frame.pack(side="top", fill="x")
timer_label = tk.Label(top_frame, font=("Arial", 12))
timer_label.pack(side="right", padx=10, pady=5)
update_timer()  # start counter

left_frame = tk.Frame(root, width=200, bg="lightblue")
left_frame.pack(side="left", fill="y")

main_frame = tk.Frame(root)
main_frame.pack(side="right", expand=True, fill="both")

"""THE BUTTONS"""
#currently owned games will show the temporary-manual game library
button_games = tk.Button(left_frame, text="Currently Owned Games", command=show_games)
button_games.pack(pady=10, padx=10)

#the random game will pick the game randomly
button_random = tk.Button(left_frame, text="Random Game", command=show_random_game)
button_random.pack(pady=10, padx=10)

#it will show the list of player(will be emptied everytiem is quitted)
button_friends = tk.Button(left_frame, text="Friends List", command=show_friends)
button_friends.pack(pady=10, padx=10)

#shows achievement per player
button_achievements = tk.Button(left_frame, text="Achievements", command=show_achievements)
button_achievements.pack(pady=10, padx=10)

#allows to add new friend name 
button_steamusername = tk.Button(left_frame, text="Input steam vanity or 64bit ID", command=show_steamusername)
button_steamusername.pack(pady=10, padx=10)
entry_name = tk.Entry(left_frame)
button_confirm = tk.Button(left_frame, text="Confirm", command=confirm_add_username)

# to output the text
output_text = tk.Text(main_frame, wrap="word")
output_text.pack(expand=True, fill="both", padx=20, pady=20)

# Quit
spacer = tk.Frame(left_frame)
spacer.pack(expand=True, fill="both")

quit_button = tk.Button(left_frame, text="QUIT", command=quit_app)
quit_button.pack(fill="x", padx=10, pady=10)

root.mainloop()