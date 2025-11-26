import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import os

# ---------------- Config ----------------
WINDOW_W, WINDOW_H = 1100, 720
BG_IMAGE = "background.png"
BUTTON_FG = "white"
BUTTON_BG_SPACE = "#BAC8DB"
BUTTON_COLOR = "#343675"

# ---------------- Icon Setup ----------------
ICON_FILE = "icon.png"  # your icon file path

# Set icon for main window (PNG via PhotoImage)
if os.path.exists(ICON_FILE):
    try:
        img = Image.open(ICON_FILE)
        root_icon = ImageTk.PhotoImage(img)
        try:
            root.iconbitmap("icon.ico")  # optional if you have .ico too
        except:
            # fallback to PNG
            tk.Tk.wm_iconphoto(tk.Tk(), True, root_icon)
    except Exception as e:
        print(f"Failed to load icon: {e}")

# Helper function to set icon for popups
def set_popup_icon(win):
    if os.path.exists(ICON_FILE):
        try:
            img = Image.open(ICON_FILE)
            icon_img = ImageTk.PhotoImage(img)
            win.wm_iconphoto(True, icon_img)
            # Keep reference to avoid garbage collection
            win.icon_img = icon_img
        except Exception as e:
            print(f"Failed to set popup icon: {e}")

# ---------------- Helpers ----------------
def percentage_from(s):
    total = s["c1"] + s["c2"] + s["c3"] + s["exam"]
    return round(total / 160 * 100, 2)

def grade_from(pct):
    if pct >= 70: return "A"
    if pct >= 60: return "B"
    if pct >= 50: return "C"
    if pct >= 40: return "D"
    return "F"

