import customtkinter as ctk
from tkinter import scrolledtext, messagebox  # Remove Listbox import
import mysql.connector
from datetime import datetime
import threading
import time

class ChatDashboard(ctk.CTkToplevel):
    def __init__(self, current_user_id, current_username):
        super().__init__()
        
        self.current_user_id = current_user_id
        self.current_username = current_username
        self.title("Chat Dashboard")
        self.geometry("800x600")

        # Set appearance and theme
        ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

        # Set background color
        self.configure(bg="#1a1a1a")

        # Navigation bar
        self.navbar = ctk.CTkFrame(self, fg_color="#333333")
        self.navbar.pack(side="top", fill="x")

        profile_button = ctk.CTkButton(self.navbar, text="Profile", command=self.toggle_profile, fg_color="#1f6aa5", hover_color="#144870")
        profile_button.pack(side="right", padx=10, pady=10)

        # Logout button
        logout_button = ctk.CTkButton(self.navbar, text="Logout", command=self.logout_user, fg_color="#ff0000", hover_color="#cc0000")
        logout_button.pack(side="right", padx=10, pady=10)

        # Frame for user list
        self.user_frame = ctk.CTkFrame(self, fg_color="#262626")
        self.user_frame.pack(side="left", fill="y", padx=(10, 0), pady=10)

        # User List Label
        user_label = ctk.CTkLabel(self.user_frame, text="Users", font=("Arial", 16), text_color="#ffffff")
        user_label.pack(pady=(10, 0))

        # Frame for user buttons
        self.user_buttons_frame = ctk.CTkFrame(self.user_frame, fg_color="#262626")
        self.user_buttons_frame.pack(fill="both", expand=True)

        # Frame for chat
        self.chat_frame = ctk.CTkFrame(self, fg_color="#262626")
        self.chat_frame.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)

        # Opponent label
        self.opponent_label = ctk.CTkLabel(self.chat_frame, text="", font=("Arial", 16), text_color="#ffffff")
        self.opponent_label.pack(pady=(10, 0))

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, state='disabled', wrap='word', bg="#1a1a1a", fg="#ffffff")
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # Message entry frame
        self.message_frame = ctk.CTkFrame(self.chat_frame, fg_color="#262626")
        self.message_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Message entry
        self.message_entry = ctk.CTkEntry(self.message_frame, placeholder_text="Type your message here...", fg_color="#333333", border_color="#1f6aa5")
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", self.send_message)

        # Send button
        send_button = ctk.CTkButton(self.message_frame, text="Send", command=self.send_message, fg_color="#1f6aa5", hover_color="#144870")
        send_button.pack(side="right")

        # Load users
        self.load_users()

        # Start a thread to refresh messages in real-time
        self.refresh_thread = threading.Thread(target=self.refresh_messages, daemon=True)
        self.refresh_thread.start()

        self.last_message_timestamp = None  # Track the timestamp of the last loaded message
        self.profile_frame = None  # Add this line to initialize profile_frame

    def load_users(self):
        try:
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='chat_app')
            cursor = conn.cursor()
            cursor.execute("SELECT id, username FROM users WHERE id != %s", (self.current_user_id,))
            users = cursor.fetchall()
            for user in users:
                user_button = ctk.CTkButton(self.user_buttons_frame, text=user[1], command=lambda u=user: self.open_chat(u[0], u[1]), fg_color="#333333", hover_color="#1f6aa5")
                user_button.pack(fill="x", pady=5, padx=10)
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def open_chat(self, user_id, username):
        self.selected_user_id = user_id
        self.selected_username = username
        self.opponent_label.configure(text=username)  # Set the opponent username label
        self.chat_display.config(state='normal')
        self.chat_display.delete('1.0', 'end')
        self.chat_display.config(state='disabled')
        
        # Highlight the selected user button
        for widget in self.user_buttons_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == username:
                widget.configure(fg_color="#1f6aa5")
            else:
                widget.configure(fg_color="#333333")

        # Load messages for the selected user
        self.load_messages(self.selected_user_id)

    def load_messages(self, to_user_id):
        try:
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='chat_app')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT from_user, message, timestamp FROM messages 
                WHERE (from_user = %s AND to_user = %s) OR (from_user = %s AND to_user = %s)
                ORDER BY timestamp
            """, (self.current_user_id, to_user_id, to_user_id, self.current_user_id))
            messages = cursor.fetchall()
            self.chat_display.config(state='normal')
            self.chat_display.delete('1.0', 'end')  # Clear the chat display before loading messages
            for msg in messages:
                timestamp = msg[2].strftime("%H:%M")
                if msg[0] == self.current_user_id:
                    self.chat_display.insert('end', f"{msg[1]}\n", 'right')
                    self.chat_display.insert('end', f"{timestamp}\n", 'right_time')
                else:
                    self.chat_display.insert('end', f"{msg[1]}\n", 'left')
                    self.chat_display.insert('end', f"{timestamp}\n", 'left_time')
            self.chat_display.tag_configure('right', justify='right', foreground='#ffffff', font=('Arial', 12, 'bold'), lmargin1=50, lmargin2=50)
            self.chat_display.tag_configure('right_time', justify='right', foreground='#ffffff', font=('Arial', 8), lmargin1=50, lmargin2=50)
            self.chat_display.tag_configure('left', justify='left', foreground='#ffff00', font=('Arial', 12, 'bold'), lmargin1=10, lmargin2=10)
            self.chat_display.tag_configure('left_time', justify='left', foreground='#ffffff', font=('Arial', 8), lmargin1=10, lmargin2=10)
            self.chat_display.config(state='disabled')
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def send_message(self, event=None):
        if not hasattr(self, 'selected_user_id'):
            messagebox.showwarning("Warning", "Select a user to chat with.")
            return

        to_user_id = self.selected_user_id
        message = self.message_entry.get()
        
        if message:
            try:
                conn = mysql.connector.connect(user='root', password='', host='localhost', database='chat_app')
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO messages (from_user, to_user, message, timestamp) 
                    VALUES (%s, %s, %s, %s)
                """, (self.current_user_id, to_user_id, message, datetime.now()))
                conn.commit()
                cursor.close()
                conn.close()
                self.message_entry.delete(0, 'end')
                self.load_messages(to_user_id)
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")

    def refresh_messages(self):
        while True:
            if hasattr(self, 'selected_user_id') and self.chat_display.winfo_exists():
                self.load_messages(self.selected_user_id)
            time.sleep(1)

    def toggle_profile(self):
        """Toggles the profile frame visibility."""
        if self.profile_frame:
            self.profile_frame.destroy()
            self.profile_frame = None
        else:
            self.open_profile()

    def open_profile(self):
        """Opens the profile in a new window."""
        import profile  # Import the profile module
        user_data = self.fetch_user_data(self.current_user_id)
        
        if user_data:
            user_data['user_id'] = self.current_user_id  # Add user ID to user_data
            profile_window = profile.ProfileWindow(None, user_data)
            profile_window.mainloop()

    def close_profile(self):
        """Closes the profile frame."""
        if self.profile_frame:
            self.profile_frame.destroy()
            self.profile_frame = None

    def fetch_user_data(self, user_id):
        """Fetch user data from the database."""
        try:
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='chat_app')
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            return user_data
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            return None

    def get_username_by_id(self, user_id):
        """Fetch username by user ID from the database."""
        try:
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='chat_app')
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
            username = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return username
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            return "Unknown"

    def logout_user(self):
        """Logs out the user and returns to the login window."""
        self.destroy()
        from login import LoginWindow  # Import here to avoid circular dependency
        login_window = LoginWindow()
        login_window.mainloop()

# Example usage - This part is not needed when used as a module.
if __name__ == "__main__":
    app = ctk.CTk()  # This line is only for testing purposes; it should be removed when integrating.
    dashboard = ChatDashboard(current_user_id=1, current_username="current_user_name")
    app.mainloop()  # This line is only for testing purposes; it should be removed when integrating.
