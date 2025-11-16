# Alexa tell me a joke - Excercise 2 
# Coded by Maria Angelica Gilleone Dy Rapsing | CC Y2 BSU G2
# Sources:
# - Python Official Documentation: https://docs.python.org/3/library/tkinter.html
# - Tkinter Canvas Rounded Rectangle Techniques: https://stackoverflow.com/questions/44099594/how-to-make-rounded-buttons-in-tkinter
# - Typewriter-style text animation: Custom implementation using Tkinter 'after' method : https://www.geeksforgeeks.org/how-to-create-typewriter-text-animation-in-tkinter/
# - GUI Design Inspiration: Standard Tkinter layout patterns and pastel-themed UI ideas : 
# - Pastel color schemes: https://colorhunt.co/palette/pastel
# - Tkinter layout patterns: https://realpython.com/python-gui-tkinter/

import tkinter as tk
import random
import os

# ----------------- Load jokes from file -----------------
def load_jokes():
    """
    Load jokes from 'randomJokes.txt' in the same directory as the script.
    Each joke is split into (setup, punchline) using the first question mark.
    """
    path = os.path.join(os.path.dirname(__file__), "randomJokes.txt")
    jokes = []
    if not os.path.exists(path):
        print("Jokes file not found:", path)
        return jokes
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            qm = line.find("?")
            if qm != -1:
                setup = line[:qm+1]
                punchline = line[qm+1:].strip()
                jokes.append((setup, punchline))
    return jokes

