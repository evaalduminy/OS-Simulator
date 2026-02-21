# 🖥️ محاكي مفاهيم أنظمة التشغيل (OS Simulator)

مشروع تعليمي تفاعلي مبني بلغة **Python** ومكتبة **CustomTkinter** يهدف إلى محاكاة وتبسيط أهم المفاهيم والنظريات في مادة نظم التشغيل. يتميز بواجهة رسومية عصرية (GUI) وسهلة الاستخدام.

## ✨ المميزات الرئيسية

يضم المشروع 5 وحدات محاكاة أساسية:

1.  **⚡ جدولة المعالج (CPU Scheduling):**
    - محاكاة خوارزميات الجدولة الشهيرة:
      - FIFO (Ad-hoc / FCFS)
      - SJF (Shortest Job First) - Preemptive & Non-Preemptive
      - Priority Scheduling - Preemptive & Non-Preemptive
      - Round Robin (RR)
    - عرض النتائج في جدول وتوليد **مخطط غانت (Gantt Chart)**.
    - حساب متوسط زمن الانتظار (Waiting Time) وزمن الاستجابة (Turnaround Time).

2.  **🔒 الجمود (Deadlock - Banker's Algorithm):**
    - محاكاة **خوارزمية المصرفي (Banker's Algorithm)** للكشف عن حالة النظام الآمنة (Safe State).
    - إدخال مصفوفات الموارد (Allocation, Max, Available) ديناميكياً.
    - تتبع الخطوات خطوة بخطوة لرؤية كيف يتم تخصيص الموارد.

3.  **🧠 إدارة الذاكرة (Memory Management):**
    - محاكاة خوارزميات التسكين (Allocation Strategies):
      - First-Fit (التوافق الأول)
      - Best-Fit (التوافق الأفضل)
      - Worst-Fit (التوافق الأسوأ)
    - تمثيل بصري للذاكرة (Memory Map) يظهر العمليات والمساحات الفارغة.
    - حساب وعرض **التجزئة الخارجية (External Fragmentation)**.

4.  **📜 المعالجة الدفعية (Batch Processing):**
    - نظام يحاكي تنفيذ مجموعة من الأوامر بشكل تسلسلي (Batch Job).
    - محرر نصوص بسيط لكتابة الأوامر وتشغيلها دفعة واحدة.

5.  **💻 واجهة سطر الأوامر (Shell Simulation):**
    - محاكاة لطرفية (Terminal) تدعم أوامر أساسية.
    - دعم للإكمال التلقائي (Autocomplete) وسجل الأوامر (History).

---

## 🚀 طريقة التثبيت والتشغيل

### المتطلبات المسبقة

- يجب تثبيت **Python 3.x** على جهازك.

### خطوات التثبيت

1.  قم بتحميل المشروع أو استنساخ المستودع:

    ```bash
    git clone https://github.com/YourUsername/OS-Simulator.git
    cd OS-Simulator
    ```

2.  قم بتثبيت المكتبات اللازمة:

    ```bash
    pip install -r requirements.txt
    ```

3.  قم بتتشغيل البرنامج الرئيسي:
    ```bash
    python main.py
    ```

---

## 🛠️ التقنيات المستخدمة

- **اللغة البرمجية:** Python
- **واجهة المستخدم:** CustomTkinter (مكتبة حديثة مبنية على Tkinter)
- **المنطق:** خوارزميات مخصصة لكل وحدة (Logic Layer مفصول عن UI).

## 📄 حقوق الاستخدام

هذا المشروع مفتوح المصدر ومتاح للأغراض التعليمية.

---

**تم التطوير بواسطة:** Hawa Aldomini
