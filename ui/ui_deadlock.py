# ui_deadlock.py (Corrected and Final Version)
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import json
from logic import logic

class DeadlockWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("محاكي خوارزمية المصرفي (تفاعلي)")
        self.geometry("1400x800")
        self.resizable(True, True)
        self.minsize(1200, 750)

        self.simulation_generator = None
        self.process_widgets = []
        self.table_labels = {}

        # --- Layout ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2) # Input panel
        self.grid_columnconfigure(1, weight=3) # Simulation panel

        # --- Panels ---
        self._create_input_panel()
        self._create_simulation_panel()

        # --- Initial Setup ---
        self.num_resources_slider.set(3)
        self.setup_resource_inputs()
        self.log("مرحباً! قم بإعداد الحالة على اليسار ثم اضغط 'بدء المحاكاة'.")

    # =================================================================
    # 1. PANEL CREATION
    # =================================================================
    def _create_input_panel(self):
        panel = ctk.CTkFrame(self)
        panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        panel.grid_rowconfigure(2, weight=1)

        # --- Resource Count ---
        res_frame = ctk.CTkFrame(panel)
        res_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(res_frame, text="1. حدد عدد الموارد:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(5,0))
        self.num_resources_slider = ctk.CTkSlider(res_frame, from_=1, to=5, number_of_steps=4, command=lambda val: self.setup_resource_inputs())
        self.num_resources_slider.pack(fill="x", padx=10, pady=10)

        # --- Available Resources ---
        avail_frame = ctk.CTkFrame(panel)
        avail_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(avail_frame, text="2. أدخل الموارد المتاحة (Available):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(5,0))
        self.available_resources_frame = ctk.CTkFrame(avail_frame, fg_color="transparent")
        self.available_resources_frame.pack(pady=10)

        # --- Processes ---
        proc_container = ctk.CTkFrame(panel)
        proc_container.pack(fill="both", expand=True, padx=10, pady=10)
        proc_container.grid_rowconfigure(1, weight=1)
        proc_container.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(proc_container, text="3. أضف العمليات:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        proc_buttons = ctk.CTkFrame(proc_container, fg_color="transparent")
        proc_buttons.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(proc_buttons, text="إضافة عملية", command=self.add_process_entry).pack(side="left", padx=5)
        ctk.CTkButton(proc_buttons, text="مسح الكل", fg_color="#D32F2F", hover_color="#E57373", command=self.clear_all).pack(side="left", padx=5)

        self.processes_scroll_frame = ctk.CTkScrollableFrame(proc_container)
        self.processes_scroll_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=5)

        # --- Presets ---
        preset_frame = ctk.CTkFrame(panel)
        preset_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(preset_frame, text="أو قم بتحميل مثال جاهز:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(5,0))
        ctk.CTkButton(preset_frame, text="تحميل مثال (حالة آمنة)", command=self.load_safe_preset).pack(fill="x", padx=5, pady=10)
        ctk.CTkButton(preset_frame, text="تحميل مثال (حالة غير آمنة)", fg_color="#555", hover_color="#666", command=self.load_unsafe_preset).pack(fill="x", padx=5, pady=(0, 5))

    def _create_simulation_panel(self):
        panel = ctk.CTkFrame(self)
        panel.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        panel.grid_rowconfigure(1, weight=1) # Table frame
        panel.grid_rowconfigure(3, weight=1) # Log frame
        panel.grid_columnconfigure(0, weight=1)

        # --- Simulation Controls ---
        sim_controls = ctk.CTkFrame(panel)
        sim_controls.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        sim_controls.grid_columnconfigure((0,1,2), weight=1)
        self.start_button = ctk.CTkButton(sim_controls, text="بدء المحاكاة", command=self.start_simulation)
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.next_step_button = ctk.CTkButton(sim_controls, text="الخطوة التالية", state="disabled", command=self.next_step)
        self.next_step_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.reset_button = ctk.CTkButton(sim_controls, text="إعادة تعيين", state="disabled", fg_color="#E67E22", hover_color="#F39C12", command=self.reset_simulation)
        self.reset_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # --- Main Table Display ---
        self.table_frame = ctk.CTkFrame(panel, fg_color="transparent")
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # --- State Vectors Display ---
        state_frame = ctk.CTkFrame(panel)
        state_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        state_frame.grid_columnconfigure(0, weight=1)
        self.work_vector_label = ctk.CTkLabel(state_frame, text="Work: [ ]", font=ctk.CTkFont(family="Consolas", size=14, weight="bold"))
        self.work_vector_label.grid(row=0, column=0, sticky="w", padx=10)
        self.safe_sequence_label = ctk.CTkLabel(state_frame, text="التسلسل الآمن: < >", font=ctk.CTkFont(size=14))
        self.safe_sequence_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        # --- Log Display ---
        log_frame = ctk.CTkFrame(panel)
        log_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0,10))
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        self.log_textbox = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(family="Consolas", size=14), wrap="word")
        self.log_textbox.grid(sticky="nsew")
        self.log_textbox.configure(state="disabled")

    # =================================================================
    # 2. UI SETUP AND MANAGEMENT
    # =================================================================
    def setup_resource_inputs(self, _=None):
        num_resources = int(self.num_resources_slider.get())
        
        # --- Available Resources ---
        # Read old values before destroying
        old_avail_values = [e.get() for e in getattr(self, 'available_entries', [])]
        for widget in self.available_resources_frame.winfo_children(): widget.destroy()
        
        self.available_entries = []
        resource_labels = ['A', 'B', 'C', 'D', 'E']
        for i in range(num_resources):
            ctk.CTkLabel(self.available_resources_frame, text=resource_labels[i]).pack(side="left")
            entry = ctk.CTkEntry(self.available_resources_frame, width=40)
            if i < len(old_avail_values): entry.insert(0, old_avail_values[i]) # Restore old value
            entry.pack(side="left", padx=(0, 5))
            self.available_entries.append(entry)
        
        # --- Process Entries ---
        for p_widget in self.process_widgets:
            # Read old values before destroying
            old_alloc_values = [e.get() for e in p_widget['alloc']]
            old_max_values = [e.get() for e in p_widget['max']]

            # Destroy old widgets
            for frame_key in ['alloc_frame', 'max_frame']:
                if frame_key in p_widget:
                    for widget in p_widget[frame_key].winfo_children(): widget.destroy()
            
            # Create new widgets and restore old values
            p_widget['alloc'] = self._create_vector_entries(p_widget['alloc_frame'], num_resources, old_alloc_values)
            p_widget['max'] = self._create_vector_entries(p_widget['max_frame'], num_resources, old_max_values)

    def add_process_entry(self, alloc_vals=None, max_vals=None):
        num_resources = len(self.available_entries)
        process_id = len(self.process_widgets)
        
        p_frame = ctk.CTkFrame(self.processes_scroll_frame, border_width=1)
        p_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(p_frame, text=f"العملية P{process_id}", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=5)
        
        ctk.CTkLabel(p_frame, text="Allocation:").grid(row=1, column=0, padx=5, sticky="e")
        alloc_frame = ctk.CTkFrame(p_frame, fg_color="transparent")
        alloc_frame.grid(row=1, column=1, padx=5, pady=5)
        alloc_entries = self._create_vector_entries(alloc_frame, num_resources, alloc_vals)

        ctk.CTkLabel(p_frame, text="Max:").grid(row=2, column=0, padx=5, sticky="e")
        max_frame = ctk.CTkFrame(p_frame, fg_color="transparent")
        max_frame.grid(row=2, column=1, padx=5, pady=5)
        max_entries = self._create_vector_entries(max_frame, num_resources, max_vals)
            
        self.process_widgets.append({
            'frame': p_frame, 'alloc_frame': alloc_frame, 'max_frame': max_frame,
            'alloc': alloc_entries, 'max': max_entries
        })

    def _create_vector_entries(self, parent, num_resources, values=None):
        entries = []
        for i in range(num_resources):
            entry = ctk.CTkEntry(parent, width=40)
            if values and i < len(values): entry.insert(0, str(values[i]))
            entry.pack(side="left", padx=2)
            entries.append(entry)
        return entries

    def clear_all(self):
        for p_widget in self.process_widgets: p_widget['frame'].destroy()
        self.process_widgets = []
        for entry in self.available_entries: entry.delete(0, "end")
        self.reset_simulation()

    def load_safe_preset(self):
        self.num_resources_slider.set(3)
        self.setup_resource_inputs()
        self.clear_all()
        
        for entry, val in zip(self.available_entries, [3, 3, 2]):
            entry.insert(0, str(val))
        
        processes = [
            {'alloc': [0, 1, 0], 'max': [7, 5, 3]}, {'alloc': [2, 0, 0], 'max': [3, 2, 2]},
            {'alloc': [3, 0, 2], 'max': [9, 0, 2]}, {'alloc': [2, 1, 1], 'max': [2, 2, 2]},
            {'alloc': [0, 0, 2], 'max': [4, 3, 3]},
        ]
        for p_data in processes:
            self.add_process_entry(p_data['alloc'], p_data['max'])
        self.log("تم تحميل مثال لحالة آمنة. اضغط 'بدء المحاكاة'.")

    def load_unsafe_preset(self):
        self.num_resources_slider.set(3)
        self.setup_resource_inputs()
        self.clear_all()
        
        for entry, val in zip(self.available_entries, [0, 1, 0]):
            entry.insert(0, str(val))
        
        processes = [
            {'alloc': [0, 1, 0], 'max': [0, 2, 0]}, {'alloc': [2, 0, 1], 'max': [3, 0, 1]},
            {'alloc': [1, 0, 0], 'max': [1, 0, 1]},
        ]
        for p_data in processes:
            self.add_process_entry(p_data['alloc'], p_data['max'])
        self.log("تم تحميل مثال لحالة غير آمنة. اضغط 'بدء المحاكاة'.")

    # =================================================================
    # 3. SIMULATION LOGIC
    # =================================================================
    def start_simulation(self):
        try:
            num_p, num_r, avail, alloc, maxim, need = self._get_system_snapshot()
            self.simulation_generator = logic.check_safety_logic_stepwise(num_p, num_r, avail, alloc, need)
            
            self._draw_table(num_p, num_r, alloc, maxim, need)
            self.log_textbox.configure(state="normal")
            self.log_textbox.delete("1.0", "end")
            self.log_textbox.configure(state="disabled")

            self.start_button.configure(state="disabled")
            self.next_step_button.configure(state="normal")
            self.reset_button.configure(state="normal")
            
            self.next_step() # Execute the first step automatically
        except (ValueError, IndexError) as e:
            messagebox.showerror("خطأ في البيانات", f"الرجاء التأكد من أن جميع الحقول تحتوي على أرقام صحيحة.\n{e}", parent=self)

    def next_step(self):
        if not self.simulation_generator: return
        try:
            state = next(self.simulation_generator)
            self._update_ui_from_state(state)
        except StopIteration:
            self.next_step_button.configure(state="disabled")
            self.log("انتهت المحاكاة.")

    def reset_simulation(self):
        self.simulation_generator = None
        self.start_button.configure(state="normal")
        self.next_step_button.configure(state="disabled")
        self.reset_button.configure(state="disabled")
        
        for widget in self.table_frame.winfo_children(): widget.destroy()
        self.table_labels = {}
        self.work_vector_label.configure(text="Work: [ ]")
        self.safe_sequence_label.configure(text="التسلسل الآمن: < >", text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        self.log("تم إعادة تعيين المحاكاة. يمكنك البدء من جديد.")

    def _update_ui_from_state(self, state):
        self.log(state["log"])
        
        # Reset all row colors to default
        for i in range(len(self.table_labels.get("rows", []))):
            if self.table_labels["finish_labels"][i].cget("text") != "✅":
                self._color_row(i, ("#F9F9F9", "#2B2B2B"))

        if state["type"] == "initial_state":
            self.work_vector_label.configure(text=f"Work: {state['work']}")
        
        elif state["type"] == "check_process":
            idx = state["process_index"]
            self.work_vector_label.configure(text=f"Work: {state['work']}")
            # Color the row being checked
            self._color_row(idx, ("#E3F2FD", "#313942") if state["can_run"] else ("#FFEBEE", "#423131"))

        elif state["type"] == "process_finished":
            idx = state["process_index"]
            self.work_vector_label.configure(text=f"Work: {state['work']}")
            self.safe_sequence_label.configure(text=f"التسلسل الآمن: < {' -> '.join(state['safe_sequence'])} >")
            # Color the finished row green
            self._color_row(idx, ("#E8F5E9", "#314231"))
            self.table_labels["finish_labels"][idx].configure(text="✅")

        elif state["type"] == "final_state":
            self.next_step_button.configure(state="disabled")
            if state["is_safe"]:
                self.safe_sequence_label.configure(text_color="#2ECC71")
            else:
                self.safe_sequence_label.configure(text="الحالة غير آمنة", text_color="#E74C3C")

    def log(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("1.0", message + "\n\n")
        self.log_textbox.configure(state="disabled")

    # =================================================================
    # 4. DRAWING AND DATA GATHERING
    # =================================================================
    def _draw_table(self, num_p, num_r, alloc, maxim, need):
        for widget in self.table_frame.winfo_children(): widget.destroy()
        self.table_labels = {"rows": [], "finish_labels": []}
        
        headers = ["", "Allocation", "Max", "Need", "Finish"]
        for j, header in enumerate(headers):
            ctk.CTkLabel(self.table_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(row=0, column=j, padx=10, pady=5)

        for i in range(num_p):
            row_labels = []
            # Process ID
            label = ctk.CTkLabel(self.table_frame, text=f" P{i} ")
            label.grid(row=i+1, column=0, pady=2)
            row_labels.append(label)
            
            # Vectors
            for j, vector in enumerate([alloc[i], maxim[i], need[i]]):
                label = ctk.CTkLabel(self.table_frame, text=f" {str(vector)} ", font=ctk.CTkFont(family="Consolas"))
                label.grid(row=i+1, column=j+1, padx=10, pady=2)
                row_labels.append(label)

            # Finish status
            label = ctk.CTkLabel(self.table_frame, text=" ❌ ")
            label.grid(row=i+1, column=4, pady=2)
            row_labels.append(label)
            self.table_labels["finish_labels"].append(label)
            
            self.table_labels["rows"].append(row_labels)

    def _color_row(self, row_index, color):
        if row_index < len(self.table_labels.get("rows", [])):
            for label in self.table_labels["rows"][row_index]:
                label.configure(fg_color=color)

    def _get_system_snapshot(self):
        num_processes = len(self.process_widgets)
        num_resources = len(self.available_entries)
        
        if num_processes == 0: raise ValueError("الرجاء إضافة عملية واحدة على الأقل.")

        available = [int(e.get()) for e in self.available_entries]
        allocation = [[int(e.get()) for e in p['alloc']] for p in self.process_widgets]
        maximum = [[int(e.get()) for e in p['max']] for p in self.process_widgets]
        need = [[maximum[i][j] - allocation[i][j] for j in range(num_resources)] for i in range(num_processes)]
        
        for i in range(num_processes):
            for j in range(num_resources):
                if need[i][j] < 0:
                    raise ValueError(f"خطأ في P{i}: Max لا يمكن أن يكون أقل من Allocation.")
        return num_processes, num_resources, available, allocation, maximum, need
