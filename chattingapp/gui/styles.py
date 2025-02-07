import customtkinter as ctk
from tkinter import messagebox

# Define styles for widgets
FONT_LARGE = ("Helvetica", 18)
FONT_MEDIUM = ("Helvetica", 14)
FONT_SMALL = ("Helvetica", 12)

BUTTON_STYLE = {
    "fg_color": "#2E8B57",
    "hover_color": "#3CB371",
}

class ProfileWindow(ctk.CTk):
    def __init__(self, user_data):
        super().__init__()
        self.title("Profile")
        self.geometry("400x300")
        self.resizable(False, False)

        # Set appearance and theme
        ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

        # User Information Labels
        self.username_label = ctk.CTkLabel(self, text="Username:", font=FONT_MEDIUM)
        self.username_label.pack(pady=(20, 5))

        self.username_value = ctk.CTkLabel(self, text=user_data['username'], font=FONT_MEDIUM)
        self.username_value.pack(pady=(0, 10))

        self.email_label = ctk.CTkLabel(self, text="Email:", font=FONT_MEDIUM)
        self.email_label.pack(pady=(10, 5))

        self.email_value = ctk.CTkLabel(self, text=user_data['email'], font=FONT_MEDIUM)
        self.email_value.pack(pady=(0, 10))

        # Entry for updating email
        self.update_email_entry = ctk.CTkEntry(self, placeholder_text="Update your email")
        self.update_email_entry.pack(pady=(10, 5), padx=20)

        # Update Button with styles
        update_button = ctk.CTkButton(
            self,
            text="Update",
            command=self.update_profile,
            **BUTTON_STYLE,
            font=FONT_LARGE
        )
        update_button.pack(pady=(20, 10))

    def update_profile(self):
        """Handles updating the user's profile."""
        
        new_email = self.update_email_entry.get().strip()
        
        if not new_email:
            messagebox.showerror("Error", "Email cannot be empty.")
            return

        # Here you would typically update the user's email in the database.
        
        # For demonstration purposes, we will just show a success message.
        messagebox.showinfo("Success", f"Email updated to: {new_email}")
        
        # Optionally update the displayed email value
        self.email_value.config(text=new_email)

# Example user data (this would typically come from your database)
user_data = {
    'username': 'JohnDoe',
    'email': 'john@example.com'
}

# Run the application
if __name__ == "__main__":
    app = ProfileWindow(user_data)
    app.mainloop()
