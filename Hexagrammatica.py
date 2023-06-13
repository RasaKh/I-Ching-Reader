from requests import get, exceptions
from random import choices
import tkinter as tk
from tkinter import scrolledtext, StringVar, messagebox
from tkinter.ttk import Progressbar
import json
import threading
import traceback
from math import floor


with open("config.json.txt") as config_file:
    config = json.load(config_file)

# Access the variables from the config
url = config["api_url"]
timeout = config["timeout"]
gui_width_ratio = config["gui_width_ratio"]
gui_height_ratio = config["gui_height_ratio"]


class current_address:
    address = "111111"
    changed = "111111"
    # Default values
    ifchanged = False


def get_hexagram_data(binary_key):
    # Load the JSON file
    with open("hexagram_data.json", encoding="utf8") as file:
        hexagram_data = json.load(file)

    # Convert binary key to string
    key = str(binary_key)

    # Retrieve data using the key
    if key in hexagram_data:
        return hexagram_data[key]
    else:
        return None


def generate_hexagram():
    def coin_flip_to_hexagram(coin_flips):
        hexagram = ""
        for i in range(6):
            line = coin_flips[i * 3 : (i + 1) * 3]  # Extract three bits for each line
            if line.count("1") == 3:
                line_type = "O"  # Changing solid (greater yang)
            elif line.count("1") == 2:
                line_type = "S"  # Solid line (lesser yang)
            elif line.count("1") == 1:
                line_type = "B"  # Broken line (lesser yin)
            else:
                line_type = "X"  # Changing broken line (greater yin)
            hexagram += line_type

        # Convert hexagram to Unicode I Ching hexagram representation
        unicode_hexagram = ""
        for char in hexagram:
            if char == "S":
                unicode_hexagram += "⚍"  # Solid line (lesser yang)
            elif char == "B":
                unicode_hexagram += "⚎"  # Broken line (lesser yin)
            elif char == "O":
                unicode_hexagram += "⚌"  # Changing solid line (greater yang)
            elif char == "X":
                unicode_hexagram += "⚏"  # Changing broken line (greater yin)

        return hexagram, unicode_hexagram

    def get_coinflip():
        try:
            response = get(url, timeout=timeout)
            response.raise_for_status()  # Raise an exception if the request was not successful
            data = response.json()

            if data["success"]:
                hex_data = data["data"]  # Extract the hex data
                coin_flips = bin(int("0x" + hex_data[0], 16))[2:20].zfill(18)
                return (
                    coin_flips,
                    False,
                )  # Return coin_flips indicating that they were generated online (False refers to it not being offline)
            else:
                # Retrieval of data from the JSON was unsuccessful
                coin_flips = "".join(choices(["0", "1"], k=18))
                return (
                    coin_flips,
                    True,
                )  # Return coin_flips indicating that they were generated offline
        except exceptions.RequestException as e:
            coin_flips = "".join(choices(["0", "1"], k=18))
            return (
                coin_flips,
                True,
            )  # Return coin_flips indicating that they were generated offline
        except (KeyError, ValueError) as e:
            coin_flips = "".join(choices(["0", "1"], k=18))
            return (
                coin_flips,
                True,
            )  # Return coin_flips indicating that they were generated offline

    def handle_api_response(response):
        try:
            response.raise_for_status()  # Raise an exception if the request was not successful
            data = response.json()

            if data["success"]:
                hex_data = data["data"]  # Extract the hex data
                coin_flips = bin(int("0x" + hex_data[0], 16))[2:20].zfill(18)
                return (
                    coin_flips,
                    False,
                )  # Return coin_flips indicating that they were generated online (False refers to it not being offline)
            else:
                # Retrieval of data from the JSON was unsuccessful
                coin_flips = "".join(choices(["0", "1"], k=18))
                return (
                    coin_flips,
                    True,
                )  # Return coin_flips indicating that they were generated offline
        except Exception as e:
            coin_flips = "".join(choices(["0", "1"], k=18))
            return (
                coin_flips,
                True,
            )  # Return coin_flips indicating that they were generated offline

    def generate_hexagram_async():
        progress_bar.start()
        coin_flips, offline = get_coinflip()
        if offline:
            generated_label.config(text="Generated offline")
        else:
            generated_label.config(text="Generated online")
        hexagram, unicode_hexagram = coin_flip_to_hexagram(coin_flips)
        hexagram_label.config(text=unicode_hexagram)

        address = [0] * 6
        address_changing = [0] * 6
        for index, line in enumerate(hexagram):
            if line == "B":
                address[index] = 0
            elif line == "X":
                address[index] = 0
                address_changing[index] = 1
            elif line == "O":
                address[index] = 1
                address_changing[index] = 1
            elif line == "S":
                address[index] = 1

        address = "".join(str(line) for line in address)
        address_changing = "".join(str(line) for line in address_changing)
        changed = int(address, 2) ^ int(address_changing, 2)
        changed = bin(changed)[2:].zfill(len(address))

        if changed == address:
            current_address.address = "".join(reversed(address))
            current_address.ifchanged = False
            result_label.config(
                text="Result: "
                + current_address.address
                + "/"
                + str(get_hexagram_data("0b" + current_address.address)["kingwen"])
            )
            result_hexagram_label.config(
                text=(get_hexagram_data("0b" + current_address.address)["hexagram"])
            )

        else:
            current_address.address = "".join(reversed(address))
            current_address.changed = "".join(reversed(changed))
            current_address.ifchanged = True
            result_label.config(
                text="Result: "
                + current_address.address
                + "/"
                + str(get_hexagram_data("0b" + current_address.address)["kingwen"])
                + " CHANGING TO: "
                + current_address.changed
                + "/"
                + str(get_hexagram_data("0b" + current_address.changed)["kingwen"])
            )
            result_hexagram_label.config(
                text=(
                    get_hexagram_data("0b" + current_address.address)["hexagram"]
                    + " > "
                    + (get_hexagram_data("0b" + current_address.changed)["hexagram"])
                )
            )
        progress_bar.stop()

    threading.Thread(target=generate_hexagram_async).start()


