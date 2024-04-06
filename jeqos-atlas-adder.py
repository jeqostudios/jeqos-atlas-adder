import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Treeview
import shutil
import zipfile

def create_blocks_json(resource_pack_path):
    # Create 'atlases' folder if it doesn't exist
    atlases_folder = os.path.join(resource_pack_path, "assets", "minecraft", "atlases")
    os.makedirs(atlases_folder, exist_ok=True)

    # Create blocks.json file inside 'atlases' folder
    blocks_file_path = os.path.join(atlases_folder, "blocks.json")
    atlas_data = {"sources": []}

    # Scan each directory inside <selected-pack>/assets/
    assets_dir = os.path.join(resource_pack_path, "assets")
    if os.path.exists(assets_dir):
        for root, dirs, files in os.walk(assets_dir):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                textures_dir = os.path.join(dir_path, "textures")
                if os.path.exists(textures_dir):
                    for texture_root, texture_dirs, texture_files in os.walk(textures_dir):
                        for texture_dir_name in texture_dirs:
                            print("Adding source:", texture_dir_name)
                            source_path = os.path.relpath(os.path.join(dir_path, "textures", texture_dir_name), assets_dir)
                            # Removing leading directories from source_path
                            while "\\" in source_path:
                                source_path = source_path[source_path.index("\\") + 1:]
                            atlas_data["sources"].append({
                                "source": texture_dir_name,
                                "prefix": source_path,  # No trailing slash
                                "type": "directory"
                            })

    # Write atlas_data to blocks.json, overwriting existing file
    with open(blocks_file_path, "w") as f:
        json.dump(atlas_data, f, indent=4)

    show_confirmation(f"Atlas added/updated for '{os.path.basename(resource_pack_path)}.'", "#4CAF50")

    # Schedule the fade out after 3 seconds
    main_window.after(3000, fade_out_confirmation)

def fade_out_confirmation():
    banner_label.config(text="", bg="#222")  # Reset the banner

def resource_pack_selected(event):
    selected_item = json_files_treeview.selection()
    if selected_item:
        resource_pack_path = json_files_treeview.item(selected_item, "text")
        current_banner_text = banner_label.cget("text")
        if not current_banner_text or not current_banner_text.startswith("Refreshing") and not current_banner_text.startswith("Selected"):
            banner_label.config(text=f"Selected: {os.path.basename(resource_pack_path)}", bg="#222", fg="white")

def update_treeview():
    json_files_treeview.delete(*json_files_treeview.get_children())
    current_directory = os.path.dirname(os.path.abspath(__file__))
    for item in os.listdir(current_directory):
        if os.path.isdir(os.path.join(current_directory, item)):
            pack_mcmeta_path = os.path.join(current_directory, item, "pack.mcmeta")
            if os.path.exists(pack_mcmeta_path):
                json_files_treeview.insert("", "end", text=item)

def show_confirmation(message, bg):
    banner_label.config(text=message, bg=bg, fg="white")

    # Schedule the fade out after 3 seconds
    main_window.after(3000, fade_out_confirmation)

def show_error_banner(message):
    banner_label.config(text=message, bg="#d90b20", fg="white")

    # Schedule the fade out after 3 seconds
    main_window.after(3000, fade_out_confirmation)

def show_info_banner(message):
    banner_label.config(text=message, bg="#0b80d9", fg="white")

    # Schedule the fade out after 3 seconds
    main_window.after(3000, fade_out_confirmation)

def on_title_bar_drag_start(event):
    global _drag_start_x, _drag_start_y
    _drag_start_x = event.x
    _drag_start_y = event.y

def on_title_bar_drag(event):
    x = main_window.winfo_x() + event.x - _drag_start_x
    y = main_window.winfo_y() + event.y - _drag_start_y
    main_window.geometry(f"+{x}+{y}")

def refresh_directories():
    update_treeview()
    show_info_banner("Resource pack list refreshed.")

def create_atlas():
    selected_item = json_files_treeview.selection()
    if selected_item:
        resource_pack_path = json_files_treeview.item(selected_item, "text")
        if not any(dirpath.endswith("textures") for dirpath, _, _ in os.walk(resource_pack_path)):
            show_error_banner("This pack has no textures.")
        else:
            create_blocks_json(resource_pack_path)
    else:
        show_error_banner("Select a resource pack.")

def zip_resource_pack():
    selected_item = json_files_treeview.selection()
    if selected_item:
        resource_pack_path = json_files_treeview.item(selected_item, "text")
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

# Set the current working directory to the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

main_window = tk.Tk()
main_window.title("Jeqo's Atlas Adder")
main_window.configure(bg="#111")  # Set dark background color
main_window.overrideredirect(True)  # Hide default title bar

# Calculate the position of the window to center it on the screen
screen_width = main_window.winfo_screenwidth()
screen_height = main_window.winfo_screenheight()
window_width = 400  # Set your desired window width
window_height = 505  # Set your desired window height
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2
main_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Create custom title bar
title_bar = tk.Frame(main_window, bg="#222", relief="raised", bd=0, padx=0, pady=0)  # Adjust padding here
title_label = tk.Label(title_bar, text="Jeqo's Atlas Adder (JAA)", bg="#222", fg="white", padx=6, pady=6)
close_button = tk.Button(title_bar, text="X", command=main_window.quit, bg="#222", fg="white", relief="flat", padx=12, pady=6, activebackground="#d90b20", activeforeground="white", font=("Arial", 10, "bold"), borderwidth=0)
title_bar.pack(fill="x")

title_label.pack(side="left")
close_button.pack(side="right")

# Make the custom title bar draggable
title_bar.bind("<Button-1>", on_title_bar_drag_start)
title_bar.bind("<B1-Motion>", on_title_bar_drag)

# Create a frame to contain the contents with padding
content_frame = tk.Frame(main_window, bg="#111", padx=30, pady=30)
content_frame.pack(expand=True, fill="both")

# Resource Packs Label
json_files_label = tk.Label(content_frame, text="Resource Packs:", bg="#111", fg="white")
json_files_label.pack(pady=(10, 10), anchor="w")

# Treeview
json_files_treeview = Treeview(content_frame, selectmode="browse", columns=("Name",), show="tree")
json_files_treeview.heading("#0", text="Resource Packs")
json_files_treeview.pack(pady=(0, 10))

json_files_treeview.bind("<<TreeviewSelect>>", resource_pack_selected)

update_treeview()

# Refresh Button
refresh_button = tk.Button(content_frame, text="Refresh", command=refresh_directories, bg="#333", fg="white", activebackground="#444", activeforeground="white", relief=tk.FLAT, width=120)
refresh_button.pack(pady=(0, 30))

# Add Atlas Button
select_button = tk.Button(content_frame, text="Add/Update Atlas", command=create_atlas, bg="#333", fg="white", activebackground="#444", activeforeground="white", relief=tk.FLAT, width=120)
select_button.pack(pady=(0, 10))

zip_button = tk.Button(content_frame, text="Zip Resource Pack", command=zip_resource_pack, bg="#333", fg="white", activebackground="#444", activeforeground="white", relief=tk.FLAT, width=120)
zip_button.pack(pady=(0, 0))

banner_label = tk.Label(main_window, text="", bg="#222", fg="white", padx=6, pady=6)  # Banner label
banner_label.pack(fill="x")

main_window.mainloop()