# ---------------- App ---------------------
class StudentApp:
    def __init__(self, root):
        self.root = root
        root.title("Student Manager")
        root.geometry(f"{WINDOW_W}x{WINDOW_H}")
        root.resizable(False, False)

        # ---------------- Background ----------------
        if os.path.exists(BG_IMAGE):
            bg = Image.open(BG_IMAGE).resize((WINDOW_W, WINDOW_H), Image.LANCZOS)
            self.bg_img = ImageTk.PhotoImage(bg)
            lbl = tk.Label(root, image=self.bg_img)
            lbl.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            root.configure(bg="#f0f0f0")
            
        # ---------------- Load Students ----------------
        self.students = self.load_students()

        # ---------------- Button Area ----------------
        self.button_frame = tk.Frame(root, bg=BUTTON_BG_SPACE, bd=0)
        self.button_frame.place(x=20, y=75, anchor="nw")  # slightly lowered

        # Define buttons with custom spacing
        button_texts = [
            ("View All", self.view_all_records, 20),
            ("View One", self.view_individual_record, 10),
            ("Highest", self.show_highest, 20),
            ("Lowest", self.show_lowest, 12),
            ("Sort", self.sort_students, 14),
            ("Add", self.add_student_window, 15),
            ("Delete", self.delete_student_window, 15),
            ("Update", self.update_student_window, 15),
        ]

        self.btn_widgets = []
        for col, (txt, cmd, pad) in enumerate(button_texts):
            # Adjust size for "View All"
            if txt == "View All":
                btn_width, btn_height = 103, 35  # slightly bigger
                pad_right = pad + 3
            else:
                btn_width, btn_height = 100, 32
                pad_right = pad

            btn_canvas = tk.Canvas(self.button_frame, width=btn_width, height=btn_height,
                                   highlightthickness=0, bg=self.button_frame["bg"], bd=0)
            btn_canvas.grid(row=0, column=col, padx=(pad, pad_right))

            # Semi-transparent button background
            img = Image.new("RGBA", (btn_width, btn_height), (52, 54, 117, 200))
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle((0, 0, btn_width, btn_height), radius=5, fill=(52, 54, 117, 200))
            photo = ImageTk.PhotoImage(img)
            btn_canvas.image = photo
            btn_canvas.create_image(0, 0, image=photo, anchor="nw")
            btn_canvas.create_text(btn_width//2, btn_height//2, text=txt, fill="white",
                                   font=("Segoe UI", 10, "bold"))

            btn_canvas.bind("<Button-1>", lambda e, f=cmd: f())

            # Hover effect
            def on_enter(event, canvas=btn_canvas, t=txt, w=btn_width, h=btn_height):
                img_hover = Image.new("RGBA", (w, h), (70, 70, 160, 220))
                draw_hover = ImageDraw.Draw(img_hover)
                draw_hover.rounded_rectangle((0, 0, w, h), radius=5, fill=(70, 70, 160, 220))
                photo_hover = ImageTk.PhotoImage(img_hover)
                canvas.image = photo_hover
                canvas.create_image(0, 0, image=photo_hover, anchor="nw")
                canvas.create_text(w//2, h//2, text=t, fill="white", font=("Segoe UI", 10, "bold"))

            def on_leave(event, canvas=btn_canvas, photo_orig=photo, t=txt, w=btn_width, h=btn_height):
                canvas.image = photo_orig
                canvas.create_image(0, 0, image=photo_orig, anchor="nw")
                canvas.create_text(w//2, h//2, text=t, fill="white", font=("Segoe UI", 10, "bold"))

            btn_canvas.bind("<Enter>", on_enter)
            btn_canvas.bind("<Leave>", on_leave)
            self.btn_widgets.append(btn_canvas)

        # ---------------- Table ----------------
        table_x, table_y = 30, 150
        table_w, table_h = 1040, 500

        self.canvas = tk.Canvas(root, width=table_w, height=table_h, highlightthickness=0)
        self.canvas.place(x=table_x, y=table_y)

        table_frame = tk.Frame(self.canvas, bg="white", bd=0)
        table_frame.place(relwidth=1, relheight=1)

        cols = ("code", "name", "course_total", "exam", "percent", "grade")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=20)
        self.tree.heading("code", text="Student Code")
        self.tree.heading("name", text="Student Name")
        self.tree.heading("course_total", text="Coursework Total")
        self.tree.heading("exam", text="Exam Mark")
        self.tree.heading("percent", text="Percentage")
        self.tree.heading("grade", text="Grade")
        self.tree.column("code", width=130, anchor="center")
        self.tree.column("name", width=350, anchor="w")
        self.tree.column("course_total", width=140, anchor="center")
        self.tree.column("exam", width=100, anchor="center")
        self.tree.column("percent", width=120, anchor="center")
        self.tree.column("grade", width=80, anchor="center")

        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28,
                        background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

        vscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.update_table(self.students)

    # ---------------- Load / Save ----------------
    def load_students(self):
        students = []
        if not os.path.exists("studentMarks.txt"):
            with open("studentMarks.txt", "w") as f:
                f.write("0\n")
            return students
        try:
            with open("studentMarks.txt", "r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f if ln.strip()]
            for line in lines[1:]:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) != 6: continue
                code, name = parts[0], parts[1]
                try:
                    c1, c2, c3, exam = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
                except ValueError:
                    continue
                students.append({"code": code, "name": name, "c1": c1, "c2": c2, "c3": c3, "exam": exam})
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read studentMarks.txt: {e}")
        return students

    def save_students(self):
        try:
            with open("studentMarks.txt", "w", encoding="utf-8") as f:
                f.write(str(len(self.students)) + "\n")
                for s in self.students:
                    f.write(f"{s['code']},{s['name']},{s['c1']},{s['c2']},{s['c3']},{s['exam']}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    # ---------------- Table Update ----------------
    def update_table(self, data):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for s in data:
            total_course = s["c1"] + s["c2"] + s["c3"]
            pct = percentage_from(s)
            grd = grade_from(pct)
            self.tree.insert("", "end", values=(s["code"], s["name"], total_course, s["exam"], f"{pct:.2f}%", grd))

    # ---------------- Features ----------------
    def view_all_records(self):
        self.update_table(self.students)
        if self.students:
            avg = round(sum(percentage_from(s) for s in self.students)/len(self.students), 2)
            messagebox.showinfo("Class Summary", f"Students: {len(self.students)}\nAverage %: {avg}%")

    def view_individual_record(self):
        win = tk.Toplevel(self.root)
        set_popup_icon(win)
        win.title("Find Student")
        win.geometry("360x160")
        win.resizable(False, False)
        tk.Label(win, text="Enter Code or Name:", font=("Segoe UI", 10)).pack(pady=(12, 6))
        entry = tk.Entry(win, font=("Segoe UI", 11))
        entry.pack(padx=12, fill="x")

        def do_search():
            key = entry.get().strip().lower()
            if not key:
                return
            results = [s for s in self.students if key == s["code"].lower() or key in s["name"].lower()]
            self.update_table(results)
            win.destroy()

        tk.Button(win, text="Search", bg=BUTTON_COLOR, fg="white", command=do_search).pack(pady=12)

    def show_highest(self):
        if not self.students: return
        best = max(self.students, key=lambda s: percentage_from(s))
        self.update_table([best])

    def show_lowest(self):
        if not self.students: return
        worst = min(self.students, key=lambda s: percentage_from(s))
        self.update_table([worst])

    def sort_students(self):
        win = tk.Toplevel(self.root)
        set_popup_icon(win)
        win.title("Sort")
        win.geometry("320x140")
        win.resizable(False, False)
        tk.Label(win, text="Sort by total percentage:", font=("Segoe UI", 10)).pack(pady=(12, 6))

        def asc():
            self.students.sort(key=lambda s: percentage_from(s))
            self.update_table(self.students)
            win.destroy()

        def desc():
            self.students.sort(key=lambda s: percentage_from(s), reverse=True)
            self.update_table(self.students)
            win.destroy()

        frm = tk.Frame(win)
        frm.pack(pady=8)
        tk.Button(frm, text="Ascending", width=12, bg=BUTTON_COLOR, fg="white", command=asc).grid(row=0, column=0, padx=6)
        tk.Button(frm, text="Descending", width=12, bg=BUTTON_COLOR, fg="white", command=desc).grid(row=0, column=1, padx=6)

    # ---------------- Add / Delete / Update ----------------
    def add_student_window(self):
        win = tk.Toplevel(self.root)
        set_popup_icon(win)
        win.title("Add Student")
        win.geometry("360x400")
        win.resizable(False, False)
        labels = ["Code", "Name", "Course1 (0-20)", "Course2 (0-20)", "Course3 (0-20)", "Exam (0-100)"]
        entries = {}
        for txt in labels:
            tk.Label(win, text=txt, font=("Segoe UI", 10)).pack(pady=(8, 0), anchor="w", padx=12)
            e = tk.Entry(win, font=("Segoe UI", 11))
            e.pack(padx=12, fill="x")
            entries[txt] = e

        def save():
            try:
                code = entries[labels[0]].get().strip()
                name = entries[labels[1]].get().strip()
                c1 = int(entries[labels[2]].get())
                c2 = int(entries[labels[3]].get())
                c3 = int(entries[labels[4]].get())
                exam = int(entries[labels[5]].get())
            except ValueError:
                messagebox.showerror("Error", "Invalid input — marks must be integers.")
                return
            if not code or not name:
                messagebox.showerror("Error", "Code and name are required.")
                return
            if any(s["code"].lower() == code.lower() for s in self.students):
                messagebox.showerror("Error", "Student code already exists.")
                return
            for m, lim in ((c1,20),(c2,20),(c3,20),(exam,100)):
                if m < 0 or m > lim:
                    messagebox.showerror("Error", f"Marks must be between 0 and {lim}.")
                    return
            new = {"code": code, "name": name, "c1": c1, "c2": c2, "c3": c3, "exam": exam}
            self.students.append(new)
            self.save_students()
            self.update_table(self.students)
            win.destroy()

        tk.Button(win, text="Save", bg=BUTTON_COLOR, fg="white", command=save).pack(pady=12)

    def delete_student_window(self):
        win = tk.Toplevel(self.root)
        set_popup_icon(win)
        win.title("Delete Student")
        win.geometry("340x140")
        win.resizable(False, False)
        tk.Label(win, text="Enter Code or Name to delete:", font=("Segoe UI", 10)).pack(pady=(12,6))
        entry = tk.Entry(win, font=("Segoe UI", 11))
        entry.pack(padx=12, fill="x")

        def do_delete():
            key = entry.get().strip().lower()
            if not key: return
            before = len(self.students)
            self.students = [s for s in self.students if not (s["code"].lower() == key or key in s["name"].lower())]
            after = len(self.students)
            if after < before:
                self.save_students()
                self.update_table(self.students)
                win.destroy()
            else:
                messagebox.showinfo("Not found", "No matching student found.")

        tk.Button(win, text="Delete", bg=BUTTON_COLOR, fg="white", command=do_delete).pack(pady=10)

    def update_student_window(self):
        win = tk.Toplevel(self.root)
        set_popup_icon(win)
        win.title("Find Student to Update")
        win.geometry("340x160")
        win.resizable(False, False)
        tk.Label(win, text="Enter Code or Name:", font=("Segoe UI", 10)).pack(pady=(12,6))
        entry = tk.Entry(win, font=("Segoe UI", 11))
        entry.pack(padx=12, fill="x")

        def find_and_edit():
            key = entry.get().strip().lower()
            for s in self.students:
                if s["code"].lower() == key or key in s["name"].lower():
                    self.open_update_form(s)
                    win.destroy()
                    return
            messagebox.showinfo("Not found", "Student not found.")

        tk.Button(win, text="Find", bg=BUTTON_COLOR, fg="white", command=find_and_edit).pack(pady=10)

    def open_update_form(self, student):
        win = tk.Toplevel(self.root)
        set_popup_icon(win)
        win.title("Update Student")
        win.geometry("360x360")
        win.resizable(False, False)
        labels = ["Name", "Course1 (0-20)", "Course2 (0-20)", "Course3 (0-20)", "Exam (0-100)"]
        entries = {}
        defaults = [student["name"], str(student["c1"]), str(student["c2"]), str(student["c3"]), str(student["exam"])]
        for txt, d in zip(labels, defaults):
            tk.Label(win, text=txt, font=("Segoe UI", 10)).pack(pady=(8,0), anchor="w", padx=12)
            e = tk.Entry(win, font=("Segoe UI", 11))
            e.pack(padx=12, fill="x")
            e.insert(0, d)
            entries[txt] = e

        def save():
            try:
                student["name"] = entries[labels[0]].get().strip()
                student["c1"] = int(entries[labels[1]].get())
                student["c2"] = int(entries[labels[2]].get())
                student["c3"] = int(entries[labels[3]].get())
                student["exam"] = int(entries[labels[4]].get())
            except:
                messagebox.showerror("Error", "Invalid input")
                return
            for m, lim in ((student["c1"],20),(student["c2"],20),(student["c3"],20),(student["exam"],100)):
                if m < 0 or m > lim:
                    messagebox.showerror("Error", f"Marks must be in range 0-{lim}")
                    return
            self.save_students()
            self.update_table(self.students)
            win.destroy()

        tk.Button(win, text="Save Changes", bg=BUTTON_COLOR, fg="white", command=save).pack(pady=12)

# ---------------- Run ---------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()