def open_window(option):

    custom_window = tk.Toplevel(root)

    if option == 0:

        custom_window.title("Reading")
        custom_info_text = scrolledtext.ScrolledText(
            custom_window, height=30, width=60, font=("Helvetica", 12)
        )
        custom_info_text.pack(padx=5, pady=5)

        address_key = "0b" + current_address.address
        changed_key = "0b" + current_address.changed

        address_data = get_hexagram_data(address_key)
        changed_data = get_hexagram_data(changed_key)

        custom_text = "<<<<********>>>>\n"
        custom_text += "Current Hexagram:{}\n".format(address_data["hexagram"])
        custom_text += "Current King Wen Number: {}\n".format(address_data["kingwen"])
        custom_text += "Current Hexagram Name: {}\n\n".format(
            address_data["name"]["english"]
        )
        custom_text += "Current Hexagram Judgment: \n{}\n".format(
            address_data["judgement"]
        )
        custom_text += "Current Hexagram Images: \n{}\n".format(address_data["images"])
        custom_text += "Current Hexagram Lines:\n"
        for index, line in enumerate(address_data["lines"]):
            custom_text += "-Line {} : \n{}\n".format(index + 1, line["meaning"])
        custom_text += "\n"

        if current_address.ifchanged:
            custom_text += "<<<<********>>>>\n"
            custom_text += "Changed Hexagram:{}\n".format(changed_data["hexagram"])
            custom_text += "Changed King Wen Number: {}\n".format(
                changed_data["kingwen"]
            )
            custom_text += "Changed Hexagram Name: {}\n\n".format(
                changed_data["name"]["english"]
            )
            custom_text += "Changed Hexagram Judgment: \n{}\n".format(
                changed_data["judgement"]
            )
            custom_text += "Changed Hexagram Images: \n{}\n".format(
                changed_data["images"]
            )

        custom_info_text.delete(
            "1.0", tk.END
        )  # Clear the content of the scroll text area
        custom_info_text.insert(tk.END, custom_text)  # Paste the custom text

    else:

        custom_window.title("About")
        custom_info_text = scrolledtext.ScrolledText(
            custom_window, height=10, font=("Helvetica", 12)
        )
        custom_info_text.pack(padx=10, pady=10)
        error_log = traceback.format_exc()
        custom_info_text.delete("1.0", tk.END)
        custom_info_text.insert(
            tk.END, "Values Tutorial:\nYou can enter either the lines of each hexagram you want from top to bottom\nwith 1 being yang and 0 yin (e.g 110100), or the Kingwen number.\n\nThis program can receive quantum generated random data from ANU QRNG and use it to do I Ching reading.\nIf the QRNG is busy the data will be generated offline, and in that case you can wait a minute for the\nQRNG to come online again before retrying. The source of the data will be shown.\nAuthor: Rasa Kh\nVersion 2.2.1\n\n\n\n\nError Log:\n" + error_log + "\nAPI URL: " + url
        )

def get_key_by_kingwen(kingwen):
    # Load the JSON file
    with open('hexagram_data.json', encoding = 'utf8') as file:
        hexagram_data = json.load(file)

    # Find the key based on the kingwen value
    for key, data in hexagram_data.items():
        if data['kingwen'] == kingwen:
            return key
    
    return None


