# Math Quiz - Exercise 1
# Coded by Maria Angelica Gilleone Dy Rapsing | CC Y2 BSU G2
# Sources:
# - Tkinter basic GUI: https://docs.python.org/3/library/tkinter.html
# - Random number generation: https://docs.python.org/3/library/random.html
# - Progress bar idea inspired by: https://stackoverflow.com/questions/54105054/simple-progress-bar-in-tkinter
# Note: I wanted to change the color of the progress bar for correct/partial/wrong answers and wasn't sure how, so I asked AI to help with that part. Other than that, the code is written by me with the help of multiple sources.

import tkinter as tk
from tkinter import messagebox
import random

class MathQuiz:
    def __init__(self, root):
        self.root = root
        self.root.title("Math Quiz")
        self.root.geometry("800x600")
        self.root.resizable(True, True)  # Let window resize, feels better than fixed

        # Variables for tracking quiz progress
        self.level = 0
        self.score = 0
        self.q_num = 0
        self.attempt = 0
        self.total_questions = 10
        self.results = []  # Will hold colors for the progress bar
        self.num1 = 0
        self.num2 = 0
        self.correct_answer = 0

        # Frames for "pages"
        self.menu_frame = tk.Frame(root)
        self.quiz_frame = tk.Frame(root, bg="#f0f8ff")  # Light blue background for quiz
        self.result_frame = tk.Frame(root, bg="#f0f8ff")
        
        self.show_menu()  # Start with menu

    # ---------------- Menu ----------------
    def show_menu(self):
        """Display the main menu with difficulty options"""
        self.clear_frames()
        self.menu_frame.pack(expand=True, fill="both")

        # Title
        tk.Label(self.menu_frame, text="🧮 MATH QUIZ 🧮",
                 font=("Comic Sans MS", 36, "bold"), fg="#4a90e2").pack(pady=30)

        # Subtitle
        tk.Label(self.menu_frame, text="Select Difficulty Level",
                 font=("Comic Sans MS", 22), fg="#555").pack(pady=10)

        # Difficulty buttons (colors: easy=green, intermediate=yellow pastel, advanced=pink)
        for lvl, color in [("Easy","#a8e6cf"),("Intermediate","#fff59d"),("Advanced","#ff8b94")]:
            tk.Button(self.menu_frame, text=lvl, width=20, height=3,
                      font=("Comic Sans MS", 18, "bold"),
                      bg=color,
                      command=lambda l=lvl.lower(): self.start_quiz(l)).pack(pady=15)

        # Footer info
        tk.Label(self.menu_frame, text=f"Each quiz has {self.total_questions} questions",
                 font=("Comic Sans MS", 14), fg="#555").pack(side="bottom", pady=20)

    # ---------------- Helper Functions ----------------
    def clear_frames(self):
        """Hide all frames and delete their widgets (simulate page change)"""
        for f in [self.menu_frame, self.quiz_frame, self.result_frame]:
            f.pack_forget()
            for w in f.winfo_children():
                w.destroy()

    def random_int(self):
        """Return a random integer depending on the difficulty level"""
        if self.level == "easy":
            return random.randint(1, 9)
        elif self.level == "intermediate":
            return random.randint(10, 99)
        else:
            return random.randint(100, 9999)

    def choose_operation(self):
        """Randomly pick addition or subtraction"""
        return random.choice(["+", "-"])

    # ---------------- Quiz Functions ----------------
    def start_quiz(self, level):
        """Reset quiz stats and show first question"""
        self.level = level
        self.score = 0
        self.q_num = 0
        self.attempt = 1
        self.results = []
        self.show_question()

    def show_question(self):
        """Show current question, answer entry, and progress bar"""
        self.clear_frames()
        self.quiz_frame.pack(expand=True, fill="both")

        # Generate numbers and operation
        self.num1 = self.random_int()
        self.num2 = self.random_int()
        self.operation = self.choose_operation()
        self.correct_answer = self.num1 + self.num2 if self.operation == "+" else self.num1 - self.num2

        # Question counter
        tk.Label(self.quiz_frame, text=f"Question {self.q_num+1} of {self.total_questions}",
                 font=("Comic Sans MS", 20), bg="#f0f8ff").pack(pady=(20,5))

        # Score display
        tk.Label(self.quiz_frame, text=f"Score: {self.score}",
                 font=("Comic Sans MS", 20, "bold"), bg="#f0f8ff", fg="#333").pack(pady=(0,10))

        # Question text
        tk.Label(self.quiz_frame, text=f"{self.num1} {self.operation} {self.num2} = ?",
                 font=("Comic Sans MS", 36, "bold"), bg="#f0f8ff", fg="#000").pack(pady=10)

        # Entry box
        self.answer_entry = tk.Entry(self.quiz_frame, font=("Comic Sans MS", 24), justify="center")
        self.answer_entry.pack(pady=10)
        self.answer_entry.focus()

        # Submit button
        tk.Button(self.quiz_frame, text="Submit", font=("Comic Sans MS", 16), width=14,
                  bg="#4a90e2", fg="white", command=self.check_answer).pack(pady=10)

        # Back to menu button
        tk.Button(self.quiz_frame, text="Back to Menu", font=("Comic Sans MS", 14), width=14,
                  bg="#999", fg="white", command=self.show_menu).pack(pady=5)

        # Progress bar
        self.create_progress_bar()

    # ---------------- Progress Bar ----------------
    def create_progress_bar(self):
        """Create a small box progress bar that changes color based on results"""
        self.bar_frame = tk.Frame(self.quiz_frame, bg="#dce6f2", width=600, height=40, bd=2, relief="solid")
        self.bar_frame.pack(pady=20)
        self.bar_frame.pack_propagate(False)

        self.bar_segments = []
        seg_width = 580 / self.total_questions
        for _ in range(self.total_questions):
            seg = tk.Frame(self.bar_frame, bg="#e6f0fa", width=seg_width, height=36)
            seg.pack(side="left", padx=1)
            self.bar_segments.append(seg)

        self.update_progress_bar()

    def update_progress_bar(self):
        """Update colors of the small boxes based on correct/partial/wrong answers"""
        for i, color in enumerate(self.results):
            self.bar_segments[i].config(bg=color)

    # ---------------- Answer Check ----------------
    def check_answer(self):
        """Check user's answer, update score and progress"""
        try:
            ans = int(self.answer_entry.get())
        except ValueError:
            messagebox.showwarning("Invalid", "Please enter an integer.")
            return

        correct_msgs = ["Great job!", "Awesome!", "You got it!", "Correct!", "Nice!"]
        wrong_msgs = ["Oops!", "Try again!", "Not quite!", "Incorrect!", "Keep going!"]

        if ans == self.correct_answer:
            points = 10 if self.attempt == 1 else 5
            self.score += points
            color = "#4caf50" if self.attempt == 1 else "#fff59d"  # Green or pastel yellow
            self.results.append(color)
            messagebox.showinfo("Correct", f"{random.choice(correct_msgs)} You earned {points} points.")
            self.next_question()
        else:
            if self.attempt == 1:
                self.attempt = 2
                messagebox.showwarning("Try again", f"{random.choice(wrong_msgs)} ❌ Incorrect. Try again!")
                self.answer_entry.delete(0, 'end')
            else:
                self.results.append("#e57373")  # Red for wrong
                messagebox.showerror("Incorrect", f"❌ Incorrect. The correct answer was {self.correct_answer}.")
                self.next_question()

        self.update_progress_bar()

    def next_question(self):
        """Go to the next question or show results if quiz is done"""
        self.q_num += 1
        self.attempt = 1
        if self.q_num >= self.total_questions:
            self.show_results()
        else:
            self.show_question()

    # ---------------- Results Page ----------------
    def show_results(self):
        """Display final score, rank, and options to play again or go back"""
        self.clear_frames()
        self.result_frame.pack(expand=True, fill="both")

        tk.Label(self.result_frame, text="🎉 Quiz Completed! 🎉",
                 font=("Comic Sans MS", 28, "bold"), bg="#f0f8ff", fg="#4a90e2").pack(pady=30)

        tk.Label(self.result_frame, text=f"Your Score: {self.score} / 100",
                 font=("Comic Sans MS", 20), bg="#f0f8ff", fg="#555").pack(pady=10)

        tk.Label(self.result_frame, text=f"Your Rank: {self.get_rank()}",
                 font=("Comic Sans MS", 20, "bold"), bg="#f0f8ff", fg="#4caf50").pack(pady=10)

        tk.Button(self.result_frame, text="Play Again", font=("Comic Sans MS", 16), width=18,
                  bg="#4a90e2", fg="white", command=lambda: self.start_quiz(self.level)).pack(pady=10)

        tk.Button(self.result_frame, text="Back to Menu", font=("Comic Sans MS", 14), width=18,
                  bg="#999", fg="white", command=self.show_menu).pack(pady=5)

        # Show final progress bar
        self.create_progress_bar()

    def get_rank(self):
        """Determine letter grade based on score"""
        if self.score >= 90: return "A+"
        if self.score >= 80: return "A"
        if self.score >= 70: return "B"
        if self.score >= 60: return "C"
        return "D"

if __name__ == "__main__":
    root = tk.Tk()
    app = MathQuiz(root)
    root.mainloop()