# ----------------- Main Application Class -----------------
class JokeApp:
    def __init__(self, root):
        # Basic setup
        self.root = root
        self.root.title("Alexa Joke Assistant")
        self.root.geometry("520x650")
        self.root.resizable(False, False)

        # ----------------- Data -----------------
        self.jokes = load_jokes()  # Load jokes
        self.current_joke = None   # Currently displayed joke
        self.anim_after_id = None  # For animated text
        self.card_offset = 0       # For floating card animation
        self.card_direction = 1

        # ----------------- Theme definitions -----------------
        # pastel/light/dark themes, with card text color
        self.themes = {
            "Mint": {"bg": "#d0f0c0", "fg": "#344e41", "button_bg": "#a7e4a0", "button_fg": "#344e41",
                     "card_bg": "#ffffff", "card_fg": "#344e41"},
            "Peach": {"bg": "#ffe5b4", "fg": "#5c4033", "button_bg": "#ffd1a4", "button_fg": "#5c4033",
                      "card_bg": "#fff5e6", "card_fg": "#5c4033"},
            "Lavender": {"bg": "#e6e6fa", "fg": "#4b0082", "button_bg": "#d8bfd8", "button_fg": "#4b0082",
                         "card_bg": "#f3e6ff", "card_fg": "#4b0082"},
            "Light Mode": {"bg": "#f0f0f0", "fg": "#333333", "button_bg": "#e0e0e0", "button_fg": "#333333",
                           "card_bg": "#ffffff", "card_fg": "#333333"},
            "Dark Mode": {"bg": "#1c1c1c", "fg": "#f0f0f0", "button_bg": "#333333", "button_fg": "#f0f0f0",
                          "card_bg": "#2b2b2b", "card_fg": "#f0f0f0"}
        }
        self.current_theme = "Mint"  # Default theme

        # ----------------- Start Menu -----------------
        self.frame_start = tk.Frame(root)
        self.frame_start.pack(fill="both", expand=True)

        # Title label with subtle animation
        self.title_label = tk.Label(self.frame_start, text="Alexa, tell me a Joke",
                                    font=("Comic Sans MS", 28, "bold"))
        self.title_label.pack(pady=60)
        self.title_scale = 1.0
        self.title_dir = 1
        self.animate_title()  # Start subtle scale animation

        # Start button
        self.button_start = tk.Button(self.frame_start, text="Start Jokes", font=("Comic Sans MS",16,"bold"),
                                      width=20, command=self.start_jokes)
        self.button_start.pack(pady=10)

        # Quit button
        self.button_quit_start = tk.Button(self.frame_start, text="Quit", font=("Comic Sans MS",14),
                                           width=20, command=root.quit)
        self.button_quit_start.pack(pady=10)

        # Settings button
        self.button_settings_start = tk.Button(self.frame_start, text="Settings ⚙", font=("Comic Sans MS",12),
                                               width=20, command=self.open_settings)
        self.button_settings_start.pack(pady=20)

        # ----------------- Joke Screen -----------------
        self.frame_joke = tk.Frame(root)

        # Card container (top frame, holds rounded card)
        self.card_frame = tk.Frame(self.frame_joke, width=460, height=300)
        self.card_frame.pack(pady=(30,15))

        # Canvas for rounded card
        self.card_canvas = tk.Canvas(self.card_frame, width=460, height=300, bd=0, highlightthickness=0)
        self.card_canvas.pack()
        self.card_radius = 25

        # Labels inside the card
        self.label_setup = tk.Label(self.card_canvas, text="", font=("Comic Sans MS",16), wraplength=400,
                                    justify="center")
        self.label_punchline = tk.Label(self.card_canvas, text="", font=("Comic Sans MS",18,"bold"),
                                        wraplength=400, justify="center")
        self.card_canvas.create_window(230, 100, window=self.label_setup)
        self.card_canvas.create_window(230, 200, window=self.label_punchline)

        # Buttons frame (below card)
        self.frame_buttons = tk.Frame(self.frame_joke)
        self.frame_buttons.pack(pady=15)
        self.button_show = tk.Button(self.frame_buttons, text="Show Punchline", font=("Comic Sans MS",12),
                                     width=15, state=tk.DISABLED, command=self.show_punchline)
        self.button_show.grid(row=0,column=0,padx=5,pady=5)
        self.button_next = tk.Button(self.frame_buttons, text="Next Joke", font=("Comic Sans MS",12),
                                     width=15, state=tk.DISABLED, command=self.show_joke)
        self.button_next.grid(row=0,column=1,padx=5,pady=5)
        self.button_menu = tk.Button(self.frame_buttons, text="Main Menu", font=("Comic Sans MS",12),
                                     width=32, command=self.show_start_menu)
        self.button_menu.grid(row=1,column=0,columnspan=2,pady=5)

        # Settings button top-right on joke screen
        self.button_settings = tk.Button(self.frame_joke, text="⚙", font=("Comic Sans MS",12,"bold"),
                                         width=3, command=self.open_settings)
        self.button_settings.place(relx=0.92, rely=0.02)

        # Apply theme and draw card
        self.apply_theme()
        self.float_card()  # Start floating animation

    # ----------------- Subtle title animation -----------------
    def animate_title(self):
        """
        Makes the start menu title subtly scale up and down.
        """
        new_size = 28 + self.title_dir
        if new_size > 30 or new_size < 28:
            self.title_dir *= -1
            new_size = 28 + self.title_dir
        self.title_label.config(font=("Comic Sans MS", new_size, "bold"))
        self.root.after(300, self.animate_title)

    # ----------------- Apply theme -----------------
    def apply_theme(self):
        """
        Update all widget colors according to the current theme.
        Ensures card text is readable in dark mode.
        """
        theme = self.themes[self.current_theme]
        self.root.configure(bg=theme["bg"])
        for frame in [self.frame_start, self.frame_joke, self.frame_buttons, self.card_frame]:
            frame.configure(bg=theme["bg"])
        self.title_label.configure(bg=theme["bg"], fg=theme["fg"])
        for button in [self.button_start, self.button_quit_start, self.button_settings_start,
                       self.button_settings] + self.frame_buttons.winfo_children():
            button.configure(bg=theme["button_bg"], fg=theme["button_fg"],
                             activebackground=theme["bg"], activeforeground=theme["fg"])
        self.card_bg = theme["card_bg"]
        self.label_setup.configure(bg=self.card_bg, fg=theme["card_fg"])
        self.label_punchline.configure(bg=self.card_bg, fg=theme["card_fg"])
        self.draw_rounded_card()

    # ----------------- Draw rounded card -----------------
    def draw_rounded_card(self):
        """
        Draws a rounded rectangle on the canvas to simulate a card.
        Uses arcs for corners and rectangles for sides.
        """
        self.card_canvas.delete("card")
        w,h,r = 460,300,self.card_radius
        # Four corners
        self.card_canvas.create_arc(0,0,2*r,2*r,start=90,extent=90,fill=self.card_bg, outline=self.card_bg, tags="card")
        self.card_canvas.create_arc(w-2*r,0,w,h,start=0,extent=90,fill=self.card_bg, outline=self.card_bg, tags="card")
        self.card_canvas.create_arc(0,h-2*r,2*r,h,start=180,extent=90,fill=self.card_bg, outline=self.card_bg, tags="card")
        self.card_canvas.create_arc(w-2*r,h-2*r,w,h,start=270,extent=90,fill=self.card_bg, outline=self.card_bg, tags="card")
        # Rectangles connecting corners
        self.card_canvas.create_rectangle(r,0,w-r,h,fill=self.card_bg, outline=self.card_bg, tags="card")
        self.card_canvas.create_rectangle(0,r,w,h-r,fill=self.card_bg, outline=self.card_bg, tags="card")

    # ----------------- Menu navigation -----------------
    def start_jokes(self):
        """Hide start menu and show joke screen"""
        self.frame_start.pack_forget()
        self.frame_joke.pack(fill="both", expand=True)
        self.show_joke()

    def show_start_menu(self):
        """Return to start menu from joke screen"""
        self.frame_joke.pack_forget()
        self.frame_start.pack(fill="both", expand=True)

    # ----------------- Show joke -----------------
    def show_joke(self):
        """Pick a random joke and animate the setup text"""
        if not self.jokes:
            self.label_setup.config(text="No jokes found!")
            return
        if self.anim_after_id:
            self.root.after_cancel(self.anim_after_id)
            self.anim_after_id = None
        self.current_joke = random.choice(self.jokes)
        setup,_ = self.current_joke
        self.label_setup.config(text="")
        self.label_punchline.config(text="")
        self.button_show.config(state=tk.DISABLED)
        self.button_next.config(state=tk.DISABLED)
        self.animate_text(self.label_setup, setup, after_done=self.enable_buttons)

    def enable_buttons(self):
        """Enable the Show Punchline and Next Joke buttons after setup appears"""
        self.button_show.config(state=tk.NORMAL)
        self.button_next.config(state=tk.NORMAL)

    def show_punchline(self):
        """Animate and show the punchline"""
        punchline = self.current_joke[1]
        self.animate_text(self.label_punchline, punchline)

    def animate_text(self, label, text, index=0, after_done=None):
        """
        Typewriter-like text animation.
        Gradually reveals text in the label.
        """
        if index <= len(text):
            label.config(text=text[:index])
            self.anim_after_id = self.root.after(20, lambda:self.animate_text(label,text,index+1,after_done))
        else:
            self.anim_after_id = None
            if after_done:
                after_done()

    # ----------------- Settings popup -----------------
    def open_settings(self):
        """Open a small settings window to select theme"""
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("300x200")
        win.resizable(False, False)
        tk.Label(win, text="Select Theme:", font=("Comic Sans MS",12)).pack(pady=10)
        theme_var = tk.StringVar(value=self.current_theme)
        tk.OptionMenu(win, theme_var, *self.themes.keys(),
                      command=lambda val: self.change_theme(val)).pack(pady=5)
        tk.Button(win, text="Close", command=win.destroy).pack(pady=20)

    def change_theme(self, value):
        """Update current theme and refresh UI"""
        self.current_theme = value
        self.apply_theme()

    # ----------------- Floating card animation -----------------
    def float_card(self):
        """Makes the joke card gently float up and down"""
        self.card_offset += self.card_direction
        if abs(self.card_offset) > 5:
            self.card_direction *= -1
        self.card_frame.place(x=30, y=150 + self.card_offset)
        self.root.after(100, self.float_card)

# ----------------- Run the application -----------------
if __name__=="__main__":
    root = tk.Tk()
    app = JokeApp(root)
    root.mainloop()

