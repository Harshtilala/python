import customtkinter as ctk
from tkinter import scrolledtext, messagebox, Menu  # Import Menu from tkinter
import mysql.connector
from datetime import datetime
import threading
import time

class ChatDashboard(ctk.CTkToplevel):
    def __init__(self, current_user_id, current_username, login_window):
        super().__init__()
        
        self.current_user_id = current_user_id
        self.current_username = current_username
        self.login_window = login_window  # Store reference to the login window
        self.title("Chat Dashboard")
        self.geometry("800x600")

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

        # Login Another Account button
        login_another_button = ctk.CTkButton(self.navbar, text="Login Another Account", command=self.login_another_account, fg_color="#1f6aa5", hover_color="#144870")
        login_another_button.pack(side="right", padx=10, pady=10)

        # Frame for user list
        self.user_frame = ctk.CTkFrame(self, fg_color="#262626")
        self.user_frame.pack(side="left", fill="y", padx=(10, 0), pady=10)

        # User List Label
        user_label = ctk.CTkLabel(self.user_frame, text="Users", font=("Arial", 16), text_color="#ffffff")
        user_label.pack(pady=(10, 0))

        # Frame for refresh and search buttons
        button_frame = ctk.CTkFrame(self.user_frame, fg_color="#262626")
        button_frame.pack(pady=(10, 0))

        # Search User Entry
        self.search_entry = ctk.CTkEntry(button_frame, placeholder_text="Search user", fg_color="#333333", border_color="#1f6aa5")
        self.search_entry.pack(pady=(0, 5), padx=10)
        self.search_entry.bind("<Return>", self.search_user)

        # Frame for search and refresh buttons
        search_refresh_frame = ctk.CTkFrame(button_frame, fg_color="#262626")
        search_refresh_frame.pack()

        # Search User button
        search_button = ctk.CTkButton(search_refresh_frame, text="Search", command=self.search_user, fg_color="#1f6aa5", hover_color="#144870", width=10, height=10)
        search_button.pack(side="left", padx=5)

        # Refresh Users button
        refresh_button = ctk.CTkButton(search_refresh_frame, text="Refresh", command=self.load_users, fg_color="#1f6aa5", hover_color="#144870", width=10, height=10)
        refresh_button.pack(side="left", padx=5)

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

        # Bind right-click event to the chat display
        self.chat_display.bind("<Button-3>", self.show_context_menu)

        # Create a context menu
        self.context_menu = Menu(self, tearoff=0)  # Use tkinter.Menu
        self.context_menu.add_command(label="Delete", command=self.delete_message)

        # Variable to store the selected message
        self.selected_message_text = None

        # Message entry frame
        self.message_frame = ctk.CTkFrame(self.chat_frame, fg_color="#262626")
        self.message_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Message entry
        self.message_entry = ctk.CTkEntry(self.message_frame, placeholder_text="Type your message here...", fg_color="#333333", border_color="#1f6aa5")
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", self.send_message)

        # Send button
        self.send_button = ctk.CTkButton(self.message_frame, text="Send", command=self.send_message, fg_color="#1f6aa5", hover_color="#144870")
        self.send_button.pack(side="right")

        # Load users
        self.load_users()

        # Start a thread to refresh messages in real-time
        self.refresh_thread = threading.Thread(target=self.refresh_messages, daemon=True)
        self.refresh_thread.start()

        self.last_message_timestamp = None  # Track the timestamp of the last loaded message
        self.profile_frame = None  # Initialize profile_frame

    def load_users(self):
        try:
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='chat_app')
            cursor = conn.cursor()
            cursor.execute("SELECT id, username FROM users WHERE id != %s", (self.current_user_id,))
            users = cursor.fetchall()
            self.display_users(users)
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def display_users(self, users):
        for widget in self.user_buttons_frame.winfo_children():
            widget.destroy()
        for user in users:
            user_button = ctk.CTkButton(self.user_buttons_frame, text=user[1], command=lambda u=user: self.open_chat(u[0], u[1]), fg_color="#333333", hover_color="#1f6aa5")
            user_button.pack(fill="x", pady=5, padx=10)

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

    def show_context_menu(self, event):
        try:
            # Get the index of the clicked message
            self.selected_message_index = self.chat_display.index(f"@{event.x},{event.y}")

            # Get the line number from the index
            line_number = int(self.selected_message_index.split('.')[0])

            # Retrieve the message text
            selected_message = self.chat_display.get(f"{line_number}.0", f"{line_number}.end")

            if selected_message.strip():
                self.selected_message_text = selected_message.strip()  # Store selected message text
                self.context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"Error showing context menu: {e}")

    def delete_message(self):
        if not hasattr(self, 'selected_message_text') or not self.selected_message_text:
            messagebox.showerror("Error", "No message selected for deletion.")
            return

        try:
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='chat_app')
            cursor = conn.cursor()

            # Fetch message ID based on content and sender
            cursor.execute("""
                SELECT id FROM messages 
                WHERE message = %s AND from_user = %s AND to_user = %s
                ORDER BY timestamp DESC LIMIT 1
            """, (self.selected_message_text, self.current_user_id, self.selected_user_id))

            message_id = cursor.fetchone()

            if message_id:
                cursor.execute("DELETE FROM messages WHERE id = %s", (message_id[0],))
                conn.commit()
                messagebox.showinfo("Deleted", "Message successfully deleted.")
            else:
                messagebox.showerror("Error", "Message not found in the database.")

            cursor.close()
            conn.close()

            # Refresh the chat after deletion
            self.load_messages(self.selected_user_id)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def login_another_account(self):
        from login import LoginWindow
        login_window = LoginWindow()
        login_window.mainloop()

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
        self.login_window.deiconify()  # Show the login window

    def search_user(self, event=None):
        search_query = self.search_entry.get().strip()
        if not search_query:
            self.load_users()
            return

        try:
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='chat_app')
            cursor = conn.cursor()
            cursor.execute("SELECT id, username FROM users WHERE username LIKE %s AND id != %s", (f"%{search_query}%", self.current_user_id))
            users = cursor.fetchall()
            self.display_users(users)
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
