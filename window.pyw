import tkinter as tk
import tkinter.ttk as ttk
import toml
import sv_ttk
import subprocess
import os
import sys
import ctypes
from PIL import Image, ImageTk
import pystray

SW_HIDE = 0
SW_SHOW = 5

user32 = ctypes.windll.user32

def toggle_visibility():
    if root.state() == 'normal':
        root.state('withdrawn') # hide the window
    else:
        root.state('normal') # show the window

process = None

# create a function to maximize the window if necessary
def maximize_window(icon, item):
    icon.stop()
    root.after(0, root.deiconify)

# create a function to minimize the window
def minimize_window(hide=False):
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    ctypes.windll.user32.ShowWindow(hwnd, 0 if hide else 6)
    root.withdraw()
    image = Image.open("icon.ico")
    menu = (pystray.MenuItem('Quit', on_closing), pystray.MenuItem('Show', maximize_window))
    icon = pystray.Icon("name", image, "LastFM Presence", menu)
    icon.run()

# create a function to exit the program
def on_closing(icon=None, item=None):
    if process is not None:
        process.kill()
    stop_presence()
    root.destroy()
    if icon is not None:
        maximize_window(icon, item)

is_visible = True
hasstyle = False
# create a function to be called when the tray icon is clicked
def on_clicked(icon):
    global is_visible
    if is_visible:
        root.withdraw() # hide the window
        is_visible = False
        icon.stop()
    else:
        icon.run()
        root.deiconify() # show the window
        is_visible = True

config = toml.load("settings.toml")

def save_settings():
    config["api_key"] = api_key_entry.get()
    config["username"] = username_entry.get()
    config["client_id"] = client_id_entry.get()
    config["small_image_avatar"] = small_image_avatar.get()
    config["button_text"] = button_text_entry.get()
    config["button_url"] = button_url_entry.get()
    with open("settings.toml", "w") as f:
        toml.dump(config, f)

def start_stop_presence():
    if config["is_running"]:
        stop_presence()
        start_stop_button.config(text="Start Presence", style="TButton")
    else:
        start_presence()
        start_stop_button.config(text="Stop Presence", style="Accent.TButton")

