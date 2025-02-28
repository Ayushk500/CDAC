import psutil
import datetime
import json
import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

def get_processes_info(progress_var):
    processes = []
    for i, proc in enumerate(psutil.process_iter(['pid', 'ppid', 'name', 'username', 'cpu_percent', 'memory_percent', 'create_time'])):
        try:
            info = proc.info
            info['memory_percent'] = round(info['memory_percent'], 2)
            info['memory_size'] = format_memory(info['memory_percent'])
            info['create_time'] = datetime.datetime.fromtimestamp(info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
            processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        progress_var.set((i + 1) / len(list(psutil.process_iter())))
    return processes

def format_memory(memory_percent):
    mem_in_kb = memory_percent * 1024
    if mem_in_kb > 1024:
        return f"{mem_in_kb / 1024:.2f} MB"
    else:
        return f"{mem_in_kb:.2f} KB"

def clean_column_name(name):
    return name.strip().replace(' ', '_')

def load_file():
    filepath = filedialog.askopenfilename(filetypes=[("All files", "*.json *.txt *.csv"), ("JSON files", "*.json"), ("Text files", "*.txt"), ("CSV files", "*.csv")])
    if filepath:
        ext = filepath.split('.')[-1].lower()
        if ext == 'json':
            with open(filepath, 'r') as file:
                processes = json.load(file)
                display_processes_info(processes)
        elif ext == 'txt':
            processes = load_txt_file(filepath)
            display_processes_info(processes)
        elif ext == 'csv':
            processes = load_csv_file(filepath)
            display_processes_info(processes)
        else:
            messagebox.showerror("File Error", "Unsupported file format.")

def load_txt_file(filepath):
    processes = []
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
            if len(lines) < 3:  # We expect at least a header and one process
                messagebox.showerror("File Error", "Invalid TXT file format.")
                return []
            for line in lines[2:]:  # Skip headers
                data = line.split()
                if len(data) >= 8:  # Ensure enough columns are present
                    try:
                        process = {
                            'ppid': data[0],
                            'pid': data[1],
                            'name': data[2],
                            'username': data[3],
                            'cpu_percent': float(data[4]),
                            'memory_percent': float(data[5]),
                            'memory_size': format_memory(float(data[5])),
                            'create_time': data[6] + " " + data[7]
                        }
                        processes.append(process)
                    except ValueError:
                        # If we can't convert cpu_percent or memory_percent, we skip the process
                        continue
                else:
                    messagebox.showerror("File Error", "Invalid data format in TXT file.")
                    return []
    except Exception as e:
        messagebox.showerror("File Error", f"An error occurred while loading TXT: {str(e)}")
    return processes

def load_csv_file(filepath):
    processes = []
    try:
        with open(filepath, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                try:
                    process = {
                        clean_column_name('ppid'): row.get('PPID', 'N/A'),
                        clean_column_name('pid'): row.get('PID', 'N/A'),
                        clean_column_name('name'): row.get('Name', 'N/A'),
                        clean_column_name('username'): row.get('User', 'N/A'),
                        clean_column_name('cpu_percent'): float(row.get('CPU (%)', 0.0)),
                        clean_column_name('memory_percent'): float(row.get('Memory (%)', 0.0)),
                        clean_column_name('memory_size'): format_memory(float(row.get('Memory (%)', 0.0))),
                        clean_column_name('create_time'): row.get('Start Time', 'N/A')
                    }
                    processes.append(process)
                except ValueError:
                    # Skip rows where float conversion fails
                    continue
    except Exception as e:
        messagebox.showerror("File Error", f"An error occurred while loading CSV: {str(e)}")
    return processes

def display_processes_info(processes):
    if not processes:
        messagebox.showwarning("No Data", "No valid processes to display.")
        return

    columns = [clean_column_name(col) for col in processes[0].keys()]
    tree["columns"] = columns
    for col in tree["columns"]:
        tree.heading(col, text=col.replace('_', ' '), command=lambda c=col: sort_tree(c, False))
        tree.column(col, width=150, anchor='center')

    for i in tree.get_children():
        tree.delete(i)

    for proc in processes:
        tree.insert("", "end", values=[proc[col] for col in columns])

    for col in columns:
        tree.heading(col, text=col.replace('_', ' '), anchor='w')

def find_process():
    search_text = entry.get().strip().lower()
    if not search_text:
        messagebox.showwarning("Input Error", "Please enter a search term.")
        return

    matches = False
    for item in tree.get_children():
        values = tree.item(item, "values")
        if search_text in str(values).lower():
            tree.selection_add(item)
            tree.see(item)
            matches = True

    if not matches:
        messagebox.showinfo("Not Found", "No matching process found.")

def sort_tree(column, reverse):
    data = [(tree.set(child, column), child) for child in tree.get_children('')]
    data.sort(key=lambda x: (float(x[0]) if x[0].replace('.', '', 1).isdigit() else x[0]), reverse=reverse)
    for index, (val, child) in enumerate(data):
        tree.move(child, '', index)
    tree.heading(column, command=lambda: sort_tree(column, not reverse))

def extract_live_processes():
    progress_var.set(0)
    progress_bar.start()
    threading.Thread(target=lambda: save_file(get_processes_info(progress_var))).start()

def save_file(processes):
    progress_bar.stop()
    filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("CSV files", "*.csv")])
    if filepath:
        ext = filepath.split('.')[-1].lower()
        if ext == 'json':
            with open(filepath, 'w') as file:
                json.dump(processes, file, indent=4)
        elif ext == 'txt':
            with open(filepath, 'w') as file:
                file.write("PPID PID NAME USERNAME CPU_PERCENT MEMORY_PERCENT MEMORY_SIZE CREATE_TIME\n")
                for proc in processes:
                    file.write(f"{proc['ppid']} {proc['pid']} {proc['name']} {proc['username']} {proc['cpu_percent']} {proc['memory_percent']} {proc['memory_size']} {proc['create_time']}\n")
        elif ext == 'csv':
            with open(filepath, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=processes[0].keys())
                writer.writeheader()
                writer.writerows(processes)
        else:
            messagebox.showerror("File Error", "Unsupported file format.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Process Viewer")
    root.geometry("1024x768")

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"), foreground="black")
    style.configure("Treeview", font=("Arial", 10), foreground="black")  # Set the text color for the data rows

    frame = tk.Frame(root)
    frame.pack(pady=20)

    load_button = tk.Button(frame, text="Load File", command=load_file)
    load_button.pack(side=tk.LEFT)

    extract_button = tk.Button(frame, text="Extract Live Processes", command=extract_live_processes)
    extract_button.pack(side=tk.LEFT, padx=5)

    find_label = tk.Label(frame, text="Find:")
    find_label.pack(side=tk.LEFT, padx=5)

    entry = tk.Entry(frame)
    entry.pack(side=tk.LEFT, padx=5)

    find_button = tk.Button(frame, text="Find", command=find_process)
    find_button.pack(side=tk.LEFT, padx=5)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=1.0)
    progress_bar.pack(fill=tk.X, pady=10)

    columns = ()
    tree = ttk.Treeview(root, columns=columns, show='headings')
    vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    vsb.pack(side='right', fill='y')
    hsb.pack(side='bottom', fill='x')
    tree.pack(fill=tk.BOTH, expand=True)

    root.mainloop()
