import customtkinter as ctk
from tkinter import messagebox
import mysql.connector

class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password='',  # Replace with your MySQL password (leave empty if none)
            database='chat_app'  # Replace with your database name
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def fetch_one(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchone()

    def close(self):
        self.cursor.close()
        self.connection.close()

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("400x350")
        self.resizable(False, False)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        title_label = ctk.CTkLabel(self, text="Login Form", font=("Arial", 20, "bold"))
        title_label.pack(pady=20)

        email_label = ctk.CTkLabel(self, text="Email:", font=("Arial", 14))
        email_label.pack(pady=(10, 0))
        self.email_entry = ctk.CTkEntry(self, placeholder_text="Enter your email")
        self.email_entry.pack(pady=(0, 10), padx=20)

        password_label = ctk.CTkLabel(self, text="Password:", font=("Arial", 14))
        password_label.pack(pady=(10, 0))
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Enter your password", show="*")
        self.password_entry.pack(pady=(0, 20), padx=20)

        login_button = ctk.CTkButton(
            self,
            text="Login",
            command=self.login_user,
            fg_color="#1f6aa5",
            hover_color="#144870",
            font=("Arial", 16)
        )
        login_button.pack(pady=20)

        register_button = ctk.CTkButton(
            self,
            text="Don't have an account? Register",
            command=self.open_register_window,
            fg_color="#2E8B57",
            hover_color="#3CB371",
            font=("Arial", 12)
        )
        register_button.pack(pady=(10, 20))

    def login_user(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showerror("Error", "All fields are required!")
            return

        db = Database()
        
        query = "SELECT * FROM users WHERE email = %s"
        
        user = db.fetch_one(query, (email,))
        
        if user and password == user['password']:  # Check plain text password
            messagebox.showinfo("Success", f"Welcome {user['username']}!")
            
            # Open the chat dashboard
            self.open_chat_dashboard(user['id'], user['username'])  # Pass the user ID and username to the chat window
            
            self.destroy()  # Close the login window after opening the chat dashboard
        else:
            messagebox.showerror("Error", "Invalid email or password!")

    def open_chat_dashboard(self, user_id, username):
        """Function to open the chat dashboard."""
        from chat_dashboard import ChatDashboard  # Import here to avoid circular dependency
        chat_window = ChatDashboard(user_id, username)  # Pass the user ID and username to the chat window
        chat_window.mainloop()  # Start the Chat Dashboard main loop

    def open_register_window(self):
        """Opens the registration window."""
        register_window = RegisterWindow()
        register_window.mainloop()  # Start the Register Window main loop
        self.destroy()  # Close the Login Window

class RegisterWindow(ctk.CTk):
    def __init__(self):
         super().__init__()
         self.title("Register")
         self.geometry("400x400")
         self.resizable(False, False)

         ctk.set_appearance_mode("light")
         ctk.set_default_color_theme("blue")

         title_label = ctk.CTkLabel(self, text="Register Form", font=("Arial", 20, "bold"))
         title_label.pack(pady=20)

         username_label = ctk.CTkLabel(self, text="Username:", font=("Arial", 14))
         username_label.pack(pady=(10, 0))
         self.username_entry = ctk.CTkEntry(self, placeholder_text="Enter your username")
         self.username_entry.pack(pady=(0, 10), padx=20)

         email_label = ctk.CTkLabel(self, text="Email:", font=("Arial", 14))
         email_label.pack(pady=(10, 0))
         self.email_entry = ctk.CTkEntry(self, placeholder_text="Enter your email")
         self.email_entry.pack(pady=(0, 10), padx=20)

         password_label = ctk.CTkLabel(self, text="Password:", font=("Arial", 14))
         password_label.pack(pady=(10, 0))
         self.password_entry = ctk.CTkEntry(self, placeholder_text="Enter your password", show="*")
         self.password_entry.pack(pady=(0, 20), padx=20)

         register_button = ctk.CTkButton(
             self,
             text="Register",
             command=self.register_user,
             fg_color="#1f6aa5",
             hover_color="#144870",
             font=("Arial", 16)
         )
         register_button.pack(pady=20)

    def register_user(self):
         username = self.username_entry.get().strip()
         email = self.email_entry.get().strip()
         password = self.password_entry.get().strip()

         if not username or not email or not password:
             messagebox.showerror("Error", "All fields are required!")
             return

         db = Database()

         query = '''
             INSERT INTO users (username, email, password)
             VALUES (%s, %s, %s)
         '''

         try:
             db.cursor.execute(query, (username, email, password))  # Store plain text password
             db.connection.commit()
             messagebox.showinfo("Success", f"User '{username}' registered successfully!")

             # Clear input fields after successful registration
             for entry in [self.username_entry, self.email_entry, self.password_entry]:
                 entry.delete(0, 'end')

         except mysql.connector.IntegrityError:
             messagebox.showerror("Error", "Username or email already exists!")

         except Exception as e:
             messagebox.showerror("Error", str(e))

         finally:
             db.close()

# Run the application
if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
