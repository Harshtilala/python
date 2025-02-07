import customtkinter as ctk
from gui.login import RegisterWindow  # Import RegisterWindow from register.py
from gui.login import LoginWindow  # Import LoginWindow from login.py

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Welcome")
        self.geometry("400x300")
        self.resizable(False, False)

        # Set appearance and theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Title Label
        title_label = ctk.CTkLabel(self, text="Welcome to the App", font=("Arial", 20, "bold"))
        title_label.pack(pady=40)

        # Register Button
        register_button = ctk.CTkButton(
            self,
            text="Register",
            command=self.open_register_window,
            fg_color="#1f6aa5",
            hover_color="#144870",
            font=("Arial", 16)
        )
        register_button.pack(pady=10)

        # Login Button
        login_button = ctk.CTkButton(
            self,
            text="Login",
            command=self.open_login_window,
            fg_color="#2E8B57",
            hover_color="#3CB371",
            font=("Arial", 16)
        )
        login_button.pack(pady=10)

    def open_register_window(self):
        """Open the RegisterWindow."""
        register_window = RegisterWindow()  # Open RegisterWindow from register.py
        self.destroy()  # Close the MainWindow
        register_window.mainloop()  # Start the RegisterWindow's event loop

    def open_login_window(self):
        """Open the LoginWindow."""
        login_window = LoginWindow()  # Open LoginWindow from login.py
        self.destroy()  # Close the MainWindow
        login_window.mainloop()  # Start the LoginWindow's event loop


# Run the application
if __name__ == "__main__":
    app = MainWindow()  # Initialize MainWindow
    app.mainloop()  # Start the main loop for the application