def start_presence():
    global process
    if process is not None:
        return
    if sys.platform.startswith('win'):
        process = subprocess.Popen(['python', 'presence.py'], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        process = subprocess.Popen(['python', 'presence.py'], preexec_fn=os.getpid)
    config["is_running"] = True
    with open("settings.toml", "w") as f:
        toml.dump(config, f)

def stop_presence():
    global process
    config["is_running"] = False
    if process is not None:
        process.kill()
        process = None
    with open("settings.toml", "w") as f:
        toml.dump(config, f)

def toggle_presence():
    if start_stop_button["text"] == "Start Presence":
        start_stop_button.config(text="Stop Presence")
        start_presence()
    else:
        start_stop_button.config(text="Start Presence")
        stop_presence()


root = tk.Tk()
window_width, window_height = 550, 375
screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
x = int((screen_width/2) - (window_width/2))
y = int((screen_height/2) - (window_height/2))
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.title("Last.fm Presence Settings")
sv_ttk.set_theme("dark")

# configure the window
root.overrideredirect(True)  # remove the default title bar
root.resizable(True, True)  # allow the window to be resizable

# create a custom title bar
title_bar = tk.Frame(root, bg="#222222", relief="raised", bd=0)
title_bar.pack(expand=True, fill="x")

# add a label to the title bar to display the window title
img = Image.open("icon.ico").resize((20,20))

title_label = tk.Label(title_bar, text=root.title(), bg="#222222", fg="white", font=("Helvetica", 12))
tk_img = ImageTk.PhotoImage(img)
title_icon = tk.Label(title_bar, image=tk_img)
title_icon.img = tk_img
title_icon.pack(side="left", padx=5)
title_label.pack(side="left", padx=5)

# add a button to close the window
close_button = ttk.Button(title_bar, text="X", style="TitleBarButton.TButton", command=on_closing)
minimize_button = ttk.Button(title_bar, text="—", style="TitleBarButton.TButton", command=minimize_window)

close_button.pack(side="right", padx=5)
minimize_button.pack(side="right", padx=5)

def set_appwindow():
    global hasstyle
    GWL_EXSTYLE=-20
    WS_EX_APPWINDOW=0x00040000
    WS_EX_TOOLWINDOW=0x00000080
    if not hasstyle:
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        res = ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        root.withdraw()
        root.after(10, lambda:root.wm_deiconify())
        hasstyle=True

# restore the default window controls when the window is double-clicked
#def restore(event):
#    root.overrideredirect(False)

#root.bind("<Double-Button-1>", restore)
# add functionality to move the window when dragging the title bar

def move_window(event):
    x, y = root.winfo_pointerxy()
    new_x = x - root._offsetx
    new_y = y - root._offsety
    root.geometry(f"+{new_x}+{new_y}")
    root.update_idletasks()
    root.wm_attributes("-topmost", True)

def start_moving_window(event):
    root._offsetx = event.x
    root._offsety = event.y

def stop_moving_window(event):
    root.wm_attributes("-topmost", False)

title_bar.bind("<B1-Motion>", move_window)
title_bar.bind("<Button-1>", start_moving_window)
title_bar.bind("<ButtonRelease-1>", stop_moving_window)

frame = ttk.Frame(root, padding=25)
frame.pack(fill='both', expand='yes')
root.resizable(False, False)
root.update()

wicon = ctypes.windll.shell32.ShellExecuteW(None, "open", "icon.ico", None, None, 0)
root.wm_iconbitmap('icon.ico')

#title = ttk.Label(frame, text='Last.fm Presence Settings', anchor='w')
#title.config(font=(400))
#title.pack(fill='x', pady=5)

settings_frame = ttk.LabelFrame(frame, text='Settings', padding=10)
settings_frame.pack(side="left", fill='x', padx=10)
settings_label = ttk.Label(settings_frame, text="Profile")
settings_label.config(font=(20))
settings_label.pack(fill='y')

# API Key
api_key_label = ttk.Label(settings_frame, text="API Key:")
api_key_label.pack(fill='x', pady=5)  # pack the label before the entry widget
api_key_entry = ttk.Entry(settings_frame)
api_key_entry.insert(0, config["api_key"])
api_key_entry.pack(fill='x', pady=5)

# Username
username_label = ttk.Label(settings_frame, text="Username:")
username_label.pack(fill='x', pady=5)
username_entry = ttk.Entry(settings_frame)
username_entry.insert(0, config["username"])
username_entry.pack(fill='x', pady=5)

# Client ID
client_id_label = ttk.Label(settings_frame, text="Client ID:")
client_id_label.pack(fill='x', pady=5)
client_id_entry = ttk.Entry(settings_frame)
client_id_entry.insert(0, config["client_id"])
client_id_entry.pack(fill='x', pady=5)

# Customization frame
customization_frame = ttk.LabelFrame(frame, text='Looks', padding=10)
customization_frame.pack(fill='x')

# Customization title
customize_label = ttk.Label(customization_frame, text="Customization")
customize_label.config(font=(20))
customize_label.pack(fill='y', pady=5)

# Button Text
button_text_label = ttk.Label(customization_frame, text="Button Text:")
button_text_label.pack(fill="x", pady=5)
button_text_entry = ttk.Entry(customization_frame)
button_text_entry.insert(0, config["button_text"])
button_text_entry.pack(fill="x", pady=5)

# Button URL
button_url_label = ttk.Label(customization_frame, text="Button URL:")
button_url_label.pack(fill="x", pady=5)
button_url_entry = ttk.Entry(customization_frame)
button_url_entry.insert(0, config["button_url"])
button_url_entry.pack(fill="x", pady=5)

# Small Image Avatar
small_image_avatar_label = ttk.Label(customization_frame, text="Small Image Avatar")
small_image_avatar_label.pack(side='left', pady=5)
small_image_avatar = tk.BooleanVar(value=config["small_image_avatar"])
small_image_avatar_checkbox = ttk.Checkbutton(customization_frame, variable=small_image_avatar)
small_image_avatar_checkbox.pack(side='left', padx=(10,0), pady=5)

# Start/Stop Button
btn_frame = ttk.Frame(frame)
start_stop_button = ttk.Button(btn_frame, text="Start Presence", command=start_stop_presence)
start_stop_button.pack(side='left', padx=0, pady=5)
btn_frame.pack(fill='x')

# Save Button
save_button = ttk.Button(btn_frame, text="Save Settings", command=save_settings)
save_button.pack(side='left', padx=5, pady=5)

frame.columnconfigure(0, weight=1)
frame.rowconfigure(1, weight=1)

def create_tray_icon():

    image = Image.open("icon.ico")
    menu = (pystray.MenuItem("Show/Hide", on_clicked),
            pystray.MenuItem("Quit", on_closing))

    icon = pystray.Icon("LastFM", image, "hello there!!", menu)

    icon.run()

def run_window():
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    hasstyle = False
    root.update_idletasks()
    root.withdraw()
    root.mainloop()

set_appwindow()
run_window()