def set_values():

    sanitized_address = list([val for val in address_entry_var.get() if val.isnumeric()])
    sanitized_address = "".join(sanitized_address)
    if sanitized_address == "":
        messagebox.showerror("Field empty", "Fill the first field please, defaulted to hexagram 1")
        sanitized_address = "111111"
        
    sanitized_changed = list([val for val in changed_entry_var.get() if val.isnumeric()])
    sanitized_changed = "".join(sanitized_changed)
    if sanitized_changed == "":
        messagebox.showerror("Field empty", "Fill the second field please, defaulted to hexagram 2")
        sanitized_changed = "000000"
    current_address.changed = sanitized_changed

    if (1 <= int(sanitized_address) <= 64):
        current_address.address = get_key_by_kingwen(int(sanitized_address))[2:]
        
    elif (len(sanitized_address) == 6 and int(sanitized_address) <= 111111):
        current_address.address = sanitized_address

    else:
        messagebox.showerror("Invalid entry", "Invalid first field entry, defaulted to hexagram 1")
        current_address.address = "111111"

    if (1 <= int(sanitized_changed) <= 64):
        current_address.changed = get_key_by_kingwen(int(sanitized_changed))[2:]
        
    elif (len(sanitized_changed) == 6 and int(sanitized_changed) <= 111111):
        current_address.changed = sanitized_changed

    else:
        messagebox.showerror("Invalid entry", "Invalid second field entry, defaulted to hexagram 2")
        current_address.changed = "000000"
        

    current_address.ifchanged = (current_address.address != current_address.changed)

    if current_address.ifchanged:
        
        result_label.config(
            text="Result: "
            + current_address.address
            + "/"
            + str(get_hexagram_data("0b" + current_address.address)["kingwen"])
            + " CHANGING TO: "
            + current_address.changed
            + "/"
            + str(get_hexagram_data("0b" + current_address.changed)["kingwen"])
        )
        result_hexagram_label.config(
            text=(
                get_hexagram_data("0b" + current_address.address)["hexagram"]
                + " > "
                + (get_hexagram_data("0b" + current_address.changed)["hexagram"])
            )
        )
    else:
        result_label.config(
                text="Result: "
                + current_address.address
                + "/"
                + str(get_hexagram_data("0b" + current_address.address)["kingwen"])
            )
        result_hexagram_label.config(
                text=(get_hexagram_data("0b" + current_address.address)["hexagram"])
            )
            
    generated_label.config(text="Manually Entered")
    hexagram_label.config(text="☯")




def show_about():
    open_window(1)


def show_reading():
    open_window(0)


# GUI setup

getsize = tk.Tk()
screen_width = getsize.winfo_screenwidth()
screen_height = getsize.winfo_screenheight()
getsize.destroy()

gui_width = floor(screen_width * gui_width_ratio)
gui_height = floor(screen_height * gui_height_ratio)

# Create the Tkinter window with the desired dimensions
root = tk.Tk()
root.geometry(f"{gui_width}x{gui_height}")
root.title("Hexagrammatica")
root.iconbitmap("hexagrammatica.ico")

f0 = tk.Frame(root)

header_label = tk.Label(
    f0, text="❖ I Ching Hexagram Reader ❖", font=("Helvetica", 16, "bold")
)


generate_button = tk.Button(
    root, text="Generate Hexagram", command=generate_hexagram, font=("Helvetica", 14)
)
generated_label = tk.Label(root, text="", font=("Helvetica", 12))
hexagram_label = tk.Label(root, text="", font=("Helvetica", 60))
result_hexagram_label = tk.Label(root, text="", font=("Helvetica", 60))
result_label = tk.Label(root, text="", font=("Helvetica", 12))

f1 = tk.Frame(root)
about_button = tk.Button(f1, text="Help", command=show_about, font=("Helvetica", 12))
custom_button = tk.Button(f1, text="Show Reading", command=show_reading, font=("Helvetica", 12))
progress_bar = Progressbar(root, mode="indeterminate")

f2 = tk.Frame(root)
address_entry_var = StringVar(value="111111")
changed_entry_var = StringVar(value="000000")
address_entry = tk.Entry(f2, textvariable=address_entry_var, font=("Helvetica", 12))
changed_entry = tk.Entry(f2, textvariable=changed_entry_var, font=("Helvetica", 12))
set_values_button = tk.Button(f2, text="Set Values", command=set_values, font=("Helvetica", 12))

f0.pack(pady=10)
header_label.pack()

generate_button.pack()
generated_label.pack()
hexagram_label.pack()
result_hexagram_label.pack()
result_label.pack(pady=5)

f1.pack(pady=5)
custom_button.pack(side=tk.LEFT, padx=5)  # Position the custom button above the About button
about_button.pack(side=tk.RIGHT, padx=5)

f2.pack(pady=5)
address_entry.pack(side=tk.LEFT, padx=5)
changed_entry.pack(side=tk.RIGHT, padx=5)
set_values_button.pack()

progress_bar.pack()  # Add the progress bar to the GUI

root.mainloop()
