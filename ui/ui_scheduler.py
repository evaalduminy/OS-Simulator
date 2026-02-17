# ui_scheduler.py (FIXED and Final Version)
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import random
from logic import logic

class SchedulerWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("محاكي جدولة المعالج")
        self.geometry("1200x700")
        self.minsize(1100, 650)

        self.process_counter = 1

        self.grid_columnconfigure(0, weight=2, minsize=450)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self._create_left_panel()
        self.right_frame = ctk.CTkFrame(self, corner_radius=10)
        self.right_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        self._show_welcome_message()

    def _create_left_panel(self):
        left_frame = ctk.CTkFrame(self, corner_radius=10)
        left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        left_frame.grid_rowconfigure(2, weight=1)

        # --- Input Frame ---
        input_frame = ctk.CTkFrame(left_frame)
        input_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        input_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        ctk.CTkLabel(input_frame, text="اسم العملية", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5)
        ctk.CTkLabel(input_frame, text="وقت الوصول", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5)
        ctk.CTkLabel(input_frame, text="وقت التنفيذ", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5)
        ctk.CTkLabel(input_frame, text="الأولوية", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5)
        self.process_name_entry = ctk.CTkEntry(input_frame, placeholder_text=f"P{self.process_counter}")
        self.process_name_entry.grid(row=1, column=0, padx=5, pady=10)
        self.arrival_time_entry = ctk.CTkEntry(input_frame, placeholder_text="0")
        self.arrival_time_entry.grid(row=1, column=1, padx=5, pady=10)
        self.burst_time_entry = ctk.CTkEntry(input_frame, placeholder_text="10")
        self.burst_time_entry.grid(row=1, column=2, padx=5, pady=10)
        self.priority_entry = ctk.CTkEntry(input_frame, placeholder_text="1")
        self.priority_entry.grid(row=1, column=3, padx=5, pady=10)
        add_button = ctk.CTkButton(input_frame, text="➕ إضافة عملية", command=self.add_process)
        add_button.grid(row=2, column=0, columnspan=4, padx=5, pady=10, sticky="ew")

        # --- Control Frame (The important part) ---
        control_frame = ctk.CTkFrame(left_frame)
        control_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        control_frame.grid_columnconfigure(0, weight=2)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, weight=1)

        self.algorithm_var = tk.StringVar(value="FCFS")
        algo_menu = ctk.CTkOptionMenu(control_frame, values=["FCFS", "SJF", "Priority", "Round Robin"], variable=self.algorithm_var)
        algo_menu.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.preemptive_var = tk.StringVar(value="غير استباقي")
        preemptive_menu = ctk.CTkOptionMenu(control_frame, values=["استباقي", "غير استباقي"], variable=self.preemptive_var)
        preemptive_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.quantum_entry = ctk.CTkEntry(control_frame, placeholder_text="Quantum=2")
        self.quantum_entry.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # The single, clear "Run" button
        run_button = ctk.CTkButton(control_frame, text="🚀 تشغيل المحاكاة", command=self.run_simulation)
        run_button.grid(row=1, column=0, columnspan=3, padx=5, pady=10, sticky="ew", ipady=5)

        # --- Table Frame ---
        table_frame = ctk.CTkFrame(left_frame)
        table_frame.grid(row=2, column=0, padx=15, pady=15, sticky="nsew")
        self._setup_table_style()
        self.process_table = ttk.Treeview(table_frame, columns=("pid", "arrival", "burst", "priority"), show="headings")
        self.process_table.heading("pid", text="العملية"); self.process_table.column("pid", anchor=tk.CENTER, width=80)
        self.process_table.heading("arrival", text="وقت الوصول"); self.process_table.column("arrival", anchor=tk.CENTER, width=100)
        self.process_table.heading("burst", text="وقت التنفيذ"); self.process_table.column("burst", anchor=tk.CENTER, width=100)
        self.process_table.heading("priority", text="الأولوية"); self.process_table.column("priority", anchor=tk.CENTER, width=80)
        self.process_table.pack(fill="both", expand=True)

        # --- Bottom Buttons ---
        bottom_buttons_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        bottom_buttons_frame.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="ew")
        bottom_buttons_frame.grid_columnconfigure((0,1), weight=1)
        
        preset_button = ctk.CTkButton(bottom_buttons_frame, text="📥 تحميل بيانات افتراضية", command=self.load_preset_data)
        preset_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        clear_button = ctk.CTkButton(bottom_buttons_frame, text="🗑️ مسح الكل", fg_color="#D32F2F", hover_color="#E57373", command=self.clear_all)
        clear_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def _get_processes_from_table(self):
        processes_data = []
        for item in self.process_table.get_children():
            values = self.process_table.item(item, 'values')
            processes_data.append({
                'pid': values[0], 
                'arrival': int(values[1]), 
                'burst': int(values[2]),
                'priority': int(values[3])
            })
        return processes_data

    def run_simulation(self):
        processes_data = self._get_processes_from_table()
        if not processes_data:
            self.show_error("خطأ", "لا توجد عمليات في الجدول.")
            return

        algo = self.algorithm_var.get()
        is_preemptive = (self.preemptive_var.get() == "استباقي")
        
        results, gantt_data, avg_tat, avg_wt = None, None, 0, 0

        try:
            if algo == "FCFS":
                results, gantt_data, avg_tat, avg_wt = logic.run_fcfs_logic(processes_data)
            elif algo == "SJF":
                results, gantt_data, avg_tat, avg_wt = logic.run_sjf_logic(processes_data, is_preemptive)
            elif algo == "Priority":
                results, gantt_data, avg_tat, avg_wt = logic.run_priority_logic(processes_data, is_preemptive)
            elif algo == "Round Robin":
                try:
                    quantum = int(self.quantum_entry.get() or 2)
                    if quantum <= 0: raise ValueError
                except ValueError:
                    self.show_error("خطأ", "الشريحة الزمنية (Quantum) يجب أن تكون رقماً صحيحاً أكبر من صفر.")
                    return
                results, gantt_data, avg_tat, avg_wt = logic.run_rr_logic(processes_data, quantum)
            
            if results is not None:
                self.display_results(results, gantt_data, avg_tat, avg_wt)
            else:
                self.show_error("خطأ", f"لم يتم إرجاع نتائج من خوارزمية {algo}.")

        except Exception as e:
            self.show_error("خطأ فادح", f"حدث خطأ غير متوقع أثناء تشغيل الخوارزمية:\n{e}")

    def _show_welcome_message(self):
        for widget in self.right_frame.winfo_children(): widget.destroy()
        welcome_label = ctk.CTkLabel(self.right_frame, text="مرحباً بك في محاكي جدولة المعالج!\n\nالنتائج ستظهر هنا بعد تشغيل إحدى الخوارزميات.", font=ctk.CTkFont(size=18), text_color="gray60", wraplength=400)
        welcome_label.place(relx=0.5, rely=0.5, anchor="center")

    def _setup_table_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#2a2d2e", borderwidth=0, rowheight=25)
        style.configure("Treeview.Heading", background="#242424", foreground="white", font=('Calibri', 12,'bold'))
        style.map('Treeview', background=[('selected', '#007ACC')])
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

    def show_error(self, title, message):
        messagebox.showerror(title, message, parent=self)

    def add_process(self):
        p_name = self.process_name_entry.get() or f"P{self.process_counter}"
        arrival = self.arrival_time_entry.get()
        burst = self.burst_time_entry.get()
        priority = self.priority_entry.get()
        if arrival.isdigit() and burst.isdigit() and priority.isdigit():
            self.process_table.insert("", "end", values=(p_name, int(arrival), int(burst), int(priority)))
            self.process_counter += 1
            for entry in [self.process_name_entry, self.arrival_time_entry, self.burst_time_entry, self.priority_entry]: entry.delete(0, "end")
            self.process_name_entry.configure(placeholder_text=f"P{self.process_counter}")
            self.process_name_entry.focus()
        else:
            self.show_error("خطأ في الإدخال", "الوصول، التنفيذ، والأولوية يجب أن تكون أرقاماً صحيحة.")

    def clear_all(self):
        for item in self.process_table.get_children(): self.process_table.delete(item)
        self.process_counter = 1
        self.process_name_entry.configure(placeholder_text=f"P{self.process_counter}")
        self._show_welcome_message()

    def load_preset_data(self):
        self.clear_all()
        preset_data = [('P1', 0, 8, 2), ('P2', 1, 4, 1), ('P3', 2, 2, 3)]
        for p in preset_data: self.process_table.insert("", "end", values=p)
        self.process_counter = len(preset_data) + 1
        self.process_name_entry.configure(placeholder_text=f"P{self.process_counter}")

    def display_results(self, processes, gantt_chart_data, avg_turnaround, avg_waiting):
        for widget in self.right_frame.winfo_children(): widget.destroy()
        if not processes: return

        gantt_container = ctk.CTkFrame(self.right_frame)
        gantt_container.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(gantt_container, text="مخطط جانت", font=ctk.CTkFont(size=14, weight="bold")).pack()
        canvas = tk.Canvas(gantt_container, bg="#2a2d2e", height=100, highlightthickness=0)
        canvas.pack(fill="x", pady=5)
        self.right_frame.update_idletasks()
        canvas_width = canvas.winfo_width()
        if not gantt_chart_data: return
        total_time = gantt_chart_data[-1]['finish']
        if total_time == 0: total_time = 1
        padding = 20
        
        process_colors = {}
        colors = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6", "#1abc9c", "#e67e22"]
        random.shuffle(colors)
        unique_pids = sorted(list(set(p['pid'] for p in processes)))
        for i, pid in enumerate(unique_pids): process_colors[pid] = colors[i % len(colors)]
        process_colors['خمول'] = "#7f8c8d"

        for block in gantt_chart_data:
            pid = block['pid']
            start_pos = padding + (block['start'] / total_time) * (canvas_width - 2 * padding)
            end_pos = padding + (block['finish'] / total_time) * (canvas_width - 2 * padding)
            if end_pos - start_pos < 1: continue
            color = process_colors.get(pid, "#bdc3c7")
            canvas.create_rectangle(start_pos, 20, end_pos, 70, fill=color, outline="white", width=1.5)
            if end_pos - start_pos > 20: canvas.create_text((start_pos + end_pos) / 2, 45, text=pid, fill="white", font=('Calibri', 10, 'bold'))
            canvas.create_text(start_pos, 85, text=str(block['start']), fill="white", font=('Calibri', 9))
            canvas.create_text(end_pos, 85, text=str(block['finish']), fill="white", font=('Calibri', 9))

        results_frame = ctk.CTkFrame(self.right_frame)
        results_frame.pack(pady=10, padx=10, fill="both", expand=True)
        results_table = ttk.Treeview(results_frame, columns=("pid", "arrival", "burst", "priority", "ct", "tat", "wt"), show="headings")
        results_table.heading("pid", text="العملية"); results_table.column("pid", anchor=tk.CENTER, width=80)
        results_table.heading("arrival", text="الوصول"); results_table.column("arrival", anchor=tk.CENTER, width=80)
        results_table.heading("burst", text="التنفيذ"); results_table.column("burst", anchor=tk.CENTER, width=80)
        results_table.heading("priority", text="الأولوية"); results_table.column("priority", anchor=tk.CENTER, width=80)
        results_table.heading("ct", text="الانتهاء"); results_table.column("ct", anchor=tk.CENTER, width=80)
        results_table.heading("tat", text="الاستجابة"); results_table.column("tat", anchor=tk.CENTER, width=80)
        results_table.heading("wt", text="الانتظار"); results_table.column("wt", anchor=tk.CENTER, width=80)
        
        sorted_results = sorted(processes, key=lambda x: int(''.join(filter(str.isdigit, x['pid'])) or 0))
        for p in sorted_results:
            results_table.insert("", "end", values=(p['pid'], p['arrival'], p['burst'], p['priority'], p.get('completion_time', 'N/A'), p.get('turnaround_time', 'N/A'), p.get('waiting_time', 'N/A')))
        results_table.pack(fill="both", expand=True)

        averages_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        averages_frame.pack(pady=10, padx=10, fill="x")
        averages_frame.grid_columnconfigure((0,1), weight=1)
        ctk.CTkLabel(averages_frame, text=f"متوسط زمن الاستجابة: {avg_turnaround:.2f}", font=ctk.CTkFont(size=14)).grid(row=0, column=0, sticky="e", padx=10)
        ctk.CTkLabel(averages_frame, text=f"متوسط زمن الانتظار: {avg_waiting:.2f}", font=ctk.CTkFont(size=14)).grid(row=0, column=1, sticky="w", padx=10)
