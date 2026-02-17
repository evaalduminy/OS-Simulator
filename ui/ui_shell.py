# ui_shell.py (New "Top Command Bar" Design)
import tkinter as tk
import customtkinter as ctk
import os
import subprocess
import threading
import queue
import glob

class ShellWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("واجهة الأوامر (تصميم علوي)")
        self.geometry("900x600")
        self.minsize(700, 500)

        # --- State & Threading ---
        self.output_queue = queue.Queue()
        self.command_history = []
        self.history_index = 0
        
        # --- Autocomplete ---
        self.autocomplete_listbox = None
        self.known_commands = ['dir', 'echo', 'ping', 'ipconfig', 'tasklist', 'help', 'cls', 'clear', 'cd', 'exit']

        # --- Layout ---
        self.grid_rowconfigure(0, weight=0) # Input Frame (fixed size)
        self.grid_rowconfigure(1, weight=1) # Output Textbox (takes all space)
        self.grid_columnconfigure(0, weight=1)

        # --- Create Widgets ---
        self._create_input_frame()
        self._create_output_textbox()

        # --- Initial Setup ---
        self.after(100, self.process_queue)
        self.add_to_queue("مرحباً بك في واجهة الأوامر ذات التصميم العلوي.\n- اكتب الأوامر في الشريط العلوي واضغط Enter.\n- استخدم Tab للإكمال التلقائي.\n\n", "info")
        self.update_prompt()

    # =================================================================
    # 1. WIDGET CREATION
    # =================================================================
    def _create_input_frame(self):
        """Creates the top bar for command input."""
        input_frame = ctk.CTkFrame(self, corner_radius=0)
        input_frame.grid(row=0, column=0, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)
        
        self.prompt_label = ctk.CTkLabel(input_frame, text=">", font=ctk.CTkFont(family="Consolas", size=14))
        self.prompt_label.grid(row=0, column=0, padx=(10, 5), pady=10)
        
        self.command_entry = ctk.CTkEntry(input_frame, font=ctk.CTkFont(family="Consolas", size=14), border_width=0)
        self.command_entry.grid(row=0, column=1, sticky="ew", pady=10)
        
        # --- Bindings ---
        self.command_entry.bind("<Return>", self.execute_command_event)
        self.command_entry.bind("<Up>", self.history_up)
        self.command_entry.bind("<Down>", self.history_down)
        self.command_entry.bind("<KeyRelease>", self.handle_autocomplete)
        self.command_entry.bind("<Tab>", self.complete_from_listbox)
        self.bind("<Button-1>", lambda e: self.hide_autocomplete())
        self.command_entry.focus()

    def _create_output_textbox(self):
        """Creates the main area for displaying output."""
        self.output_textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=14), wrap="word", corner_radius=0)
        self.output_textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.output_textbox.configure(state="disabled")
        self._setup_text_tags()

    def _setup_text_tags(self):
        """Defines colors for syntax highlighting."""
        self.output_textbox.tag_config("prompt", foreground="#00FF00")
        self.output_textbox.tag_config("command", foreground="#87CEFA")
        self.output_textbox.tag_config("output", foreground="white")
        self.output_textbox.tag_config("error", foreground="#FF6347")
        self.output_textbox.tag_config("info", foreground="#FFFF00")

    # =================================================================
    # 2. QUEUE & COMMAND EXECUTION
    # =================================================================
    def add_to_queue(self, text, tag="output"):
        self.output_queue.put((text, tag))

    def process_queue(self):
        try:
            while not self.output_queue.empty():
                text, tag = self.output_queue.get_nowait()
                self.output_textbox.configure(state="normal")
                if text == "CLS_COMMAND":
                    self.output_textbox.delete("1.0", "end")
                else:
                    self.output_textbox.insert("end", text, tag)
                self.output_textbox.configure(state="disabled")
                self.output_textbox.see("end")
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_queue)

    def execute_command_event(self, event=None):
        if self.autocomplete_listbox and self.autocomplete_listbox.winfo_exists():
            self.complete_from_listbox()
            return "break"

        command = self.command_entry.get().strip()
        if command:
            if not self.command_history or self.command_history[-1] != command:
                self.command_history.append(command)
            self.history_index = len(self.command_history)
            
            # Print the command to the output screen before executing
            self.add_to_queue(f"\n{self.prompt_label.cget('text')} ", "prompt")
            self.add_to_queue(f"{command}\n", "command")
            
            self.run_command(command)
            self.command_entry.delete(0, "end")
        return "break"

    def run_command(self, command):
        command_parts = command.strip().split()
        cmd = command_parts[0].lower()

        # --- Built-in Commands (run in main thread) ---
        if cmd == "exit": self.destroy(); return
        if cmd in ["cls", "clear"]: self.add_to_queue("CLS_COMMAND"); return
        if cmd == "cd": self.handle_cd(command_parts); return
        if cmd == "help":
            help_text = "الأوامر المدمجة المتاحة:\n" + "\n".join(f"- {c}" for c in self.known_commands) + "\n"
            self.add_to_queue(help_text, "info")
            return

        # --- External Commands (run in a new thread) ---
        thread = threading.Thread(target=self._execute_subprocess, args=(command,))
        thread.daemon = True
        thread.start()

    def handle_cd(self, command_parts):
        try:
            path = " ".join(command_parts[1:]) if len(command_parts) > 1 else os.path.expanduser("~")
            os.chdir(path)
            self.update_prompt() # Update prompt to show new path
        except Exception as e:
            self.add_to_queue(f"خطأ في تغيير المجلد: {e}\n", "error")

    def _execute_subprocess(self, command):
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
            for line in iter(process.stdout.readline, ''):
                self.add_to_queue(line, "output")
            process.stdout.close()
            process.wait()
        except Exception as e:
            self.add_to_queue(f"حدث خطأ غير متوقع: {e}\n", "error")

    # =================================================================
    # 3. HISTORY, PROMPT, AUTOCOMPLETE
    # =================================================================
    def update_prompt(self):
        self.prompt_label.configure(text=f"{os.getcwd()}>")

    def history_up(self, event=None):
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, "end")
            self.command_entry.insert(0, self.command_history[self.history_index])
        return "break"

    def history_down(self, event=None):
        self.command_entry.delete(0, "end")
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.command_entry.insert(0, self.command_history[self.history_index])
        else:
            self.history_index = len(self.command_history)
        return "break"

    def handle_autocomplete(self, event=None):
        if event.keysym in ("Up", "Down", "Return", "Tab"): return
        self.hide_autocomplete()
        text = self.command_entry.get()
        parts = text.split()
        if not text or text.endswith(" "): return
        to_complete = parts[-1]
        suggestions = []
        if len(parts) == 1:
            suggestions = [cmd for cmd in self.known_commands if cmd.startswith(to_complete.lower())]
        else:
            path_suggestions = glob.glob(to_complete + '*')
            suggestions = [os.path.basename(p).replace('\\', '/') for p in path_suggestions]
        if suggestions: self.show_autocomplete(suggestions)

    def show_autocomplete(self, suggestions):
        self.hide_autocomplete()
        entry_x = self.command_entry.winfo_rootx()
        entry_y = self.command_entry.winfo_rooty()
        entry_height = self.command_entry.winfo_height()
        self.autocomplete_listbox = tk.Listbox(self, font=('Consolas', 12), bg="#2B2B2B", fg="white", highlightthickness=0, selectbackground="#007ACC")
        for s in suggestions: self.autocomplete_listbox.insert("end", s)
        self.autocomplete_listbox.place(x=entry_x - self.winfo_rootx(), y=entry_y - self.winfo_rooty() + entry_height)
        self.autocomplete_listbox.bind("<Double-Button-1>", self.complete_from_listbox)
        self.autocomplete_listbox.selection_set(0)

    def hide_autocomplete(self, event=None):
        if self.autocomplete_listbox:
            self.autocomplete_listbox.destroy()
            self.autocomplete_listbox = None

    def complete_from_listbox(self, event=None):
        if not self.autocomplete_listbox: return "break"
        selected_index = self.autocomplete_listbox.curselection()
        if not selected_index: selected_index = (0,)
        completion = self.autocomplete_listbox.get(selected_index[0])
        current_text = self.command_entry.get()
        parts = current_text.split()
        base = " ".join(parts[:-1])
        new_text = (base + " " if base else "") + completion
        self.command_entry.delete(0, "end")
        self.command_entry.insert(0, new_text)
        self.hide_autocomplete()
        return "break"
