import os
import ctypes
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from threading import Thread, Event
import subprocess
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import random
import csv
from datetime import datetime
import time
import json
from idlelib.tooltip import Hovertip

class FileSearcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Search Tool")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        self.style = ttk.Style()
        self.style.theme_use('cyborg')  # Initial theme set to 'cyborg'

        self.searching = False  # Flag to indicate if a search is in progress
        self.include_hidden = tk.BooleanVar(value=False)  # Variable for the checkbox
        self.stop_event = Event()
        self.create_widgets()
        self.drives = self.get_drives()
        self.fake_percent = 0  # Initialize fake progress percentage
        self.search_history = []  # Initialize search history
        self.phrases = [
            "Patience is a form of wisdom. It demonstrates that we understand and accept the fact that sometimes things must unfold in their own time. - Jon Kabat-Zinn",
            "Nothing ever goes away until it teaches us what we need to know. - Pema Chödrön",
            "Your mind will answer most questions if you learn to relax & wait for the answer. - William S. Burroughs",
            "Hurrying around in search of contentment seemed a perfect way of ensuring I'd never be settled or content. - Pico Iyer",
            "You must first have a lot of patience to learn to have patience. - Stanislaw Jerzy Lee",
            "Endurance is patience concentrated. - Thomas Carlyle",
            "Even a snail will eventually reach its destination. - Gail Tsukiyama",
            "There is no road too long to the man who advances deliberately and without undue haste; there are no honors too distant to the man who prepares himself for them with patience. - Jean de la Bruyère",
            "How many a man has thrown up his hands at a time when a little more effort, a little more patience would have achieved success. - Elbert Hubbard",
            "Sometimes things aren't clear right away. That's where you need to be patient and persevere and see where things lead. - Mary Pierce",
            "One moment of patience may ward off great disaster. One moment of impatience may ruin a whole life. - Chinese Proverb",
            "Whoever is out of patience is out of possession of their soul. - Francis Bacon",
            "The two most powerful warriors are patience and time. - Leo Tolstoy",
            "Patience is not simply the ability to wait - it's how we behave while we're waiting. - Joyce Meyer",
            "Rivers know this: there is no hurry. We shall get there some day. - A.A. Milne",
            "Life is full of challenges, but I always have the Three Ps: Passion, patience and persistence. And the fourth one is pizza. - Butch Hartman",
            "Perfection is attained by slow degrees; she requires the hand of time. - Voltaire",
            "It is strange that the years teach us patience; that the shorter our time, the greater our capacity for waiting. - Elizabeth Taylor",
            "The greatest power is often simple patience. - E. Joseph Cossman",
            "Trees that are slow to grow bear the best fruit. - Moliere",
            "The key to everything is patience. You get the chicken by hatching the egg, not by smashing it. - Arnold H. Glasow",
            "Slow and steady wins the race. - Aesop",
            "Patience is a conquering virtue. - Geoffrey Chaucer",
            "Patience is waiting. Not passively waiting. That is laziness. But to keep going when the going is hard and slow - that is patience. - Leo Tolstoy",
            "Patience is the support of weakness; impatience the ruin of strength. - Charles Caleb Colton",
            "Genius is eternal patience. - Michelangelo",
            "Come what may, all bad fortune is to be conquered by endurance. - Virgil",
            "Patience, that blending of moral courage with physical timidity. - Thomas Hardy",
            "Learning patience can be a difficult experience, but once conquered, you will find life is easier. - Catherine Pulsifer",
            "To lose patience is to lose the battle. - Mahatma Gandhi",
            "All men commend patience, although few are willing to practice it. - Thomas a Kempis",
            "When it comes to patience, we don't have to change old habits; we can build better ones. - Sue Bender",
            "No, I will be the pattern of all patience; I will say nothing. - William Shakespeare",
            "I am extraordinarily patient, provided I get my own way in the end. - Margaret Thatcher",
            "We could never learn to be brave and patient, if there were only joy in the world. - Helen Keller",
            "Adopt the pace of nature; her secret is patience. - Ralph Waldo Emerson",
            "Everyone wants a revolution. No one wants to do the dishes. - Tish Harrison Warren",
            "When people are waiting, they are bad judges of time, and every half minute seems like five. - Jane Austen"
        ]

    def create_widgets(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Create frames for search criteria and results side by side
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="both", expand=True)
        top_frame.grid_rowconfigure(0, weight=1)
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)

        # Create search criteria frame
        criteria_frame = ttk.Labelframe(top_frame, text="Search Criteria", padding=10)
        criteria_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        criteria_frame.columnconfigure(1, weight=1)
        criteria_frame.rowconfigure(12, weight=1)  # Make the last row expandable

        ttk.Label(criteria_frame, text="Text in File Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.text_var = tk.StringVar()
        text_entry = ttk.Entry(criteria_frame, textvariable=self.text_var)
        text_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        text_entry.bind("<Return>", lambda event: self.start_search())
        Hovertip(text_entry, "Enter text to search for in the file names.")

        ttk.Label(criteria_frame, text="File Extension:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.ext_var = tk.StringVar()
        ext_entry = ttk.Entry(criteria_frame, textvariable=self.ext_var)
        ext_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ext_entry.bind("<Return>", lambda event: self.start_search())
        Hovertip(ext_entry, "Enter file extension to search for (e.g., .txt, .pdf).")

        ttk.Label(criteria_frame, text="Search in Drive:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.drive_var = tk.StringVar()
        self.drive_combobox = ttk.Combobox(criteria_frame, textvariable=self.drive_var)
        self.drive_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.drive_combobox.bind("<<ComboboxSelected>>", self.populate_folders)
        Hovertip(self.drive_combobox, "Select the drive to search in.")

        ttk.Label(criteria_frame, text="Select Folder:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.folder_var = tk.StringVar()
        self.folder_combobox = ttk.Combobox(criteria_frame, textvariable=self.folder_var)
        self.folder_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.folder_combobox['values'] = ['Entire Directory']
        Hovertip(self.folder_combobox, "Select the folder to search in. 'Entire Directory' searches the whole drive.")

        # Checkbox for hidden folders
        hidden_check = ttk.Checkbutton(criteria_frame, text="Search Hidden Folders", variable=self.include_hidden)
        hidden_check.grid(row=4, column=0, columnspan=2, pady=5)
        Hovertip(hidden_check, "Check this box to include hidden folders in the search.")

        # Additional filters
        ttk.Label(criteria_frame, text="Min File Size (KB):").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.min_size_var = tk.StringVar()
        min_size_entry = ttk.Entry(criteria_frame, textvariable=self.min_size_var)
        min_size_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        Hovertip(min_size_entry, "Enter the minimum file size in KB.")

        ttk.Label(criteria_frame, text="Max File Size (KB):").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.max_size_var = tk.StringVar()
        max_size_entry = ttk.Entry(criteria_frame, textvariable=self.max_size_var)
        max_size_entry.grid(row=6, column=1, padx=5, pady=5, sticky="ew")
        Hovertip(max_size_entry, "Enter the maximum file size in KB.")

        ttk.Label(criteria_frame, text="Date Modified After (dd/mm/yyyy):").grid(row=7, column=0, padx=5, pady=5, sticky="e")
        self.date_after_var = tk.StringVar()
        date_after_entry = ttk.Entry(criteria_frame, textvariable=self.date_after_var)
        date_after_entry.grid(row=7, column=1, padx=5, pady=5, sticky="ew")
        Hovertip(date_after_entry, "Enter the earliest date modified (dd/mm/yyyy).")

        ttk.Label(criteria_frame, text="Date Modified Before (dd/mm/yyyy):").grid(row=8, column=0, padx=5, pady=5, sticky="e")
        self.date_before_var = tk.StringVar()
        date_before_entry = ttk.Entry(criteria_frame, textvariable=self.date_before_var)
        date_before_entry.grid(row=8, column=1, padx=5, pady=5, sticky="ew")
        Hovertip(date_before_entry, "Enter the latest date modified (dd/mm/yyyy).")

        # Progress bar and percentage label
        self.progress_var = tk.DoubleVar()
        self.progress_label_var = tk.StringVar()
        
        self.progress_label = ttk.Label(criteria_frame, textvariable=self.progress_label_var)
        self.progress_label.grid(row=9, column=0, columnspan=2)

        self.progress_bar = ttk.Progressbar(criteria_frame, mode='determinate', variable=self.progress_var, length=400)
        self.progress_bar.grid(row=10, column=0, columnspan=2, pady=10)

        button_frame = ttk.Frame(criteria_frame)
        button_frame.grid(row=11, column=0, columnspan=2, pady=10)
        search_btn = ttk.Button(button_frame, text="Search", command=self.start_search)
        search_btn.pack(side='left', padx=5)
        Hovertip(search_btn, "Click to start the search.")
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel_search)
        cancel_btn.pack(side='left', padx=5)
        Hovertip(cancel_btn, "Click to cancel the search.")
        
        save_btn = ttk.Button(button_frame, text="Save Settings", command=self.save_settings)
        save_btn.pack(side='left', padx=5)
        Hovertip(save_btn, "Click to save the current search settings.")
        
        load_btn = ttk.Button(button_frame, text="Load Settings", command=self.load_settings)
        load_btn.pack(side='left', padx=5)
        Hovertip(load_btn, "Click to load saved search settings.")
        
        export_btn = ttk.Button(button_frame, text="Export Results", command=self.export_results)
        export_btn.pack(side='left', padx=5)
        Hovertip(export_btn, "Click to export the search results to a CSV file.")

        # Fun phrases label with fixed width
        self.fun_phrase_var = tk.StringVar()
        self.fun_phrase_label = ttk.Label(criteria_frame, textvariable=self.fun_phrase_var, font=("Helvetica", 10, "italic"), wraplength=400, justify="left")
        self.fun_phrase_label.grid(row=12, column=0, columnspan=2, pady=5, sticky="w")

        # Results and Preview
        result_frame = ttk.Labelframe(top_frame, text="Search Results", padding=10)
        result_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(2, weight=1)  # Make the result box expandable

        click_label = ttk.Label(result_frame, text="Click to open folder")
        click_label.grid(row=0, column=0, padx=5, pady=5)

        self.result_count_var = tk.StringVar()
        self.result_count_label = ttk.Label(result_frame, textvariable=self.result_count_var)
        self.result_count_label.grid(row=1, column=0, padx=5, pady=5)

        self.result_box = tk.Text(result_frame, wrap='word')
        self.result_box.grid(row=2, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(result_frame, command=self.result_box.yview)
        self.scrollbar.grid(row=2, column=1, sticky="ns")

        self.result_box.config(yscrollcommand=self.scrollbar.set)
        self.result_box.bind("<Button-1>", self.handle_click)

        # Configure the tag for highlighting
        self.result_box.tag_configure('highlight', background='lightblue')

        # Context Menu
        self.context_menu = tk.Menu(self.result_box, tearoff=0)
        self.context_menu.add_command(label="Open", command=self.open_selected_file)
        self.context_menu.add_command(label="Copy Path", command=self.copy_path_to_clipboard)
        self.result_box.bind("<Button-3>", self.show_context_menu)

        # Add "by Ryan Hall" in the lower right
        made_by_label = ttk.Label(self.root, text="by Ryan Hall", font=("Helvetica", 8))
        made_by_label.pack(side="bottom", anchor="se", padx=10, pady=5)

        # Make the progress bar darker when empty
        self.style.configure("TProgressbar", troughcolor='gray', thickness=15)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")
        self.set_status("Ready")

    def get_drives(self):
        drives = []
        bitmask = os.popen('wmic logicaldisk get caption').read().split()
        for drive in bitmask:
            if ':' in drive:
                drives.append(drive + '\\')
        self.drive_combobox['values'] = drives
        if drives:
            self.drive_combobox.current(0)
        return drives

    def populate_folders(self, event):
        drive = self.drive_var.get()
        if not drive:
            return
        folders = ['Entire Directory'] + [f for f in os.listdir(drive) if os.path.isdir(os.path.join(drive, f)) and not self.is_hidden(os.path.join(drive, f))]
        self.folder_combobox['values'] = folders
        if folders:
            self.folder_combobox.current(0)
        else:
            self.folder_combobox.set('')

    def start_search(self):
        if self.searching:
            return
        self.searching = True
        self.stop_event.clear()
        self.fake_percent = 0
        self.progress_var.set(0)
        self.progress_label_var.set("0.0%")
        self.result_count_var.set("Total Results: 0")
        self.result_box.delete(1.0, tk.END)
        self.set_status("Searching...")
        search_thread = Thread(target=self.search_files)
        search_thread.start()
        fake_progress_thread = Thread(target=self.fake_progress)
        fake_progress_thread.start()
        fun_phrases_thread = Thread(target=self.display_fun_phrases)
        fun_phrases_thread.start()

    def cancel_search(self):
        self.searching = False
        self.stop_event.set()
        self.set_status("Search interrupted")
        self.progress_label_var.set("Search interrupted")
        self.fun_phrase_var.set("")  # Clear fun phrases

    def fake_progress(self):
        while self.searching and self.fake_percent < 100:
            if self.stop_event.is_set():
                break
            self.fake_percent += 0.02  # Increase by 0.02% every second
            if self.fake_percent <= self.progress_var.get():
                self.progress_label_var.set(f"{self.progress_var.get():.1f}%")
            else:
                self.progress_label_var.set(f"{self.fake_percent:.1f}%")
            self.progress_bar["value"] = self.fake_percent
            self.root.update_idletasks()
            self.stop_event.wait(1)  # Increase every 1 second

    def display_fun_phrases(self):
        while self.searching:
            phrase = random.choice(self.phrases)
            self.fun_phrase_var.set(phrase)
            self.root.update_idletasks()
            self.stop_event.wait(15)  # Change phrase every 15 seconds
        self.fun_phrase_var.set("")  # Clear fun phrases when search stops

    def search_files(self):
        text = self.text_var.get().lower()
        ext = self.ext_var.get().lower()
        drive = self.drive_var.get()
        folder = self.folder_var.get()
        include_hidden = self.include_hidden.get()
        min_size = self.min_size_var.get()
        max_size = self.max_size_var.get()
        date_after = self.date_after_var.get()
        date_before = self.date_before_var.get()

        if not drive:
            messagebox.showwarning("Input Error", "Please select a drive to search in.")
            self.progress_var.set(0)
            self.progress_label_var.set("0.0%")
            self.searching = False
            self.set_status("Ready")
            return

        search_path = drive if folder == 'Entire Directory' else os.path.join(drive, folder)

        if not os.path.exists(search_path):
            messagebox.showwarning("Input Error", "The specified folder does not exist.")
            self.progress_var.set(0)
            self.progress_label_var.set("0.0%")
            self.searching = False
            self.set_status("Ready")
            return

        total_files = 0
        for root, dirs, files in os.walk(search_path):
            if not include_hidden:
                dirs[:] = [d for d in dirs if not self.is_hidden(os.path.join(root, d))]
            total_files += len(files)

        result = []
        processed_files = 0
        update_interval = max(total_files // 100, 1)  # Update progress bar every 1% of files
        for root, dirs, files in os.walk(search_path):
            if not self.searching:
                break
            if not include_hidden:
                dirs[:] = [d for d in dirs if not self.is_hidden(os.path.join(root, d))]
            for file in files:
                if not self.searching:
                    break
                if text in file.lower() and (not ext or file.lower().endswith(ext)):
                    full_path = os.path.join(root, file)
                    if self.file_matches_criteria(full_path, min_size, max_size, date_after, date_before):
                        result.append(full_path)
                processed_files += 1
                if processed_files % update_interval == 0:
                    progress_percent = (processed_files / total_files) * 100
                    self.progress_var.set(progress_percent)
                    if progress_percent > self.fake_percent:
                        self.progress_label_var.set(f"{progress_percent:.1f}%")
                        self.progress_bar["value"] = progress_percent
                    self.root.update_idletasks()

        self.display_results(result)
        self.search_history.append({
            'text': text,
            'ext': ext,
            'drive': drive,
            'folder': folder,
            'include_hidden': include_hidden,
            'min_size': min_size,
            'max_size': max_size,
            'date_after': date_after,
            'date_before': date_before,
            'results': result
        })
        if self.searching:  # If the search was not canceled
            self.progress_var.set(100)
            self.progress_label_var.set("100.0%")
            self.set_status("Search completed")
        self.searching = False
        self.fun_phrase_var.set("")  # Clear fun phrases

    def file_matches_criteria(self, filepath, min_size, max_size, date_after, date_before):
        file_stat = os.stat(filepath)
        if min_size and file_stat.st_size < int(min_size) * 1024:
            return False
        if max_size and file_stat.st_size > int(max_size) * 1024:
            return False
        if date_after and datetime.fromtimestamp(file_stat.st_mtime) < datetime.strptime(date_after, '%d/%m/%Y'):
            return False
        if date_before and datetime.fromtimestamp(file_stat.st_mtime) > datetime.strptime(date_before, '%d/%m/%Y'):
            return False
        return True

    def is_hidden(self, filepath):
        if os.name == 'nt':
            attribute = ctypes.windll.kernel32.GetFileAttributesW(str(filepath))
            return attribute & 2
        else:
            return os.path.basename(filepath).startswith('.')

    def display_results(self, results):
        self.result_count_var.set(f"Total Results: {len(results)}")
        if results:
            for file in results:
                self.result_box.insert(tk.END, file + "\n")
        else:
            self.result_box.insert(tk.END, "No files found.")

    def handle_click(self, event):
        self.result_box.tag_remove('highlight', '1.0', tk.END)  # Remove previous highlights
        index = self.result_box.index("@%s,%s" % (event.x, event.y))
        line_start = self.result_box.index("%s linestart" % index)
        line_end = self.result_box.index("%s lineend" % index)
        self.result_box.tag_add('highlight', line_start, line_end)
        
        line = self.result_box.get(line_start, line_end).strip()
        if os.path.exists(line):
            subprocess.Popen(['explorer', '/select,', line])

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def open_selected_file(self):
        line = self.get_selected_line()
        if line and os.path.exists(line):
            subprocess.Popen(['explorer', line])

    def copy_path_to_clipboard(self):
        line = self.get_selected_line()
        if line:
            self.root.clipboard_clear()
            self.root.clipboard_append(line)

    def get_selected_line(self):
        try:
            index = self.result_box.index(tk.INSERT)
            line_start = self.result_box.index("%s linestart" % index)
            line_end = self.result_box.index("%s lineend" % index)
            return self.result_box.get(line_start, line_end).strip()
        except tk.TclError:
            return None

    def save_settings(self):
        settings = {
            'text': self.text_var.get(),
            'ext': self.ext_var.get(),
            'drive': self.drive_var.get(),
            'folder': self.folder_var.get(),
            'include_hidden': self.include_hidden.get(),
            'min_size': self.min_size_var.get(),
            'max_size': self.max_size_var.get(),
            'date_after': self.date_after_var.get(),
            'date_before': self.date_before_var.get()
        }
        settings_file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if settings_file:
            with open(settings_file, 'w') as file:
                json.dump(settings, file)
            self.set_status("Settings saved")

    def load_settings(self):
        settings_file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if settings_file:
            with open(settings_file, 'r') as file:
                settings = json.load(file)
            self.text_var.set(settings.get('text', ''))
            self.ext_var.set(settings.get('ext', ''))
            self.drive_var.set(settings.get('drive', ''))
            self.folder_var.set(settings.get('folder', ''))
            self.include_hidden.set(settings.get('include_hidden', False))
            self.min_size_var.set(settings.get('min_size', ''))
            self.max_size_var.set(settings.get('max_size', ''))
            self.date_after_var.set(settings.get('date_after', ''))
            self.date_before_var.set(settings.get('date_before', ''))
            self.set_status("Settings loaded")

    def export_results(self):
        results_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if results_file:
            with open(results_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Results"])
                for result in self.result_box.get("1.0", tk.END).strip().split("\n"):
                    writer.writerow([result])
            self.set_status("Results exported")

    def set_status(self, status):
        self.status_var.set(status)

if __name__ == "__main__":
    try:
        root = ttk.Window(themename="cyborg")
        app = FileSearcherApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", str(e))
        root.mainloop()
