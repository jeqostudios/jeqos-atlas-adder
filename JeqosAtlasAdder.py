import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import requests
except ImportError:
    install("requests")
    import requests
    
import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Treeview
import shutil
import zipfile
import requests
import webbrowser
import sys

current_version = "1.1.0"

main_window = tk.Tk()

banner_label = tk.Label(main_window, text="", bg="#111", fg="white", padx=10, pady=10)  
banner_label.pack(fill="x", side="bottom")

github_release_url = "https://github.com/jeqostudios/jeqos-atlas-adder/releases/latest"

def check_latest_version(release_url):
    try:
        response = requests.get(release_url, allow_redirects=False)
        response.raise_for_status()
        latest_version = response.headers['Location'].split('/')[-1]
        return latest_version
    except Exception as e:
        show_error_banner(f"Failed to retrieve latest info from GitHub: {str(e)}")
        return None

def compare_versions(current_version, latest_version):
    current_version = current_version.lstrip("v")
    latest_version = latest_version.lstrip("v")
    return current_version < latest_version

latest_version = check_latest_version(github_release_url)

if latest_version:
    if compare_versions(current_version, latest_version):
        banner_label.config(text="A newer version is available. Click here to view page.", bg="#d90b20", fg="white")
        main_window.after(5000, lambda: banner_label.config(text="", bg="#111"))
else:
    banner_label.config(text="Failed to retrieve latest info from GitHub.", bg="#d90b20", fg="white")
    main_window.after(5000, lambda: banner_label.config(text="", bg="#111"))

def update_banner(event):
    if banner_label.cget("text") == "A newer version is available. Click here to view page.":
        webbrowser.open("https://jeqo.net/atlas-adder")

banner_label.bind("<Button-1>", update_banner)

def create_blocks_json(resource_pack_path):
    atlases_folder = os.path.join(resource_pack_path, "assets", "minecraft", "atlases")
    os.makedirs(atlases_folder, exist_ok=True)

    blocks_file_path = os.path.join(atlases_folder, "blocks.json")
    blocks_json_exists = os.path.exists(blocks_file_path)

    atlas_data = {"sources": []}

    textures_dir = os.path.join(resource_pack_path, "assets", "minecraft", "textures")
    if os.path.exists(textures_dir):
        for root, dirs, files in os.walk(textures_dir):
            for texture_dir_name in dirs:
                show_info_banner("Adding source: " + texture_dir_name)
                source_path = os.path.relpath(os.path.join(root, texture_dir_name), textures_dir)
                atlas_data["sources"].append({
                    "source": texture_dir_name,
                    "prefix": source_path.replace("\\", "/"),  # Replace backslashes with forward slashes
                    "type": "directory"
                })

    with open(blocks_file_path, "w") as f:
        json.dump(atlas_data, f, indent=4)

    if blocks_json_exists:
        show_confirmation(f"Atlas updated for '{os.path.basename(resource_pack_path)}.'", "#4CAF50")
    else:
        show_confirmation(f"Atlas added to '{os.path.basename(resource_pack_path)}.'", "#4CAF50")

    main_window.after(3000, reset_banner)

def select_directory():
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        initial_dir = os.path.dirname(sys.executable)
    else:
        # Running as Python script
        initial_dir = os.getcwd()
    
    selected_directory = filedialog.askdirectory(initialdir=initial_dir)
    
    if selected_directory:
        update_listbox(selected_directory)
        show_info_banner("Resource pack directory selected.")
    else:
        show_error_banner("No directory selected.")

def update_listbox(directory):
    json_files_listbox.delete(0, tk.END)
    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            if 'pack.mcmeta' in files:
                json_files_listbox.insert(tk.END, os.path.basename(root))
    else:
        show_error_banner("Invalid directory.")

def on_title_bar_drag_start(event):
    global _drag_start_x, _drag_start_y
    _drag_start_x = event.x
    _drag_start_y = event.y

def on_title_bar_drag(event):
    x = main_window.winfo_x() + event.x - _drag_start_x
    y = main_window.winfo_y() + event.y - _drag_start_y
    main_window.geometry(f"+{x}+{y}")

