# ui_batch.py (Redesigned and Improved)
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import subprocess
import threading
import time

class BatchWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("المعالجة الدفعية (Batch Processing)")
        self.geometry("1000x700")
        self.minsize(800, 600)

        # --- State & Threading ---
        self.batch_thread = None
        self.is_running = threading.Event()
        self.is_paused = threading.Event()
        self.is_cancelled = threading.Event()
        self.current_command_index = -1

        # --- Layout ---
        self.grid_rowconfigure(0, weight=1) # Editor Panel
        self.grid_rowconfigure(1, weight=1) # Output Panel
        self.grid_columnconfigure(0, weight=1)

        # --- Create Panels ---
        self._create_editor_panel()
        self._create_output_panel()

    # =================================================================
    # 1. PANEL CREATION
    # =================================================================
    def _create_editor_panel(self):
        panel = ctk.CTkFrame(self)
        panel.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        # --- Header and Controls ---
        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(header, text="محرر الأوامر", font=ctk.CTkFont(weight="bold")).pack(side="left")

        control_buttons = ctk.CTkFrame(header, fg_color="transparent")
        control_buttons.pack(side="right")
        self.start_button = ctk.CTkButton(control_buttons, text="▶ بدء التنفيذ", command=self.start_batch)
        self.start_button.pack(side="left", padx=5)
        self.pause_resume_button = ctk.CTkButton(control_buttons, text="⏸ إيقاف مؤقت", state="disabled", command=self.toggle_pause)
        self.pause_resume_button.pack(side="left", padx=5)
        self.cancel_button = ctk.CTkButton(control_buttons, text="⏹ إلغاء", state="disabled", fg_color="#c0392b", hover_color="#e74c3c", command=self.cancel_batch)
        self.cancel_button.pack(side="left", padx=5)

        # --- Text Editor with Line Numbers ---
        editor_frame = ctk.CTkFrame(panel)
        editor_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        editor_frame.grid_rowconfigure(0, weight=1)
        editor_frame.grid_columnconfigure(1, weight=1)

        self.line_numbers = tk.Text(editor_frame, width=4, padx=4, takefocus=0, border=0,
                                    background="#2B2B2B", foreground="gray50", state="disabled",
                                    font=('Consolas', 14))
        self.line_numbers.grid(row=0, column=0, sticky="ns")

        self.commands_textbox = ctk.CTkTextbox(editor_frame, font=ctk.CTkFont(family="Consolas", size=14), wrap="word")
        self.commands_textbox.grid(row=0, column=1, sticky="nsew")
        self.commands_textbox.insert("1.0", "echo مرحباً من الدفعة الأولى\n\nping -n 2 google.com\n\necho عرض محتويات المجلد الحالي:\ndir\n\necho انتهت المعالجة الدفعية.")
        
        # --- Sync scrolling and line numbers ---
        self.commands_textbox._textbox.configure(yscrollcommand=self._on_textbox_scroll)
        self.commands_textbox.bind("<KeyRelease>", self._on_key_release)
        self.commands_textbox.bind("<MouseWheel>", self._on_mouse_wheel)
        
        self._update_line_numbers()

    def _create_output_panel(self):
        panel = ctk.CTkFrame(self)
        panel.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        # --- Progress Bar and Options ---
        progress_frame = ctk.CTkFrame(panel, fg_color="transparent")
        progress_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        progress_frame.grid_columnconfigure(1, weight=1)
        
        self.stop_on_error_checkbox = ctk.CTkCheckBox(progress_frame, text="التوقف عند حدوث خطأ")
        self.stop_on_error_checkbox.grid(row=0, column=0, pady=5, sticky="w")
        self.stop_on_error_checkbox.select()
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, orientation="horizontal")
        self.progress_bar.grid(row=0, column=1, padx=20, pady=5, sticky="ew")
        self.progress_bar.set(0)

        # --- Output Textbox ---
        self.output_textbox = ctk.CTkTextbox(panel, font=ctk.CTkFont(family="Consolas", size=14), wrap="word")
        self.output_textbox.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.output_textbox.configure(state="disabled")

    # =================================================================
    # 2. LINE NUMBER AND HIGHLIGHTING LOGIC
    # =================================================================
    def _on_textbox_scroll(self, *args):
        self.line_numbers.yview_moveto(args[0])

    def _on_mouse_wheel(self, event):
        self.line_numbers.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def _on_key_release(self, event=None):
        self._update_line_numbers()

    def _update_line_numbers(self):
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        
        line_count = self.commands_textbox.get("1.0", "end-1c").count("\n") + 1
        line_numbers_text = "\n".join(str(i) for i in range(1, line_count + 1))
        
        self.line_numbers.insert("1.0", line_numbers_text)
        self.line_numbers.configure(state="disabled")

    def _highlight_line(self, line_index):
        # Remove previous highlight
        self.commands_textbox.tag_remove("highlight", "1.0", "end")
        
        if line_index >= 0:
            # Add new highlight
            start_index = f"{line_index + 1}.0"
            end_index = f"{line_index + 1}.end"
            self.commands_textbox.tag_add("highlight", start_index, end_index)
            self.commands_textbox.tag_config("highlight", background="#007ACC")
            self.commands_textbox.see(start_index)

    # =================================================================
    # 3. BATCH EXECUTION LOGIC
    # =================================================================
    def update_output(self, text):
        self.output_textbox.configure(state="normal")
        self.output_textbox.insert("end", text)
        self.output_textbox.see("end")
        self.output_textbox.configure(state="disabled")

    def start_batch(self):
        commands = self.commands_textbox.get("1.0", "end").strip().split('\n')
        self.valid_commands = [(i, cmd) for i, cmd in enumerate(commands) if cmd.strip()]
        
        if not self.valid_commands:
            messagebox.showwarning("فارغ", "الرجاء إدخال أمر واحد على الأقل.", parent=self)
            return

        self.is_running.set()
        self.is_paused.clear()
        self.is_cancelled.clear()
        
        self.start_button.configure(state="disabled")
        self.pause_resume_button.configure(state="normal", text="⏸ إيقاف مؤقت")
        self.cancel_button.configure(state="normal")
        self.commands_textbox.configure(state="disabled")
        
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.configure(state="disabled")
        
        self.batch_thread = threading.Thread(target=self.run_batch, args=(self.valid_commands,))
        self.batch_thread.daemon = True
        self.batch_thread.start()

    def toggle_pause(self):
        if self.is_paused.is_set():
            self.is_paused.clear()
            self.pause_resume_button.configure(text="⏸ إيقاف مؤقت")
        else:
            self.is_paused.set()
            self.pause_resume_button.configure(text="▶ استئناف")

    def cancel_batch(self):
        if self.is_running.is_set():
            if messagebox.askyesno("تأكيد الإلغاء", "هل تريد بالتأكيد إلغاء العملية الحالية؟", parent=self):
                self.is_cancelled.set()
                self.is_paused.clear() # Ensure it's not stuck in pause

    def reset_ui_state(self):
        self.start_button.configure(state="normal")
        self.pause_resume_button.configure(state="disabled", text="⏸ إيقاف مؤقت")
        self.cancel_button.configure(state="disabled")
        self.commands_textbox.configure(state="normal")
        self.is_running.clear()
        self._highlight_line(-1) # Remove highlight

    def run_batch(self, commands_with_indices):
        total_commands = len(commands_with_indices)
        stop_on_error = self.stop_on_error_checkbox.get() == 1
        
        for i, (line_index, command) in enumerate(commands_with_indices):
            if self.is_cancelled.is_set():
                self.after(0, lambda: self.update_output("\n--- ⏹ تم إلغاء العملية الدفعية من قبل المستخدم ---\n"))
                break
            
            while self.is_paused.is_set():
                if self.is_cancelled.is_set(): break
                time.sleep(0.1)
            
            self.after(0, self._highlight_line, line_index)
            self.after(0, lambda cmd=command: self.update_output(f"\n>>> Executing: {cmd}\n"))
            
            has_error = False
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
                if result.stdout:
                    self.after(0, lambda out=result.stdout: self.update_output(out))
                if result.stderr:
                    self.after(0, lambda err=result.stderr: self.update_output(f"ERROR: {err}"))
                    has_error = True
            except subprocess.TimeoutExpired:
                self.after(0, lambda: self.update_output("ERROR: Command timed out after 60 seconds.\n"))
                has_error = True
            except Exception as e:
                self.after(0, lambda err=e: self.update_output(f"An unexpected error occurred: {err}\n"))
                has_error = True
            
            if has_error and stop_on_error:
                self.after(0, lambda: self.update_output("\n--- ❌ توقفت العملية بسبب حدوث خطأ ---\n"))
                break
                
            progress = (i + 1) / total_commands
            self.after(0, lambda p=progress: self.progress_bar.set(p))
        
        if not self.is_cancelled.is_set() and not (has_error and stop_on_error):
            self.after(0, lambda: self.update_output("\n--- ✅ انتهت جميع الأوامر في الدفعة ---\n"))
            
        self.after(0, self.reset_ui_state)
