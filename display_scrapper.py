import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import sys


# Function to execute the PowerShell script and get new data
def execute_scraper():
    script_path = os.path.join(sys._MEIPASS, "scrapper.ps1") if getattr(sys, 'frozen', False) else "scrapper.ps1"
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path])

# Function to load data from JSON file
def load_data(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        populate_tree(tree, "", data)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load data: {e}")

# Function to format key names
def format_key(key):
    return key.replace("_", " ").title()

# Function to populate tree view
def populate_tree(tree, parent, data):
    global tree_data
    tree.delete(*tree.get_children())
    tree_data.clear()
    if isinstance(data, dict):
        for key, value in data.items():
            node = tree.insert(parent, "end", text=format_key(key), open=False)
            tree_data[node] = value

# Function to format data for better readability
def format_data(data):
    if isinstance(data, list):
        return "\n".join([json.dumps(item, indent=2) for item in data])
    elif isinstance(data, dict):
        return json.dumps(data, indent=2)
    return str(data)

# Function to display selected data
def on_tree_select(event):
    selected_item = tree.focus()
    if selected_item in tree_data:
        formatted_text = format_data(tree_data[selected_item])
        detail_text.config(state=tk.NORMAL)
        detail_text.delete(1.0, tk.END)
        detail_text.insert(tk.END, formatted_text)
        detail_text.config(state=tk.DISABLED)

# Function to open an existing JSON file
def open_file():
    filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
    if filepath:
        load_data(filepath)

# Initialize GUI
root = tk.Tk()
root.title("Scraper Data Viewer")
root.geometry("1000x600")

# Menu Bar
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Extract Data", command=execute_scraper)
file_menu.add_command(label="Open Data File", command=open_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)
root.config(menu=menu_bar)

# Main Layout
frame = tk.PanedWindow(root, orient=tk.HORIZONTAL)
frame.pack(fill=tk.BOTH, expand=True)

# Left Pane (Tree View Navigation)
left_pane = tk.Frame(frame, width=250, bg="#f0f0f0")
frame.add(left_pane)

tree = ttk.Treeview(left_pane)
tree.pack(fill=tk.BOTH, expand=True)
tree.bind("<<TreeviewSelect>>", on_tree_select)

# Right Pane (Details View)
right_pane = tk.Frame(frame)
frame.add(right_pane)

header_label = tk.Label(right_pane, text="Details", font=("Arial", 16))
header_label.pack(pady=5)

# Scrollable Text Widget
text_frame = tk.Frame(right_pane)
text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

detail_text = tk.Text(text_frame, wrap=tk.WORD, font=("Arial", 12), state=tk.DISABLED)
detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar_y = ttk.Scrollbar(text_frame, command=detail_text.yview)
scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
detail_text.config(yscrollcommand=scrollbar_y.set)

scrollbar_x = ttk.Scrollbar(right_pane, orient=tk.HORIZONTAL, command=detail_text.xview)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
detail_text.config(xscrollcommand=scrollbar_x.set)

# Data Storage
tree_data = {}

# Start GUI
root.mainloop()