def create_atlas():
    selected_item = json_files_listbox.curselection()
    if selected_item:
        resource_pack_path = json_files_listbox.get(selected_item)
        if not any(dirpath.endswith("textures") for dirpath, _, _ in os.walk(resource_pack_path)):
            show_error_banner("This pack has no textures.")
        else:
            create_blocks_json(resource_pack_path)
    else:
        show_error_banner("Select a resource pack.")

def zip_resource_pack():
    selected_item = json_files_listbox.curselection()
    if selected_item:
        resource_pack_path = json_files_listbox.get(selected_item)
        zip_filename = os.path.basename(resource_pack_path) + ".zip"
        with zipfile.ZipFile(zip_filename, "w") as zipf:
            for root, dirs, files in os.walk(resource_pack_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, resource_pack_path)
                    zipf.write(file_path, arcname=arcname)
        show_confirmation(f"'{os.path.basename(resource_pack_path)}' successfully zipped.", "#4CAF50")
    else:
        show_error_banner("Select a resource pack.")

def on_hover_close(event):
    close_button.config(bg="#d90b20")

def on_leave_close(event):
    close_button.config(bg="#1d9bf0")

def show_confirmation(message, bg):
    banner_label.config(text=message, bg=bg, fg="white")
    main_window.after(3000, reset_banner)

def show_error_banner(message):
    banner_label.config(text=message, bg="#d90b20", fg="white")
    main_window.after(3000, reset_banner)

def show_info_banner(message):
    banner_label.config(text=message, bg="#0b80d9", fg="white")
    main_window.after(3000, reset_banner)

def reset_banner():
    banner_label.config(text="", bg="#111")

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

main_window.title("Jeqo's Atlas Adder")
main_window.configure(bg="#222")
main_window.overrideredirect(True)

screen_width = main_window.winfo_screenwidth()
screen_height = main_window.winfo_screenheight()
window_width = 300
window_height = 480
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2
main_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

title_bar = tk.Frame(main_window, bg="#1d9bf0", relief="raised", bd=0, padx=0, pady=0)
title_label = tk.Label(title_bar, text="Jeqo's Atlas Adder", bg="#1d9bf0", fg="white", padx=10, pady=5)
close_button = tk.Button(title_bar, text="X", command=main_window.quit, bg="#1d9bf0", fg="white", relief="flat", padx=10, pady=5, activebackground="#d90b20", activeforeground="white", font=("Arial", 10, "bold"), borderwidth=0)
title_bar.pack(fill="x")

title_label.pack(side="left")
close_button.pack(side="right")

close_button.bind("<Enter>", on_hover_close)
close_button.bind("<Leave>", on_leave_close)

title_bar.bind("<Button-1>", on_title_bar_drag_start)
title_bar.bind("<B1-Motion>", on_title_bar_drag)

content_frame = tk.Frame(main_window, bg="#222", padx=30, pady=30)
content_frame.pack(expand=True, fill="both")

json_files_label = tk.Label(content_frame, text="Resource Packs:", bg="#222", fg="white")
json_files_label.pack(pady=(0, 10), anchor="w")

json_files_listbox = tk.Listbox(content_frame, bg="#111", fg="#bbb", selectbackground="#333", selectforeground="#1d9bf0", border=0, highlightthickness=0, width=50)
json_files_listbox.pack(pady=(0, 10))

select_dir_button = tk.Button(content_frame, text="Select Directory", command=select_directory, bg="#333", fg="white", activebackground="#444", activeforeground="white", relief=tk.FLAT, width=45, padx=5, pady=5)
select_dir_button.pack(pady=(0, 30))

select_button = tk.Button(content_frame, text="Add/Update Atlas", command=create_atlas, bg="#1d9bf0", fg="white", activebackground="#197ec2", activeforeground="white", relief=tk.FLAT, width=45, padx=5, pady=5)
select_button.pack(pady=(0, 10))

zip_button = tk.Button(content_frame, text="Zip Resource Pack", command=zip_resource_pack, bg="#333", fg="white", activebackground="#444", activeforeground="white", relief=tk.FLAT, width=45, padx=5, pady=5)
zip_button.pack(pady=(0, 0))

main_window.mainloop()