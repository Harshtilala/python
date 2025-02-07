import customtkinter as ctk
from tkinter import messagebox
import mysql.connector

# Dark Blue Color Scheme
COLORS = {
    "primary": "#1A237E",
    "secondary": "#0D47A1",
    "background": "#0D1A35",
    "text": "#FFFFFF",
    "button": "#1976D2",
    "hover": "#1565C0"
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='chat_app'
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def fetch_one(self, query, params=None):
        self.cursor.execute(query, params) if params else self.cursor.execute(query)
        return self.cursor.fetchone()

    def execute(self, query, params=None):
        self.cursor.execute(query, params)
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Secure Login")
        self.geometry("500x550")
        self.configure(fg_color=COLORS["background"])
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, padx=40, pady=40)

        # Header
        ctk.CTkLabel(main_frame, text="SECURE LOGIN", 
                    font=("Arial", 24, "bold"),
                    text_color=COLORS["text"]).pack(pady=(0, 30))

        # Email Input
        email_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        email_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(email_frame, text="Email:", 
                    text_color=COLORS["text"]).pack(anchor="w")
        self.email_entry = ctk.CTkEntry(email_frame, 
                                      placeholder_text="Enter your email",
                                      fg_color="#2E3B4E",
                                      border_color=COLORS["primary"],
                                      border_width=1)
        self.email_entry.pack(fill="x", pady=5)

        # Password Input
        password_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        password_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(password_frame, text="Password:", 
                    text_color=COLORS["text"]).pack(anchor="w")
        self.password_entry = ctk.CTkEntry(password_frame, 
                                         show="*",
                                         fg_color="#2E3B4E",
                                         border_color=COLORS["primary"],
                                         border_width=1)
        self.password_entry.pack(fill="x", pady=5)

        # Login Button
        ctk.CTkButton(main_frame, text="Login", 
                     command=self.login_user,
                     fg_color=COLORS["button"],
                     hover_color=COLORS["hover"],
                     height=40).pack(fill="x", pady=20)

        # Register Link
        register_link = ctk.CTkLabel(main_frame, 
                                   text="Create new account", 
                                   text_color=COLORS["secondary"],
                                   cursor="hand2",
                                   font=("Arial", 12, "underline"))
        register_link.pack(pady=10)
        register_link.bind("<Button-1>", lambda e: self.open_register())

    def login_user(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showerror("Error", "All fields are required!")
            return

        db = Database()
        user = db.fetch_one("SELECT * FROM users WHERE email = %s", (email,))
        db.close()

        if user and password == user['password']:
            messagebox.showinfo("Success", f"Welcome {user['username']}!")
            self.withdraw()  # Hide the login window
            self.open_dashboard(user)
        else:
            messagebox.showerror("Error", "Invalid credentials!")

    def open_dashboard(self, user):
        from chat_dashboard import ChatDashboard
        dashboard = ChatDashboard(user['id'], user['username'], self)
        dashboard.mainloop()

    def open_register(self):
        self.withdraw()
        RegisterWindow(self)
        self.wait_window(RegisterWindow)
        self.deiconify()

class RegisterWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Create Account")
        self.geometry("500x600")
        self.configure(fg_color=COLORS["background"])
        self.master = master
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, padx=40, pady=40)

        # Header
        ctk.CTkLabel(main_frame, text="NEW ACCOUNT", 
                    font=("Arial", 24, "bold"),
                    text_color=COLORS["text"]).pack(pady=(0, 30))

        # Username Input
        username_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        username_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(username_frame, text="Username:", 
                    text_color=COLORS["text"]).pack(anchor="w")
        self.username_entry = ctk.CTkEntry(username_frame, 
                                         fg_color="#2E3B4E",
                                         border_color=COLORS["primary"],
                                         border_width=1)
        self.username_entry.pack(fill="x", pady=5)

        # Email Input
        email_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        email_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(email_frame, text="Email:", 
                    text_color=COLORS["text"]).pack(anchor="w")
        self.email_entry = ctk.CTkEntry(email_frame, 
                                      fg_color="#2E3B4E",
                                      border_color=COLORS["primary"],
                                      border_width=1)
        self.email_entry.pack(fill="x", pady=5)

        # Password Input
        password_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        password_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(password_frame, text="Password:", 
                    text_color=COLORS["text"]).pack(anchor="w")
        self.password_entry = ctk.CTkEntry(password_frame, 
                                         show="*",
                                         fg_color="#2E3B4E",
                                         border_color=COLORS["primary"],
                                         border_width=1)
        self.password_entry.pack(fill="x", pady=5)

        # Register Button
        ctk.CTkButton(main_frame, text="Create Account", 
                     command=self.register_user,
                     fg_color=COLORS["button"],
                     hover_color=COLORS["hover"],
                     height=40).pack(fill="x", pady=20)

    def register_user(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not all([username, email, password]):
            messagebox.showerror("Error", "All fields are required!")
            return

        db = Database()
        try:
            db.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, password)
            )
            messagebox.showinfo("Success", "Account created successfully!")
            # Auto-fill login email and close window
            self.master.email_entry.delete(0, 'end')
            self.master.email_entry.insert(0, email)
            self.destroy()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Account already exists!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()