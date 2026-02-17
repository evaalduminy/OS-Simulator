
import customtkinter as ctk
from tkinter import messagebox

# --- استيراد كل واجهة من ملفها الخاص ---
from ui_scheduler import SchedulerWindow
from ui_deadlock import DeadlockWindow
from ui_batch import BatchWindow
from ui_shell import ShellWindow
from ui_memory import MemoryManagementWindow

# --- الخطوة 1: تحديد شكل ولون التطبيق بالكامل ---
# هذان السطران هما المسؤولان عن المظهر الجميل (الأسود والأخضر)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

# --- الخطوة 2: بناء النافذة الرئيسية للتطبيق ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("محاكي مفاهيم أنظمة التشغيل")
        self.geometry("800x600")

        # متغيرات لتذكر النوافذ المفتوحة (لمنع فتح النافذة مرتين)
        self.scheduler_window = None
        self.deadlock_window = None
        self.batch_window = None
        self.shell_window = None
        self.memory_window = None

         # --- بناء الواجهة: عنوان في الأعلى، وأزرار في المنتصف ---
        ctk.CTkLabel(self, text="اختر المحاكي الذي تريد تشغيله", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure((0, 1), weight=1)
        main_frame.grid_rowconfigure((0, 1, 2), weight=1)

        card_font = ctk.CTkFont(size=16, weight="bold")
        
        # --- ربط كل زر بالدالة التي تفتح نافذته ---
        ctk.CTkButton(main_frame, text="جدولة المعالج", font=card_font, command=self.open_scheduler_window).grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkButton(main_frame, text="الجمود", font=card_font, command=self.open_deadlock_window).grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkButton(main_frame, text="المعالجة الدفعية (Batch)", font=card_font, command=self.open_batch_window).grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkButton(main_frame, text="واجهة الأوامر (Shell)", font=card_font, command=self.open_shell_window).grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkButton(main_frame, text="إدارة الذاكرة", font=card_font, command=self.open_memory_window).grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    # --- الخطوة 3: دوال لفتح وإغلاق كل نافذة ---
    # هذا مثال واحد، والبقية متشابهة
    def open_scheduler_window(self):
        if self.scheduler_window is None: # إذا كانت النافذة مغلقة
            self.withdraw() # أخفِ النافذة الرئيسية
            self.scheduler_window = SchedulerWindow(self) # افتح النافذة الجديدة
            self.scheduler_window.protocol("WM_DELETE_WINDOW", self.on_scheduler_close) # ماذا تفعل عند الضغط على X
        else:
            self.scheduler_window.focus() # إذا كانت مفتوحة، فقط اجلبها للأمام

    def on_scheduler_close(self):
        self.scheduler_window.destroy() # دمر النافذة
        self.scheduler_window = None # أخبر البرنامج أنها أصبحت مغلقة
        self.deiconify() # أعد إظهار النافذة الرئيسية

    # (بقية دوال الفتح والإغلاق بنفس الطريقة)
    def open_deadlock_window(self):
        if self.deadlock_window is None: self.withdraw(); self.deadlock_window = DeadlockWindow(self); self.deadlock_window.protocol("WM_DELETE_WINDOW", self.on_deadlock_close)
        else: self.deadlock_window.focus()
    def on_deadlock_close(self): self.deadlock_window.destroy(); self.deadlock_window = None; self.deiconify()

    def open_batch_window(self):
        if self.batch_window is None: self.withdraw(); self.batch_window = BatchWindow(self); self.batch_window.protocol("WM_DELETE_WINDOW", self.on_batch_close)
        else: self.batch_window.focus()
    def on_batch_close(self):
        if self.batch_window.is_running.is_set():
            if not messagebox.askyesno("تأكيد", "هناك عملية قيد التشغيل. هل تريد إلغاءها؟"): return
        self.batch_window.destroy(); self.batch_window = None; self.deiconify()

    def open_shell_window(self):
        if self.shell_window is None: self.withdraw(); self.shell_window = ShellWindow(self); self.shell_window.protocol("WM_DELETE_WINDOW", self.on_shell_close)
        else: self.shell_window.focus()
    def on_shell_close(self): self.shell_window.destroy(); self.shell_window = None; self.deiconify()

    def open_memory_window(self):
        if self.memory_window is None: self.withdraw(); self.memory_window = MemoryManagementWindow(self); self.memory_window.protocol("WM_DELETE_WINDOW", self.on_memory_close)
        else: self.memory_window.focus()
    def on_memory_close(self): self.memory_window.destroy(); self.memory_window = None; self.deiconify()

# --- الخطوة 4: تشغيل التطبيق ---
if __name__ == "__main__":
    app = App() # أنشئ التطبيق
    app.mainloop() # شغله
