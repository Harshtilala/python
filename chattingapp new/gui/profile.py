import customtkinter as ctk
from tkinter import messagebox
import mysql.connector

class ProfileWindow(ctk.CTk):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.title("Profile")
        self.geometry("400x300")
        self.resizable(False, False)

        # Set appearance and theme
        ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

        # User Information Labels
        self.username_label = ctk.CTkLabel(self, text="Username:", font=("Arial", 14))
        self.username_label.pack(pady=(20, 5))

        self.username_value = ctk.CTkLabel(self, text=user_data['username'], font=("Arial", 14))
        self.username_value.pack(pady=(0, 10))

        self.user_id_label = ctk.CTkLabel(self, text="User ID:", font=("Arial", 14))
        self.user_id_label.pack(pady=(10, 5))

        self.user_id_value = ctk.CTkLabel(self, text=user_data['user_id'], font=("Arial", 14))
        self.user_id_value.pack(pady=(0, 10))

        self.email_label = ctk.CTkLabel(self, text="Email:", font=("Arial", 14))
        self.email_label.pack(pady=(10, 5))

        self.email_value = ctk.CTkLabel(self, text=user_data['email'], font=("Arial", 14))
        self.email_value.pack(pady=(0, 10))

        # Entry for updating email
        self.update_email_entry = ctk.CTkEntry(self, placeholder_text="Update your email")
        self.update_email_entry.pack(pady=(10, 5), padx=20)

        # Update Button
        update_button = ctk.CTkButton(
            self,
            text="Update",
            command=self.update_profile,
            fg_color="#1f6aa5",
            hover_color="#144870",
            font=("Arial", 16)
        )
        update_button.pack(pady=(20, 10))

    def update_profile(self):
        """Handles updating the user's profile."""
        
        new_email = self.update_email_entry.get().strip()
        
        if not new_email:
            messagebox.showerror("Error", "Email cannot be empty.")
            return

        # Update the user's email in the database
        try:
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='chat_app')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET email = %s WHERE username = %s", (new_email, self.username_value.cget("text")))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", f"Email updated to: {new_email}")
            self.email_value.config(text=new_email)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

# Example user data (this would typically come from your database)
user_data = {
    'username': 'JohnDoe',
    'email': 'john@example.com',
    'user_id': '12345'
}

# Run the application
if __name__ == "__main__": 
    app = ProfileWindow(user_data)
    app.mainloop()
