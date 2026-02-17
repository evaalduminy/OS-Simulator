# ui_memory.py
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import random
from logic.logic_memory import MemoryManager

class MemoryManagementWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("محاكي إدارة الذاكرة")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        # --- State ---
        self.memory_manager = MemoryManager(total_size=1024) # Default 1MB memory
        self.processes_queue = []
        self.process_colors = {}

        # --- Layout ---
        self.grid_columnconfigure(0, weight=1, minsize=300) # Control Panel
        self.grid_columnconfigure(1, weight=3) # Simulation Panel
        self.grid_rowconfigure(0, weight=1)

        self._create_control_panel()
        self._create_simulation_panel()

        # Use 'after' to ensure the initial drawing happens after the window is fully rendered
        self.after(100, self.update_display)

    def _create_control_panel(self):
        panel = ctk.CTkScrollableFrame(self, label_text="لوحة التحكم")
        panel.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        
        # --- Memory Size ---
        mem_size_frame = ctk.CTkFrame(panel)
        mem_size_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(mem_size_frame, text="حجم الذاكرة الكلي (KB):").pack()
        self.mem_size_slider = ctk.CTkSlider(mem_size_frame, from_=128, to=4096, number_of_steps=30, command=self.on_mem_size_change)
        self.mem_size_slider.pack(pady=5, fill="x", padx=10)
        self.mem_size_label = ctk.CTkLabel(mem_size_frame, text="1024 KB")
        self.mem_size_label.pack()
        self.mem_size_slider.set(1024)
        
        # --- Add Process ---
        add_proc_frame = ctk.CTkFrame(panel)
        add_proc_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(add_proc_frame, text="إضافة عملية جديدة").pack()
        ctk.CTkLabel(add_proc_frame, text="حجم العملية (KB):").pack(side="left", padx=5)
        self.process_size_entry = ctk.CTkEntry(add_proc_frame, width=80)
        self.process_size_entry.pack(side="left", padx=5, expand=True)
        ctk.CTkButton(add_proc_frame, text="إضافة", width=60, command=self.add_process).pack(side="left", padx=5)

        # --- Algorithm Selection ---
        algo_frame = ctk.CTkFrame(panel)
        algo_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(algo_frame, text="خوارزمية التخصيص").pack()
        self.algorithm_var = tk.StringVar(value="Best-Fit")
        ctk.CTkRadioButton(algo_frame, text="First-Fit (الملائمة الأولى)", variable=self.algorithm_var, value="First-Fit").pack(anchor="w", padx=20, pady=2)
        ctk.CTkRadioButton(algo_frame, text="Best-Fit (الملائمة الأفضل)", variable=self.algorithm_var, value="Best-Fit").pack(anchor="w", padx=20, pady=2)
        ctk.CTkRadioButton(algo_frame, text="Worst-Fit (الملائمة الأسوأ)", variable=self.algorithm_var, value="Worst-Fit").pack(anchor="w", padx=20, pady=2)
        
        ctk.CTkButton(panel, text="⬇️ تخصيص ذاكرة للعملية التالية", command=self.allocate_memory).pack(pady=10, padx=10, fill="x", ipady=5)

        # --- De-allocation ---
        dealloc_frame = ctk.CTkFrame(panel)
        dealloc_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(dealloc_frame, text="تحرير الذاكرة (De-allocation)").pack()
        self.allocated_listbox = tk.Listbox(dealloc_frame, bg="#2B2B2B", fg="white", selectbackground="#007ACC", highlightthickness=0, borderwidth=0, height=5)
        self.allocated_listbox.pack(pady=5, fill="x")
        ctk.CTkButton(dealloc_frame, text="⬆️ تحرير الذاكرة المحددة", command=self.free_memory).pack(pady=10, fill="x")

    def _create_simulation_panel(self):
        panel = ctk.CTkFrame(self)
        panel.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        panel.grid_rowconfigure(0, weight=3) # Memory visualization
        panel.grid_rowconfigure(1, weight=2) # Queue and Log
        panel.grid_columnconfigure(0, weight=1)

        # --- Memory Canvas ---
        ctk.CTkLabel(panel, text="التمثيل المرئي للذاكرة", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(10,0), sticky="n")
        self.memory_canvas = tk.Canvas(panel, bg="#1A1A1A", highlightthickness=0)
        self.memory_canvas.grid(row=0, column=0, padx=10, pady=(40,10), sticky="nsew")

        # --- Bottom Section (Queue & Log) ---
        bottom_frame = ctk.CTkFrame(panel, fg_color="transparent")
        bottom_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        bottom_frame.grid_columnconfigure((0, 1), weight=1)
        bottom_frame.grid_rowconfigure(0, weight=1)

        # Processes Queue
        queue_frame = ctk.CTkFrame(bottom_frame)
        queue_frame.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        ctk.CTkLabel(queue_frame, text="طابور العمليات المنتظرة").pack(pady=5)
        self.queue_listbox = tk.Listbox(queue_frame, bg="#2B2B2B", fg="white", highlightthickness=0, borderwidth=0)
        self.queue_listbox.pack(pady=5, padx=10, fill="both", expand=True)

        # Log
        log_frame = ctk.CTkFrame(bottom_frame)
        log_frame.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
        ctk.CTkLabel(log_frame, text="سجل الأحداث").pack(pady=5)
        self.log_textbox = ctk.CTkTextbox(log_frame, wrap="word", state="disabled")
        self.log_textbox.pack(pady=5, padx=10, fill="both", expand=True)

    def on_mem_size_change(self, value):
        size = int(value)
        self.mem_size_label.configure(text=f"{size} KB")
        if messagebox.askyesno("تأكيد", "سيؤدي تغيير حجم الذاكرة إلى مسح الحالة الحالية. هل تريد المتابعة؟", parent=self):
            self.memory_manager = MemoryManager(total_size=size)
            self.processes_queue = []
            self.process_colors = {}
            self.log_message(f"تم إعادة تهيئة الذاكرة بحجم {size} KB.")
            self.update_display()
        else:
            self.mem_size_slider.set(self.memory_manager.total_size) # Revert slider

    def add_process(self):
        try:
            size_str = self.process_size_entry.get()
            if not size_str:
                messagebox.showwarning("إدخال فارغ", "الرجاء إدخال حجم للعملية.", parent=self)
                return
            size = int(size_str)
            if size <= 0: raise ValueError
            process = self.memory_manager.add_process(size)
            self.processes_queue.append(process)
            self.process_colors[process['id']] = self.get_random_color()
            self.log_message(f"تمت إضافة العملية {process['id']} بحجم {size}KB إلى الطابور.")
            self.process_size_entry.delete(0, "end")
            self.update_display()
        except ValueError:
            messagebox.showerror("خطأ", "الرجاء إدخال حجم صحيح وموجب للعملية.", parent=self)

    def allocate_memory(self):
        if not self.processes_queue:
            self.log_message("لا توجد عمليات في الطابور لتخصيصها.")
            return
        
        process_to_allocate = self.processes_queue[0]
        algorithm = self.algorithm_var.get()
        
        block, message = self.memory_manager.allocate(process_to_allocate, algorithm)
        
        self.log_message(message)
        if block:
            self.processes_queue.pop(0)
        
        self.update_display()

    def free_memory(self):
        selected = self.allocated_listbox.curselection()
        if not selected:
            self.log_message("الرجاء تحديد عملية مخصصة لتحريرها.")
            return
        
        selected_text = self.allocated_listbox.get(selected[0])
        block_id = int(selected_text.split(" ")[1].replace(":", ""))
        
        message = self.memory_manager.free(block_id)
        self.log_message(message)
        self.update_display()

    def update_display(self):
        self.draw_memory()
        self.update_lists()
        self.update_fragmentation_info()

    def draw_memory(self):
        self.memory_canvas.delete("all")
        canvas_width = self.memory_canvas.winfo_width()
        canvas_height = self.memory_canvas.winfo_height()
        total_size = self.memory_manager.total_size
        
        if canvas_width < 2 or canvas_height < 2: return

        for block in self.memory_manager.memory:
            start_pos = (block['start'] / total_size) * canvas_width
            end_pos = ((block['start'] + block['size']) / total_size) * canvas_width
            
            color = "#333333" # Free
            text_color = "white"
            process_text = f"فارغ ({block['size']}KB)"

            if block['status'] == 'allocated':
                process_id = block['process_id']
                color = self.process_colors.get(process_id, "#CCCCCC")
                process_text = f"{process_id} ({block['size']}KB)"

            self.memory_canvas.create_rectangle(start_pos, 20, end_pos, canvas_height - 20, fill=color, outline="white", width=2)
            
            if end_pos - start_pos > 50:
                self.memory_canvas.create_text((start_pos + end_pos) / 2, canvas_height / 2, text=process_text, fill=text_color, font=('Calibri', 10, 'bold'))
            
            self.memory_canvas.create_text(start_pos + 5, 10, text=f"{block['start']}KB", anchor="w", fill="gray")

        self.memory_canvas.create_text(canvas_width - 5, 10, text=f"{total_size}KB", anchor="e", fill="gray")

    def update_lists(self):
        self.queue_listbox.delete(0, "end")
        for proc in self.processes_queue:
            self.queue_listbox.insert("end", f"{proc['id']} ({proc['size']}KB)")

        self.allocated_listbox.delete(0, "end")
        for block in self.memory_manager.memory:
            if block['status'] == 'allocated':
                self.allocated_listbox.insert("end", f"Block {block['id']}: {block['process_id']} ({block['size']}KB)")

    def update_fragmentation_info(self):
        external_frag = self.memory_manager.get_fragmentation()
        self.log_message(f"--- تحديث الحالة ---\nالتجزئة الخارجية الحالية: {external_frag} KB", clear_existing=False)

    def log_message(self, message, clear_existing=True):
        self.log_textbox.configure(state="normal")
        if clear_existing:
            self.log_textbox.delete("1.0", "end")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")

    def get_random_color(self):
        # Generate colors that are not too dark
        r = random.randint(50, 200)
        g = random.randint(50, 200)
        b = random.randint(50, 200)
        return f"#{r:02x}{g:02x}{b:02x}"
