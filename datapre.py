import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import sqlite3
from datetime import datetime
from cryptography.fernet import Fernet

encryption_key = Fernet.generate_key()

db_path = "/home/nasla/Documents/vs//data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    content TEXT,
                    date_created TEXT,
                    user_id INTEGER)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL)''')


cursor.execute('''CREATE TABLE IF NOT EXISTS prevented_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    date_prevented TEXT,
                    user_id INTEGER)''')
conn.commit()

def encrypt_content(content):
    fernet = Fernet(encryption_key)
    encrypted_content = fernet.encrypt(content.encode())
    return encrypted_content

def prevent_data_loss(file_path, user_id):
    print(f"Data loss prevention triggered for file: {file_path} by user_id: {user_id}")
    date_prevented = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(file_path, 'r') as file:
        content = file.read()
    
    encrypted_content = encrypt_content(content)
    
    with open(file_path, 'wb') as file:
        file.write(encrypted_content)
        
    file_name = os.path.basename(file_path)
    date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO files (name, content, date_created, user_id) VALUES (?, ?, ?, ?)',
                   (file_name, encrypted_content, date_created, user_id))
    conn.commit()
    
    cursor.execute('INSERT INTO prevented_files (file_name, date_prevented, user_id) VALUES (?, ?, ?)',
                   (os.path.basename(file_path), date_prevented, user_id))
    conn.commit()
    

    
def browse_file(user_id):
    file_path = filedialog.askopenfilename()
    if file_path:
        prevent_data_loss(file_path, user_id)

def show_help():
    help_message = "This is the Data Loss Prevention Tool. It helps you prevent data loss by checking for sensitive files.\n" \
                   "Click 'Browse' in the 'File' menu to select a file for data loss prevention.\n" \
                   "You can also open files to view their content using the 'Open' option in the 'File' menu."
    messagebox.showinfo("Help", help_message)

def show_about():
    about_message = "Data Loss Prevention Tool\nVersion 1.0\n\nCreated by Nasla"
    messagebox.showinfo("About", about_message)

def show_settings():
    print("Displaying settings.")

def exit_tool():
    if messagebox.askyesno("Exit", "Are you sure you want to exit the Data Loss Prevention Tool?"):
        conn.close()
        root.quit()

def create_new_file_and_save():
    new_file_dialog = tk.Toplevel(root)
    new_file_dialog.title("Create New File")
    new_file_content = tk.Text(new_file_dialog, wrap=tk.WORD, width=50, height=10)
    new_file_content.pack(padx=10, pady=10)

    def save_new_file():
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            content = new_file_content.get("1.0", tk.END)
            with open(file_path, "w") as new_file:
                new_file.write(content)

            file_name = os.path.basename(file_path)
            date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('INSERT INTO files (name, content, date_created) VALUES (?, ?, ?)', (file_name, content, date_created))
            conn.commit()

            new_file_dialog.destroy()
    save_button = tk.Button(new_file_dialog, text="Save", command=save_new_file)
    save_button.pack(pady=10)

def open_file_and_show_content():
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, "r") as opened_file:
            content = opened_file.read()

        content_window = tk.Toplevel(root)
        content_window.title(f"Content of {os.path.basename(file_path)}")
        content_text = tk.Text(content_window, wrap=tk.WORD, width=50, height=15)
        content_text.pack(padx=10, pady=10)
        content_text.insert(tk.END, content)
        content_text.config(state=tk.DISABLED) 
        file_name = os.path.basename(file_path)
        date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('INSERT INTO files (name, content, date_created) VALUES (?, ?, ?)', (file_name, content, date_created))
        conn.commit()
        
def add_user_to_database(username, password):
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()

def open_user_page(username, user_id):
    user_page = tk.Toplevel(root)
    user_page.title(f"Welcome, {username}")

    welcome_label = tk.Label(user_page, text=f"Welcome, {username}!", font=("Arial", 14, "bold"))
    welcome_label.pack(pady=10)
    create_new_file_button = tk.Button(user_page, text="Create New File", command=create_new_file_and_save)
    create_new_file_button.pack(pady=5)

    open_file_button = tk.Button(user_page, text="Open File", command=open_file_and_show_content)
    open_file_button.pack(pady=5)

    browse_file_button = tk.Button(user_page, text="Browse File for Data Prevention", command=lambda: browse_file(user_id))
    browse_file_button.pack(pady=5)

    files_prevented_label = tk.Label(user_page, text="Files Prevented from Data Loss:", font=("Arial", 12, "bold"))
    files_prevented_label.pack(pady=5)
    
    files_container = tk.Listbox(user_page, width=50, height=10)
    files_container.pack(pady=5)

    scrollbar = tk.Scrollbar(user_page, command=files_container.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    files_container.config(yscrollcommand=scrollbar.set)
    cursor.execute('SELECT * FROM prevented_files WHERE user_id=?', (user_id,))
    prevented_files = cursor.fetchall()
    for file_data in prevented_files:
        file_name = file_data[1]
        date_prevented = file_data[2]
        file_info = f"File: {file_name}, Date Prevented: {date_prevented}"
        files_container.insert(tk.END, file_info)
        
def login():
    def login_user():
        username = username_entry.get()
        password = password_entry.get()

        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()

        if user:
            messagebox.showinfo("Login", "Login successful!")
            user_id = user[0]  
            login_window.destroy()
            open_user_page(username, user_id)  
        else:
            messagebox.showerror("Login Error", "Invalid username or password")

    login_window = tk.Toplevel(root)
    login_window.title("Login")
    
    login_window_width = 300
    login_window_height = 200
    login_window.geometry(f"{login_window_width}x{login_window_height}")

    username_label = tk.Label(login_window, text="Username:")
    username_label.pack(pady=5)
    username_entry = tk.Entry(login_window)
    username_entry.pack(pady=5)

    password_label = tk.Label(login_window, text="Password:")
    password_label.pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(pady=5)

    login_button = tk.Button(login_window, text="Login", command=login_user)
    login_button.pack(pady=10)

def register():
    def register_user():
        username = new_username_entry.get()
        password = new_password_entry.get()

        if len(username) == 0 or len(password) == 0:
            messagebox.showerror("Registration Error", "Username and password cannot be empty")
            return

        cursor.execute('SELECT * FROM users WHERE username=?', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            messagebox.showerror("Registration Error", "Username already exists")
        else:
            add_user_to_database(username, password)
            messagebox.showinfo("Registration", "Registration successful!")
            register_window.destroy()

    register_window = tk.Toplevel(root)
    register_window.title("Register")
    
    register_window_width = 300
    register_window_height = 200
    register_window.geometry(f"{register_window_width}x{register_window_height}")

    new_username_label = tk.Label(register_window, text="New Username:")
    new_username_label.pack(pady=5)
    new_username_entry = tk.Entry(register_window)
    new_username_entry.pack(pady=5)

    new_password_label = tk.Label(register_window, text="New Password:")
    new_password_label.pack(pady=5)
    new_password_entry = tk.Entry(register_window, show="*")
    new_password_entry.pack(pady=5)

    register_button = tk.Button(register_window, text="Register", command=register_user)
    register_button.pack(pady=10)

def create_gui():
    global root
    root = tk.Tk()
    root.title("Data Loss Prevention Tool")
    window_width = 1500
    window_height = 450
    root.geometry(f"{window_width}x{window_height}")
    
    background_image = tk.PhotoImage(file=r"/home/nasla/Documents/vs/backgroung.png")
    
    canvas = tk.Canvas(root, width=1500, height=800)
    canvas.pack()
    canvas.create_image(0, 0, anchor=tk.NW, image=background_image)

    menubar = tk.Menu(root)
    root.config(menu=menubar)

    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)

    file_menu.add_command(label="New", command=create_new_file_and_save)  
    file_menu.add_command(label="Open", command=open_file_and_show_content)  

    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="Help", command=show_help) 
    help_menu.add_command(label="About", command=show_about)

    settings_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Settings", menu=settings_menu)
    settings_menu.add_command(label="Settings", command=show_settings)
    settings_menu.add_command(label="Exit", command=exit_tool)

    login_button = tk.Button(canvas, text="Login", command=login, width=10, height=2, font=("Arial", 10, "bold"))
    login_button.place(x=window_width-800, y=200)

    register_button = tk.Button(canvas, text="Register", command=register, width=10, height=2, font=("Arial", 10, "bold"))
    register_button.place(x=window_width-800, y=250)
    
    welcome_text = "Welcome to the Data Loss Prevention Tool!"
    welcome_x = 480  
    welcome_y = 10   
    welcome_font = ("Arial", 20, "bold")
    welcome_color = "white"
    
    canvas.create_text(welcome_x, welcome_y, text=welcome_text, font=welcome_font, fill=welcome_color, anchor=tk.NW)
    
    title_paragraph = "Data loss prevention (DLP) is a tool and processes that ensure the sensitive data is not lost, misused, or accessed by unauthorized users."
    title_x = 200  
    title_y = 80   
    title_font = ("Arial", 14)
    title_color = "white"
    
    canvas.create_text(title_x, title_y, text=title_paragraph, font=title_font, fill=title_color, anchor=tk.NW)
    
    new_line_text = "This tool helps you prevent data loss by checking for sensitive files and ensuring data security."
    new_line_x = 400  
    new_line_y = title_y + 30  
    new_line_font = ("Arial", 14)
    new_line_color = "white"

    canvas.create_text(new_line_x, new_line_y, text=new_line_text, font=new_line_font, fill=new_line_color, anchor=tk.NW)
    
    new_line_text = "All the users can keep their files here for preventing their sensitive data."
    new_line_x = 480  
    new_line_y = title_y + 60 
    new_line_font = ("Arial", 14)
    new_line_color = "white"

    canvas.create_text(new_line_x, new_line_y, text=new_line_text, font=new_line_font, fill=new_line_color, anchor=tk.NW)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
