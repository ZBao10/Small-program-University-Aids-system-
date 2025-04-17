from tkinter import *
from tkinter import messagebox, filedialog
import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Get the current file directory dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct absolute paths for images
FIGURE_IMAGE_PATH = os.path.join(BASE_DIR, "assets", "loginpage", "image_1.png")
HELP_IMAGE_PATH = os.path.join(BASE_DIR, "assets", "loginpage", "image_2.png")

# Define file paths
ADMIN_FILE_PATH = os.path.join(BASE_DIR, "admin.txt")
USER_FILE_PATH = os.path.join(BASE_DIR, "users.txt")
GUIDANCE_FILE_PATH = os.path.join(BASE_DIR, "guidance.txt")
HEADMIN_FILE_PATH = os.path.join(BASE_DIR, "headminister.txt")
AID_REQUESTS_FILE = os.path.join(BASE_DIR, "aid_requests.txt")

# Initialize dictionaries
admin_dict = {}
users_dict = {}
guidance_dict = {}
headmin_dict = {}

# Load admin data
def readadmin():
    try:
        with open(ADMIN_FILE_PATH, "r") as file:
            for line in file:
                username, password = line.strip().split(":")
                admin_dict[username] = password
    except FileNotFoundError:
        print(f"Warning: {ADMIN_FILE_PATH} not found.")

# Load user data
def readuser():
    line = None
    try:
        with open(USER_FILE_PATH, "r") as file:
            for line in file:
                parts = line.strip().split(":")
                if len(parts) < 4:
                    continue
                user_id, username, password, balance_and_contact = parts[:4]
                balance_parts = balance_and_contact.split("|")
                balance = float(balance_parts[0])
                address = balance_parts[1] if len(balance_parts) > 1 and balance_parts[1] != "-" else "Not Provided"
                phonenumber = balance_parts[2] if len(balance_parts) > 2 and balance_parts[2] != "-" else "Not Provided"
                users_dict[user_id] = {
                    "username": username,
                    "password": password,
                    "balance": balance,
                    "address": address,
                    "phonenumber": phonenumber
                }
    except FileNotFoundError:
        print(f"Warning: {USER_FILE_PATH} not found.")
    except ValueError as e:
        print(f"Error parsing line: {line}. Error: {e}")

# Load guidance data
def readguidance():
    """ Reads guidance user details from the file and loads them into guidance_dict correctly. """
    try:
        with open(GUIDANCE_FILE_PATH, "r") as file:
            for line in file:
                username, password, phonenumber, department = line.strip().split(":")
                guidance_dict[username] = {
                    "username": username,
                    "password": password,
                    "phonenumber": phonenumber,
                    "department": department
                }
    except FileNotFoundError:
        print(f"Warning: {GUIDANCE_FILE_PATH} not found.")

# Load head minister data
def readheadminister():
    try:
        with open(HEADMIN_FILE_PATH, "r") as file:
            for line in file:
                username, password = line.strip().split(":")
                headmin_dict[username] = password
    except FileNotFoundError:
        print(f"Warning: {HEADMIN_FILE_PATH} not found.")

# Load aid requests
def load_aid_requests():
    if os.path.exists(AID_REQUESTS_FILE):
        with open(AID_REQUESTS_FILE, "r") as file:
            content = file.read().strip()
            if content:
                try:
                    loaded_requests = json.loads(content)
                    return {req['request_id']: req for req in loaded_requests}
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    return {}
            else:
                return {}
    return {}

aid_requests = load_aid_requests()

# Save aid request
def save_aid_request(request_id, username, aid_type, description, documents):
    aid_requests[request_id] = {
        "username": username,
        "aid_type": aid_type,
        "description": description,
        "documents": documents,
        "status": "Pending"
    }
    with open(AID_REQUESTS_FILE, "w") as file:
        formatted_requests = []
        for req_id, details in aid_requests.items():
            formatted_requests.append({
                "request_id": req_id,
                "username": details["username"],
                "aid_type": details["aid_type"],
                "description": details["description"],
                "documents": details["documents"],
                "status": details["status"]
            })
        json.dump(formatted_requests, file, indent=4)
    print("Current aid request IDs:", list(aid_requests.keys()))

class UniversityAidApp:
    def __init__(self, root):
        self.root = root
        self.root.title("University Aid System")
        self.root.geometry("800x800")
        self.root.minsize(800, 800)
        self.root.config(bg="white")

        self.frames = {}
        self.username = None
        self.details_labels = {}  # For dynamic updates
        self.guidance_request_id_entry = None
        self.guidance_details_text = None
        self.guidance_doc_list = None

        # Create frames
        self.create_login_frame()
        self.create_registration_frame()
        
        self.create_admin_frame()
        self.create_admin_add_user_frame()
        self.create_admin_delete_user_frame()
        self.create_admin_update_user_details_frame()
        self.create_report_frame() 
        self.create_report_headminister_frame()

        self.create_select_user_FOR_details_frame()
        self.create_user_details_admin_frame()

        self.create_user_frame()
        self.create_user_apply_aid_frame()
        self.create_user_view_aid_frame()
        self.create_user_details_frame()
        self.create_update_user_details_frame()

        self.create_guidance_frame()
        self.create_guidance_view_aid_frame()
        self.create_select_user_for_details_guidance_frame()
        self.create_guidance_user_details_frame()  
        self.create_guidance_details_frame()
        self.create_update_guidance_details_frame()

        self.create_headminister_frame()
        self.create_select_user_for_details_headminister_frame()
        self.create_headminister_user_details_frame()

        self.create_headminister_manage_account_frame()
        self.create_headminister_add_user_frame()
        self.create_headminister_delete_user_frame()
        self.create_headminister_update_user_details_frame()

        self.create_manage_account_frame()

        self.show_frame("login")

    def show_frame(self, frame_name):
        self.current_frame = frame_name  # Save the current frame name.
        for frame in self.frames.values():
            frame.pack_forget()
        if frame_name == "user" and self.username in users_dict:
            student_name = users_dict[self.username]["username"]
            self.user_title_label.config(text=f"Welcome, {student_name} 🎓")
        self.frames[frame_name].pack(fill="both", expand=True)

    def create_login_frame(self):
        frame = Frame(self.root, bg="white")
        title_bar = Frame(frame, bg="darkblue", height=60)
        title_bar.pack(fill="x")
        Label(title_bar, text="University Aid System", font=("Comic Sans MS", 25, "bold"), bg="darkblue", fg="white").pack(pady=10)
        try:
            self.figure_photo = PhotoImage(file=FIGURE_IMAGE_PATH).subsample(1)
            Label(frame, image=self.figure_photo, bg="white").pack(pady=10)
        except Exception as e:
            print(f"Error loading figure image: {e}")
        form = Frame(frame, bg="white")
        form.pack(pady=10)
        Label(form, text="ID :", font=("Arial", 12, "bold"), bg="white").grid(row=0, column=0, padx=5, pady=(0,3), sticky="w")
        username_input = Entry(form, font=("Arial", 12), width=25, bg="lightgray")
        username_input.grid(row=1, column=0, padx=5, pady=3)
        Label(form, text="Password:", font=("Arial", 12, "bold"), bg="white").grid(row=2, column=0, padx=5, pady=(10,3), sticky="w")
        password_input = Entry(form, font=("Arial", 12), width=25, show="*", bg="lightgray")
        password_input.grid(row=3, column=0, padx=5, pady=3)
        login_notif = Label(frame, text="", font=("Arial", 12), bg="white", fg="red")
        login_notif.pack(pady=5)

        def login():
            username = username_input.get().strip()
            password = password_input.get().strip()
            print(f"Attempting login with ID: {username}, Password: {password}")
            if username in admin_dict and admin_dict[username] == password:
                self.username = username
                self.show_frame("admin")
                username_input.delete(0, END)
                password_input.delete(0, END)
                login_notif.config(text="", fg="green")
            elif username in users_dict and users_dict[username]["password"] == password:
                self.username = username
                self.show_frame("user")
                username_input.delete(0, END)
                password_input.delete(0, END)
                login_notif.config(text="", fg="green")
            elif username in guidance_dict and guidance_dict[username]["password"] == password:
                self.username = username
                self.show_frame("guidance")
                username_input.delete(0, END)
                password_input.delete(0, END)
                login_notif.config(text="", fg="green")
            elif username in headmin_dict and headmin_dict[username] == password:
                self.username = username
                self.show_frame("headminister")
                username_input.delete(0, END)
                password_input.delete(0, END)
                login_notif.config(text="", fg="green")
            else:
                login_notif.config(text="Invalid ID or password", fg="red")

        Button(frame, text="LOGIN", font=("Arial", 14, "bold"), bg="lightgray", fg="black", width=15, command=login).pack(pady=10)
        Button(frame, text="Register", font=("Arial", 8),bg="#0073e6", fg="black", width=8,command=lambda: self.show_frame("registration")).pack(pady=1)
        Label(frame, text="© Group 5. All Rights Reserved.", font=("Calibri", 10), bg="#f4f4f9", fg="#666").pack(side="bottom", pady=10)
        try:
            self.help_photo = PhotoImage(file=HELP_IMAGE_PATH)
            Label(frame, image=self.help_photo, bg="white").pack(side="bottom", pady=10)
        except Exception as e:
            print(f"Error loading help image: {e}")
        self.frames["login"] = frame
        
    def create_registration_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        # Title Bar
        title_bar = Frame(frame, bg="darkblue", height=60)
        title_bar.pack(fill="x")
        Label(title_bar, text="User Registration", font=("Comic Sans MS", 20, "bold"),
            bg="darkblue", fg="white").pack(pady=10)
        
        # Container for form fields
        container = Frame(frame, bg="white")
        container.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Username Field
        Label(container, text="Username:", font=("Calibri", 14), bg="white").pack(pady=5)
        self.reg_username_entry = Entry(container, font=("Calibri", 14), bg="#D3D3D3")
        self.reg_username_entry.pack(pady=5, fill="x")
        
        # Password Field
        Label(container, text="Password:", font=("Calibri", 14), bg="white").pack(pady=5)
        self.reg_password_entry = Entry(container, font=("Calibri", 14), show="*", bg="#D3D3D3")
        self.reg_password_entry.pack(pady=5, fill="x")
        
        # Confirm Password Field
        Label(container, text="Confirm Password:", font=("Calibri", 14), bg="white").pack(pady=5)
        self.reg_confirm_entry = Entry(container, font=("Calibri", 14), show="*", bg="#D3D3D3")
        self.reg_confirm_entry.pack(pady=5, fill="x")
        
        # Phone Number Field
        Label(container, text="Phone Number:", font=("Calibri", 14), bg="white").pack(pady=5)
        self.reg_phone_entry = Entry(container, font=("Calibri", 14), bg="#D3D3D3")
        self.reg_phone_entry.pack(pady=5, fill="x")
        
        # Address Field
        Label(container, text="Address:", font=("Calibri", 14), bg="white").pack(pady=5)
        self.reg_address_entry = Entry(container, font=("Calibri", 14), bg="#D3D3D3")
        self.reg_address_entry.pack(pady=5, fill="x")
        
        # Notification Label
        self.reg_notif_label = Label(container, text="", font=("Calibri", 12), bg="white", fg="red")
        self.reg_notif_label.pack(pady=10)
        
        # Helper function to clear all registration entries
        def clear_registration_entries():
            self.reg_username_entry.delete(0, END)
            self.reg_password_entry.delete(0, END)
            self.reg_confirm_entry.delete(0, END)
            self.reg_phone_entry.delete(0, END)
            self.reg_address_entry.delete(0, END)
        
        def register_user():
            username = self.reg_username_entry.get().strip()
            password = self.reg_password_entry.get().strip()
            confirm_password = self.reg_confirm_entry.get().strip()
            phone = self.reg_phone_entry.get().strip() or "Not Provided"
            address = self.reg_address_entry.get().strip() or "Not Provided"
            
            if not username or not password or not confirm_password:
                self.reg_notif_label.config(text="Please fill in all required fields.")
                return
            if password != confirm_password:
                self.reg_notif_label.config(text="Passwords do not match.")
                return
            
            # Check if the username already exists in users_dict
            for uid, user in users_dict.items():
                if user.get("username") == username:
                    self.reg_notif_label.config(text="Username already taken. Choose another.")
                    return
            
            # Generate a new user id (for example, U0001, U0002, etc.)
            new_user_id = "A" + format(len(users_dict) + 1)
            
            # Add the new user to the dictionary
            users_dict[new_user_id] = {
                "username": username,
                "password": password,
                "balance": 0,
                "address": address,
                "phonenumber": phone
            }
            
            # Append the new user record to the user file
            with open(USER_FILE_PATH, "a") as file:
                file.write(f"{new_user_id}:{username}:{password}:0.0|{address}|{phone}\n")
            
            self.reg_notif_label.config(text="Registration successful! Redirecting to login...", fg="green")
            clear_registration_entries()
            self.refresh_frames()
            self.frames["admin_delete_user"].destroy()
            self.create_admin_delete_user_frame()
            self.frames["headminister_delete_user"].destroy()
            self.create_headminister_delete_user_frame()
            frame.after(2000, lambda: self.show_frame("login"))
            self.reg_notif_label.after(2000, lambda: self.reg_notif_label.config(text="", fg="red"))


            self.frames["headminister"].destroy()
            self.frames["check_user_details_headminister"].destroy()
            self.frames["user_details_headminister"].destroy()
            self.create_headminister_frame()
            self.create_select_user_for_details_headminister_frame()
            self.create_headminister_user_details_frame()
        
        Button(container, text="Register", font=("Calibri", 14), bg="#0073e6", fg="white",
            command=register_user).pack(pady=10)
        # The "Back to Login" button now clears all entries before showing the login frame.
        Button(container, text="Back to Login", font=("Calibri", 14), bg="#e60000", fg="white",
            command=lambda: [clear_registration_entries(), self.show_frame("login")]).pack(pady=5)
        
        self.frames["registration"] = frame

    def refresh_frames(self):
        frames_to_refresh = [
            "check_user_details",  
            "check_user_details_guidance", 
            "check_user_details_headminister",
            "user_details_admin",
            "user_details_guidance",
            "user_details_headminister",
            "update_user_details",
            "update_user_details_admin",
            "update_user_details_headminister",
            "manage_account",
            "headminister_manage_account",
        ]
        for frame_name in frames_to_refresh:
            if frame_name in self.frames:
                self.frames[frame_name].destroy()
        self.create_user_apply_aid_frame()
        self.create_user_view_aid_frame()
        self.create_guidance_view_aid_frame()
        self.create_select_user_FOR_details_frame()
        self.create_select_user_for_details_headminister_frame()
        self.create_select_user_for_details_guidance_frame()
        self.create_user_details_frame()
        self.create_user_details_admin_frame()
        self.create_guidance_user_details_frame()  
        self.create_update_user_details_frame()
        self.create_admin_update_user_details_frame()
        self.create_headminister_update_user_details_frame()
        self.create_manage_account_frame()
        self.create_headminister_manage_account_frame()

    # ADMIN PART
    def create_admin_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        title_bar = Frame(frame, bg="darkblue", height=60)
        title_bar.pack(fill="x")
        Label(title_bar, text="🛠 Admin Dashboard", font=("Comic Sans MS", 20, "bold"), bg="darkblue", fg="white", pady=10).pack(fill="x")

        
        Button(frame, text="👥 User Details", font=("Calibri", 14), bg="#0073e6", fg="white", width=20, command=lambda: self.show_frame("check_user_details")).pack(pady=10)
        Button(frame, text="🔧 Manage Account", font=("Calibri", 14), bg="#0073e6", fg="white", width=20, command=lambda: self.show_frame("manage_account")).pack(pady=10)
        # Use lambda to delay execution of show_frame("report")
        Button(frame, text="📊 Report List", font=("Calibri", 14), bg="#0073e6", fg="white", width=20, command=lambda: self.show_frame("report")).pack(pady=10)

        def logout():
            if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
                self.show_frame("login")
        Button(frame, text="🚪 Logout", font=("Calibri", 14), bg="#e60000", fg="white", width=20, command=logout).pack(pady=20)
        self.frames["admin"] = frame

    def create_manage_account_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        title_bar = Frame(frame, bg="darkblue", height=60)
        title_bar.pack(fill="x")
        Label(title_bar, text="Manage User Accounts", font=("Comic Sans MS", 20, "bold"), bg="darkblue", fg="white").pack(pady=10)

        Button(frame, text="Add User", font=("Calibri", 14), bg="#0073e6", fg="white", width=20, command=lambda: self.show_frame("admin_add_user")).pack(pady=10)
        Button(frame, text="🗑 Delete User", font=("Calibri", 14), bg="#e60000", fg="white", width=20, command=lambda: self.show_frame("admin_delete_user")).pack(pady=10)
        Button(frame, text="Back", font=("Calibri", 14), bg="#e60000", fg="white", command=lambda: self.show_frame("admin")).pack(pady=10)
        self.frames["manage_account"] = frame

    def create_admin_add_user_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        title_bar = Frame(frame, bg="darkblue", height=60)
        title_bar.pack(fill="x")
        Label(title_bar, text="+ Add User", font=("Comic Sans MS", 20, "bold"), bg="darkblue", fg="white").pack(pady=10)

        Label(frame, text="Add New User", font=("Helvetica", 18, "bold"), bg="#f4f4f9", fg="#333").pack(pady=10)
        Label(frame, text="New User ID:", font=("Calibri", 14), bg="#f4f4f9").pack(pady=5)
        new_user_id_input = Entry(frame, font=("Calibri", 14))
        new_user_id_input.pack(pady=5)
        Label(frame, text="New User Username:", font=("Calibri", 14), bg="#f4f4f9").pack(pady=5)
        new_username_input = Entry(frame, font=("Calibri", 14))
        new_username_input.pack(pady=5)
        Label(frame, text="New User Password:", font=("Calibri", 14), bg="#f4f4f9").pack(pady=5)
        new_password_input = Entry(frame, font=("Calibri", 14), show="*")
        new_password_input.pack(pady=5)
        add_notif = Label(frame, text="", font=("Calibri", 12), bg="#f4f4f9", fg="red")
        add_notif.pack(pady=10)

        def save_user():
            user_id = new_user_id_input.get().strip()
            newuser_username = new_username_input.get().strip()
            newuser_password = new_password_input.get().strip()
            if user_id == "" or newuser_username == "" or newuser_password == "":
                add_notif.config(text="Please fill in all fields.", fg="red")
            elif user_id in users_dict:
                add_notif.config(text="User ID already exists. Please choose a different ID.", fg="red")
            else:
                users_dict[user_id] = {
                    "username": newuser_username,
                    "password": newuser_password,
                    "balance": 0,
                    "address": "Not Provided",
                    "phonenumber": "Not Provided"
                }
                with open(USER_FILE_PATH, 'a') as file:
                    file.write(f"{user_id}:{newuser_username}:{newuser_password}:0.0|Not Provided|Not Provided\n")
                add_notif.config(text="User added successfully!", fg="green")
                frame.after(3000, lambda: add_notif.config(text=""))
                self.refresh_frames()
                self.frames["admin_delete_user"].destroy()
                self.create_admin_delete_user_frame()
                self.frames["headminister_delete_user"].destroy()
                self.create_headminister_delete_user_frame()
                new_user_id_input.delete(0, END)
                new_username_input.delete(0, END)
                new_password_input.delete(0, END)

        Button(frame, text="Save", font=("Calibri", 14), bg="#0073e6", fg="white", command=save_user).pack(pady=10)
        Button(frame, text="Back", font=("Calibri", 14), bg="#e60000", fg="white", command=lambda: self.show_frame("admin")).pack(pady=5)
        self.frames["admin_add_user"] = frame

    def create_admin_delete_user_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        title_bar = Frame(frame, bg="darkblue", height=60)
        title_bar.pack(fill="x")
        Label(title_bar, text="Search Users to Delete", font=("Comic Sans MS", 20, "bold"), bg="darkblue", fg="white").pack(pady=10)

        name_entry = Entry(frame, font=("Calibri", 14))
        name_entry.pack(pady=10)
        name_entry.focus()
        name_list = Listbox(frame, width=50)
        name_list.pack(pady=10)
        delete_notif = Label(frame, text="", font=("Calibri", 12), bg="#f4f4f9", fg="red")
        delete_notif.pack(pady=10)

        def update(data=None):
            name_list.delete(0, END)
            if data is None:
                data = list(users_dict.keys())
            for item in data:
                name_list.insert(END, item)

        def fillblank(event):
            name_entry.delete(0, END)
            name_entry.insert(0, name_list.get(ACTIVE))

        def check(event):
            typed = name_entry.get()
            if typed == "":
                data = list(users_dict.keys())
            else:
                data = [item for item in users_dict.keys() if typed.lower() in item.lower()]
            update(data)

        def delete_user():
            selected_user = name_list.get(ACTIVE)
            if not selected_user:
                delete_notif.config(text="No user selected!", fg="red")
                return
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {selected_user}? This action cannot be undone.")
            if not confirm:
                return
            if selected_user in users_dict:
                del users_dict[selected_user]
                with open(USER_FILE_PATH, "w") as file:
                    for user_id, user in users_dict.items():
                        file.write(f"{user_id}:{user.get('username', 'N/A')}:{user.get('password', 'N/A')}:{user.get('balance', 'Not Provided')}|{user.get('address', 'Not Provided')}|{user.get('phonenumber', 'Not Provided')}\n")
                delete_notif.config(text="User deleted successfully!", fg="green")
                frame.after(3000, lambda: delete_notif.config(text=""))
                update()
                self.refresh_frames()
                self.frames["headminister_delete_user"].destroy()
                self.create_headminister_delete_user_frame()
            else:
                delete_notif.config(text="User not found!", fg="red")

        Button(frame, text="Delete", font=("Calibri", 14), bg="#e60000", fg="white", command=delete_user).pack(pady=10)
        Button(frame, text="Back", font=("Calibri", 14), bg="#0073e6", fg="white", command=lambda: self.show_frame("admin")).pack(pady=5)
        name_list.bind("<<ListboxSelect>>", fillblank)
        name_entry.bind("<KeyRelease>", check)
        update()
        self.frames["admin_delete_user"] = frame

    def create_user_details_admin_frame(self):
        frame = Frame(self.root, bg="white")
        header = Frame(frame, bg="#141885", height=80)
        header.pack(fill="x")
        Label(header, text="User's detail", font=("Helvetica", 22, "bold"), bg="#141885", fg="white").pack(pady=20)
        container = Frame(frame, bg="white")
        container.pack(pady=20, padx=40, fill="both", expand=True)
        self.admin_details_labels = {}
        self.admin_details_labels["username"] = Label(container, text="Username: ", font=("Calibri", 14, "bold"),
                                                      bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=2)
        self.admin_details_labels["username"].pack(pady=10, padx=10, fill="x")
        self.admin_details_labels["password"] = Label(container, text="Password: ", font=("Calibri", 14, "bold"),
                                                      bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=2)
        self.admin_details_labels["password"].pack(pady=10, padx=10, fill="x")
        row1 = Frame(container, bg="white")
        row1.pack(pady=5, padx=10, fill="x")
        self.admin_details_labels["balance"] = Label(row1, text="Balance: ", font=("Calibri", 14, "bold"),
                                                     bg="#D3D3D3", fg="black", anchor="w", padx=10, width=25, height=4)
        self.admin_details_labels["balance"].pack(side="left", padx=5, expand=True, fill="both")
        self.admin_details_labels["phonenumber"] = Label(row1, text="Telephone number:", font=("Calibri", 14, "bold"),
                                                         bg="#D3D3D3", fg="black", anchor="w", padx=10, width=25, height=4)
        self.admin_details_labels["phonenumber"].pack(side="right", padx=5, expand=True, fill="both")
        self.admin_details_labels["address"] = Label(container, text="Address: ", font=("Calibri", 14, "bold"),
                                                     bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=4)
        self.admin_details_labels["address"].pack(pady=10, padx=10, fill="x")
        Button(container, text="🔙 Back", font=("Calibri", 14), bg="#e60000", fg="white", width=20,
               command=lambda: self.show_frame("check_user_details")).pack(pady=20)
        Button(container, text="✏ Update User", font=("Calibri", 14), bg="#0073e6", fg="white", width=20, 
                command=lambda: self.show_frame("update_user_details_admin")).pack(pady=10)
        self.frames["user_details_admin"] = frame

    def show_user_details_adminVersion(self, user_id):
        if user_id in users_dict:
            self.selected_user_id_admin = user_id
            user = users_dict[user_id]
            self.admin_details_labels["username"].config(text=f"Username: {user.get('username', 'N/A')}")
            self.admin_details_labels["password"].config(text=f"Password: {user.get('password', 'N/A')}")
            self.admin_details_labels["balance"].config(text=f"Balance: RM {user.get('balance', 'Not Provided')}")
            self.admin_details_labels["phonenumber"].config(text=f"Telephone number:\n{user.get('phonenumber', 'Not Provided')}")
            self.admin_details_labels["address"].config(text=f"Address: {user.get('address', 'Not Provided')}")
            self.show_frame("user_details_admin")
        else:
            messagebox.showwarning("Error", "User details not found!")

    def create_select_user_FOR_details_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        title_bar = Frame(frame, bg="darkblue", height=60)
        title_bar.pack(fill="x")
        Label(title_bar, text="Search Users", font=("Comic Sans MS", 20, "bold"), bg="darkblue", fg="white").pack(pady=10)

        name_entry = Entry(frame, font=("Calibri", 14))
        name_entry.pack(pady=10)
        name_entry.focus()
        name_list = Listbox(frame, width=50)
        name_list.pack(pady=10)

        def update(data=None):
            name_list.delete(0, END)
            for item in (data or users_dict.keys()):
                name_list.insert(END, item)

        def fillblank(event):
            name_entry.delete(0, END)
            name_entry.insert(0, name_list.get(ACTIVE))

        def check(event):
            typed = name_entry.get().strip().lower()
            update([user_id for user_id in users_dict if typed in user_id.lower()])

        def view_user_details():
            selected_user = name_list.get(ACTIVE)
            if selected_user in users_dict:
                self.show_user_details_adminVersion(selected_user)  
            else:
                messagebox.showwarning("Error", "No user selected. Please select a user from the list.")

        Button(frame, text="View Details", font=("Calibri", 14), bg="#0073e6", fg="white", command=view_user_details).pack(pady=10)
        Button(frame, text="Back", font=("Calibri", 14), bg="#e60000", fg="white", command=lambda: self.show_frame("admin")).pack(pady=5)
        name_list.bind("<<ListboxSelect>>", fillblank)
        name_entry.bind("<KeyRelease>", check)
        update()
        self.frames["check_user_details"] = frame

    def create_admin_update_user_details_frame(self):
        frame = Frame(self.root, bg="white")
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, text="Update User's Details", font=("Comic Sans MS", 20, "bold"), bg="#141885", fg="white").pack(pady=20)

        container = Frame(frame, bg="white")
        container.pack(pady=20, padx=40, fill="both", expand=True)
        self.admin_update_entries = {}

        def create_update_entry(label_text, current_value):
            field_frame = Frame(container, bg="white")
            field_frame.pack(fill="x", pady=10)
            label = Label(field_frame, text=label_text, font=("Calibri", 14, "bold"),
                          bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=2)
            label.pack(fill="x")
            entry = Entry(field_frame, font=("Calibri", 14), width=50, bd=0, bg="#D3D3D3")
            entry.pack(fill="x", pady=5)
            entry.insert(0, current_value)
            return entry

        self.admin_update_entries["username"] = create_update_entry("Username:", "")
        self.admin_update_entries["password"] = create_update_entry("Password:", "")
        self.admin_update_entries["phonenumber"] = create_update_entry("Telephone number:", "")
        self.admin_update_entries["address"] = create_update_entry("Address:", "")

        def clear_entries():
            for entry in self.admin_update_entries.values():
                entry.delete(0, END)

        def save_and_return():
            if not hasattr(self, 'selected_user_id_admin') or self.selected_user_id_admin not in users_dict:
                messagebox.showwarning("Error", "No valid user selected!")
                return
            user_id = self.selected_user_id_admin
            username = self.admin_update_entries["username"].get().strip()
            password = self.admin_update_entries["password"].get().strip()
            phone = self.admin_update_entries["phonenumber"].get().strip() or "Not Provided"
            address = self.admin_update_entries["address"].get().strip() or "Not Provided"
            if not username or not password:
                messagebox.showwarning("Error", "Username and Password must be filled!")
                return
            users_dict[user_id] = {
                "username": username,
                "password": password,
                "balance": users_dict[user_id]["balance"],
                "address": address,
                "phonenumber": phone
            }
            with open(USER_FILE_PATH, "w") as file:
                for u_id, user in users_dict.items():
                    file.write(f"{u_id}:{user.get('username', 'N/A')}:{user.get('password', 'N/A')}:{user.get('balance', 'Not Provided')}|{user.get('address', 'Not Provided')}|{user.get('phonenumber', 'Not Provided')}\n")
            messagebox.showinfo("Success", "User details updated successfully!")
            clear_entries()
            self.show_frame("user_details_admin")

        def back_and_clear():
            clear_entries()
            self.show_frame("user_details_admin")

        button_frame = Frame(container, bg="white")
        button_frame.pack(pady=20)
        Button(button_frame, text="🔙 Back", font=("Calibri", 14), bg="#e60000", fg="white", width=20,
               command=back_and_clear).pack(pady=5)
        Button(button_frame, text="Save & Return", font=("Calibri", 14), bg="#0073e6", fg="white", width=20,
               command=save_and_return).pack(pady=5)
        self.frames["update_user_details_admin"] = frame

    # --------------------- REPORT FRAME ---------------------
    def create_report_frame(self, show=True):
        # Create a new Frame for the report
        frame = Frame(self.root, bg="#f4f4f9")
        frame.pack(fill="both", expand=True)

        # Title Bar: Title for the report
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, 
            text="University Aid Requests Report", 
            font=("Comic Sans MS", 20, "bold"), 
            bg="#141885", 
            fg="white").pack(pady=20)

        # Create a canvas with a vertical scrollbar to hold the scrollable content
        canvas_frame = Frame(frame, bg="#f4f4f9")
        canvas_frame.pack(fill="both", expand=True)
        canvas = Canvas(canvas_frame, bg="#f4f4f9", highlightthickness=0)
        scrollbar = Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg="#f4f4f9")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Summary Section: Totals for aid requests
        summary_frame = Frame(scrollable_frame, bg="#f4f4f9", padx=10, pady=10)
        summary_frame.pack(fill="x", pady=5)
        total_requests = len(aid_requests)
        accepted = sum(1 for req in aid_requests.values() if req["status"] == "Accepted")
        declined = sum(1 for req in aid_requests.values() if req["status"] == "Declined")
        pending = sum(1 for req in aid_requests.values() if req["status"] == "Pending")
        summary_text = (f"Total Aid Requests: {total_requests}    |    Accepted: {accepted}    |    "
                        f"Declined: {declined}    |    Pending: {pending}")
        summary_label = Label(summary_frame, text=summary_text, font=("Calibri", 12, "bold"), 
                            bg="#f4f4f9", fg="#333")
        summary_label.pack()

        # Create a form-like record for each aid request
        for req_id, details in aid_requests.items():
            record_frame = Frame(scrollable_frame, bg="white", bd=2, relief="groove", padx=10, pady=10)
            record_frame.pack(fill="x", padx=10, pady=5)
            Label(record_frame, text="Request ID:", font=("Calibri", 12, "bold"), bg="white") \
                .grid(row=0, column=0, sticky="w", padx=5, pady=2)
            Label(record_frame, text=req_id, font=("Calibri", 12), bg="white") \
                .grid(row=0, column=1, sticky="w", padx=5, pady=2)
            Label(record_frame, text="Username:", font=("Calibri", 12, "bold"), bg="white") \
                .grid(row=1, column=0, sticky="w", padx=5, pady=2)
            Label(record_frame, text=details['username'], font=("Calibri", 12), bg="white") \
                .grid(row=1, column=1, sticky="w", padx=5, pady=2)
            Label(record_frame, text="Aid Type:", font=("Calibri", 12, "bold"), bg="white") \
                .grid(row=2, column=0, sticky="w", padx=5, pady=2)
            Label(record_frame, text=details['aid_type'], font=("Calibri", 12), bg="white") \
                .grid(row=2, column=1, sticky="w", padx=5, pady=2)
            Label(record_frame, text="Status:", font=("Calibri", 12, "bold"), bg="white") \
                .grid(row=3, column=0, sticky="w", padx=5, pady=2)
            Label(record_frame, text=details['status'], font=("Calibri", 12), bg="white") \
                .grid(row=3, column=1, sticky="w", padx=5, pady=2)
            Label(record_frame, text="Description:", font=("Calibri", 12, "bold"), bg="white") \
                .grid(row=4, column=0, sticky="nw", padx=5, pady=2)
            Label(record_frame, text=details['description'], font=("Calibri", 12), bg="white", 
                wraplength=500, justify="left") \
                .grid(row=4, column=1, sticky="w", padx=5, pady=2)
            Label(record_frame, text="Documents:", font=("Calibri", 12, "bold"), bg="white") \
                .grid(row=5, column=0, sticky="w", padx=5, pady=2)
            documents_text = ", ".join(details['documents']) if details['documents'] else "None"
            Label(record_frame, text=documents_text, font=("Calibri", 12), bg="white", 
                wraplength=500, justify="left") \
                .grid(row=5, column=1, sticky="w", padx=5, pady=2)

        # Footer: Create a frame at the bottom to hold the buttons vertically
        footer_frame = Frame(frame, bg="#f4f4f9", padx=10, pady=10)
        footer_frame.pack(side="bottom", fill="x", pady=10)

        def save_report():
            report_text = self.generate_report_text()
            file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                    filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
            if file_path:
                try:
                    with open(file_path, "w") as file:
                        file.write(report_text)
                    messagebox.showinfo("Report Saved", f"Report successfully saved to:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save report: {e}")

        # Stack the buttons vertically
        back_button = Button(footer_frame, text="Back", font=("Calibri", 12, "bold"), width=15,bg="#e60000", fg="white", command=lambda: self.show_frame("admin"))
        back_button.pack(pady=5)

        pdf_button = Button(footer_frame, text="Save as PDF", font=("Calibri", 12, "bold"), width=15,bg="#0073e6", fg="white", 
            command=lambda: self.save_report_as_pdf(self.generate_report_text()))
        pdf_button.pack(pady=5)
        
        save_text_button = Button(footer_frame, text="Save Report", font=("Calibri", 12, "bold"), width=15,bg="#0073e6", fg="white", command=save_report)
        save_text_button.pack(pady=5)

        self.frames["report"] = frame
        if show:
            self.show_frame("report")

    def generate_report_text(self):
        report_text = "=== University Aid Requests Report ===\n\n"
        total_requests = len(aid_requests)
        accepted = sum(1 for req in aid_requests.values() if req["status"] == "Accepted")
        declined = sum(1 for req in aid_requests.values() if req["status"] == "Declined")
        pending = sum(1 for req in aid_requests.values() if req["status"] == "Pending")
        report_text += f"Total Aid Requests: {total_requests}\n"
        report_text += f"Accepted: {accepted}\n"
        report_text += f"Declined: {declined}\n"
        report_text += f"Pending: {pending}\n\n"
        report_text += "=" * 50 + "\n\n"
        for req_id, details in aid_requests.items():
            report_text += f"Request ID: {req_id}\n"
            report_text += f"Username: {details['username']}\n"
            report_text += f"Aid Type: {details['aid_type']}\n"
            report_text += f"Status: {details['status']}\n"
            report_text += f"Description: {details['description']}\n"
            if details['documents']:
                report_text += f"Documents: {', '.join(details['documents'])}\n"
            else:
                report_text += "Documents: None\n"
            report_text += "-" * 50 + "\n"
        return report_text

    def save_report_as_pdf(self, report_text):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")])
        if file_path:
            try:
                c = canvas.Canvas(file_path, pagesize=letter)
                width, height = letter
                x_margin = 50
                y = height - 50
                line_height = 15
                for line in report_text.splitlines():
                    if y < 50:
                        c.showPage()
                        y = height - 50
                    c.drawString(x_margin, y, line)
                    y -= line_height
                c.save()
                messagebox.showinfo("Report Saved", f"Report successfully saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save PDF report: {e}")

    def create_report_headminister_frame(self, show=True):
        frame = Frame(self.root, bg="#f4f4f9")
        frame.pack(fill="both", expand=True)

        # Title Bar (Top)
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, text="University Aid Requests Report", 
            font=("Comic Sans MS", 20, "bold"), bg="#141885", fg="white")\
            .pack(pady=20)

        # Scrollable Content Area (Middle)
        canvas_frame = Frame(frame, bg="#f4f4f9")
        canvas_frame.pack(fill="both", expand=True)
        canvas_obj = Canvas(canvas_frame, bg="#f4f4f9", highlightthickness=0)
        scrollbar = Scrollbar(canvas_frame, orient="vertical", command=canvas_obj.yview)
        scrollable_frame = Frame(canvas_obj, bg="#f4f4f9")
        scrollable_frame.bind("<Configure>", lambda e: canvas_obj.configure(scrollregion=canvas_obj.bbox("all")))
        canvas_obj.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_obj.configure(yscrollcommand=scrollbar.set)
        canvas_obj.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Summary Section: Display overall statistics of aid requests
        summary_frame = Frame(scrollable_frame, bg="#f4f4f9", padx=10, pady=10)
        summary_frame.pack(fill="x", pady=5)
        total_requests = len(aid_requests)
        accepted = sum(1 for req in aid_requests.values() if req["status"] == "Accepted")
        declined = sum(1 for req in aid_requests.values() if req["status"] == "Declined")
        pending = sum(1 for req in aid_requests.values() if req["status"] == "Pending")
        summary_text = (f"Total Aid Requests: {total_requests} | Accepted: {accepted} | "
                        f"Declined: {declined} | Pending: {pending}")
        Label(summary_frame, text=summary_text, font=("Calibri", 12, "bold"), 
            bg="#f4f4f9", fg="#333").pack()

        # Display each aid request record
        for req_id, details in aid_requests.items():
            record_frame = Frame(scrollable_frame, bg="white", bd=2, relief="groove", padx=10, pady=10)
            record_frame.pack(fill="x", padx=10, pady=5)
            Label(record_frame, text="Request ID:", font=("Calibri", 12, "bold"), bg="white")\
                .grid(row=0, column=0, sticky="w", padx=5, pady=2)
            Label(record_frame, text=req_id, font=("Calibri", 12), bg="white")\
                .grid(row=0, column=1, sticky="w", padx=5, pady=2)
            Label(record_frame, text="Username:", font=("Calibri", 12, "bold"), bg="white")\
                .grid(row=1, column=0, sticky="w", padx=5, pady=2)
            Label(record_frame, text=details['username'], font=("Calibri", 12), bg="white")\
                .grid(row=1, column=1, sticky="w", padx=5, pady=2)
            Label(record_frame, text="Aid Type:", font=("Calibri", 12, "bold"), bg="white")\
                .grid(row=2, column=0, sticky="w", padx=5, pady=2)
            Label(record_frame, text=details['aid_type'], font=("Calibri", 12), bg="white")\
                .grid(row=2, column=1, sticky="w", padx=5, pady=2)
            Label(record_frame, text="Status:", font=("Calibri", 12, "bold"), bg="white")\
                .grid(row=3, column=0, sticky="w", padx=5, pady=2)
            Label(record_frame, text=details['status'], font=("Calibri", 12), bg="white")\
                .grid(row=3, column=1, sticky="w", padx=5, pady=2)
            Label(record_frame, text="Description:", font=("Calibri", 12, "bold"), bg="white")\
                .grid(row=4, column=0, sticky="nw", padx=5, pady=2)
            Label(record_frame, text=details['description'], font=("Calibri", 12), bg="white",
                wraplength=500, justify="left")\
                .grid(row=4, column=1, sticky="w", padx=5, pady=2)
            Label(record_frame, text="Documents:", font=("Calibri", 12, "bold"), bg="white")\
                .grid(row=5, column=0, sticky="w", padx=5, pady=2)
            documents_text = ", ".join(details['documents']) if details['documents'] else "None"
            Label(record_frame, text=documents_text, font=("Calibri", 12), bg="white",
                wraplength=500, justify="left")\
                .grid(row=5, column=1, sticky="w", padx=5, pady=2)

        # Footer: Create a frame at the bottom to hold the buttons vertically
        footer_frame = Frame(frame, bg="#f4f4f9")
        footer_frame.pack(side="bottom", pady=10)

        def save_report():
            report_text = self.generate_report_text()
            file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                    filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
            if file_path:
                try:
                    with open(file_path, "w") as file:
                        file.write(report_text)
                    messagebox.showinfo("Report Saved", f"Report successfully saved to:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save report: {e}")

        # Pack buttons vertically inside the footer frame
        Button(footer_frame, text="Back", font=("Calibri", 12, "bold"), bg="#e60000", fg="white",  width=15,
            command=lambda: self.show_frame("headminister")).pack(pady=5)
        Button(footer_frame, text="Save as PDF", font=("Calibri", 12, "bold"), bg="#0073e6", fg="white",  width=15 ,
            command=lambda: self.save_report_as_pdf(self.generate_report_text())).pack(pady=5)
        Button(footer_frame, text="Save Report", font=("Calibri", 12, "bold"), bg="#0073e6", fg="white",  width=15 ,
            command=save_report).pack(pady=5)

        self.frames["report_headminister"] = frame
        if show:
            self.show_frame("report_headminister")

    def refresh_report_frames(self):
        # Remember the currently visible frame.
        current = self.current_frame if hasattr(self, "current_frame") else None

        # Refresh admin report frame.
        if "report" in self.frames:
            self.frames["report"].destroy()
        self.create_report_frame(show=False)  # Build without auto-showing.

        # Refresh headminister report frame.
        if "report_headminister" in self.frames:
            self.frames["report_headminister"].destroy()
        self.create_report_headminister_frame(show=False)

        # Return to the current frame (if still available).
        if current:
            self.show_frame(current)


    # USER PART
    def create_user_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        self.user_title_bar = Frame(frame, bg="darkblue", height=60)
        self.user_title_bar.pack(fill="x")
        self.user_title_label = Label(self.user_title_bar, text="Welcome, Student 🎓", font=("Comic Sans MS", 20, "bold"), bg="darkblue", fg="white")
        self.user_title_label.pack(pady=10)


        Button(frame, text="📄 Apply Aid", font=("Calibri", 14), bg="#0073e6", fg="white", width=20, command=lambda: self.show_frame("apply_aid")).pack(pady=10)
        Button(frame, text="📊 View Aid", font=("Calibri", 14), bg="#0073e6", fg="white", width=20, command=lambda: self.show_frame("view_aid")).pack(pady=10)
        Button(frame, text="👤 View My Details", font=("Calibri", 14), bg="#0073e6", fg="white", width=20, command=self.show_user_details).pack(pady=10)

        def logout():
            if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
                self.show_frame("login")
        Button(frame, text="🚪 Logout", font=("Calibri", 14), bg="#e60000", fg="white", width=20, command=logout).pack(pady=20)
        Label(frame, text="© Group 5. All Rights Reserved.", font=("Calibri", 10), bg="#f4f4f9", fg="#666").pack(side="bottom", pady=10)
        self.frames["user"] = frame

    def submit_aid_request(self):
        username = self.username_entry.get()
        aid_type = self.aid_type_var.get()
        description = self.description_text.get("1.0", END).strip()
        
        # Use the stored file paths from self.uploaded_files if they exist
        documents = self.uploaded_files if hasattr(self, "uploaded_files") else []
        
        if not username or not aid_type or not description:
            messagebox.showerror("Error", "All fields are required!")
            return
        request_id = f"AID{len(aid_requests) + 1:04d}"
        save_aid_request(request_id, username, aid_type, description, documents)
        messagebox.showinfo("Success", f"Aid Request Submitted! Your Request ID: {request_id}")
        self.reset_form()
        self.refresh_report_frames()  # Update the reports.

    def reset_form(self):
        self.username_entry.delete(0, END)
        self.description_text.delete("1.0", END)
        self.file_list.delete(0, END)

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            # Create an "uploads" folder in your BASE_DIR if it doesn't exist.
            uploads_dir = os.path.join(BASE_DIR, "uploads")
            os.makedirs(uploads_dir, exist_ok=True)
            
            # Copy the selected file into the uploads folder.
            import shutil
            dest_path = os.path.join(uploads_dir, os.path.basename(file_path))
            shutil.copy(file_path, dest_path)
            
            # Store the relative path (or absolute if you prefer) of the uploaded file.
            relative_path = os.path.relpath(dest_path, BASE_DIR)
            
            # Add the filename (or path) to the file list widget for display.
            self.file_list.insert(END, os.path.basename(dest_path))
            
            # Keep a list of the stored file paths for use when submitting.
            if not hasattr(self, "uploaded_files"):
                self.uploaded_files = []
            self.uploaded_files.append(relative_path)

    def view_aid_requests(self):
        request_id = self.request_id_entry.get().strip() 
        print("Looking for request ID:", request_id)
        print("Available IDs:", list(aid_requests.keys())) 
        if request_id in aid_requests:
            request = aid_requests[request_id]
            self.details_text.set(
                f"Username: {request['username']}\n"
                f"Aid Type: {request['aid_type']}\n"
                f"Status: {request['status']}\n"
                f"Description: {request['description']}"
            )
            self.doc_list.delete(0, END)
            for doc in request['documents']:
                self.doc_list.insert(END, os.path.basename(doc))

        else:
            messagebox.showerror("Error", "Request ID not found!")

    def create_user_apply_aid_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, text="Apply for Aid", font=("Comic Sans MS", 20, "bold"), bg="#141885", fg="white").pack(pady=20)

        container = Frame(frame, bg="white")
        container.pack(pady=20, padx=40, fill="both", expand=True)
        Label(container, text="Username:", font=("Calibri", 14), bg="white").pack(pady=5)
        self.username_entry = Entry(container, font=("Calibri", 14))
        self.username_entry.pack(pady=5)
        Label(container, text="Aid Type:", font=("Calibri", 14), bg="white").pack(pady=5)
        self.aid_type_var = StringVar()
        OptionMenu(container, self.aid_type_var, "Hostel", "Counselling", "Finance").pack(pady=5)
        Label(container, text="Description:", font=("Calibri", 14), bg="white").pack(pady=5)
        self.description_text = Text(container, height=4, width=50, font=("Calibri", 14))
        self.description_text.pack(pady=5)
        Label(container, text="Upload Documents:", font=("Calibri", 14), bg="white").pack(pady=5)
        Button(container, text="Choose File", command=self.upload_file, font=("Calibri", 14), bg="#0073e6", fg="white").pack(pady=5)
        self.file_list = Listbox(container, height=3, font=("Calibri", 14))
        self.file_list.pack(pady=5)
        Button(container, text="Submit Aid Request", command=self.submit_aid_request, font=("Calibri", 14), bg="#0073e6", fg="white").pack(pady=10)
        Button(container, text="Back", font=("Calibri", 14), bg="#e60000", fg="white", command=lambda: self.show_frame("user")).pack(pady=5)
        self.frames["apply_aid"] = frame

    def create_user_view_aid_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, text="View Aid Request", font=("Comic Sans MS", 20, "bold"), bg="#141885", fg="white").pack(pady=20)
        
        container = Frame(frame, bg="white")
        container.pack(pady=20, padx=40, fill="both", expand=True)

        request_id_frame = Frame(container, bg="#D3D3D3", padx=10, pady=10)
        request_id_frame.pack(pady=5, fill="x")

        Label(request_id_frame, text="Enter Request ID:", font=("Calibri", 14), bg="#D3D3D3").pack(side="left", pady=5)
        self.request_id_entry = Entry(request_id_frame, font=("Calibri", 14))
        self.request_id_entry.pack(side="left", pady=5)

        Button(container, text="View Request", command=self.view_aid_requests, font=("Calibri", 14), bg="#0073e6", fg="white").pack(pady=10)
        details_frame = Frame(container, bg="#D3D3D3", padx=10, pady=10)
        details_frame.pack(pady=5, fill="both", expand=False)
        self.details_text = StringVar()
        Label(details_frame, textvariable=self.details_text, justify=LEFT, wraplength=400, font=("Calibri", 16), bg="#D3D3D3", anchor="w").pack(pady=10)
        documents_frame = Frame(container, bg="#D3D3D3", padx=10, pady=10)
        documents_frame.pack(pady=5, fill="x")
        Label(documents_frame, text="Documents:", font=("Calibri", 14), bg="#D3D3D3").pack(side="left", pady=5)
        self.doc_list = Listbox(documents_frame, height=3, font=("Calibri", 14), bg="#D3D3D3")
        self.doc_list.pack(side="left", pady=5)
        Button(container, text="Back", font=("Calibri", 14), bg="#e60000", fg="white", command=lambda: self.show_frame("user")).pack(pady=5)
        self.frames["view_aid"] = frame

    def create_user_details_frame(self):
        frame = Frame(self.root, bg="white")
        header = Frame(frame, bg="#141885", height=80)
        header.pack(fill="x")
        Label(header, text="My details", font=("Helvetica", 22, "bold"), bg="#141885", fg="white").pack(pady=20)
        container = Frame(frame, bg="white")
        container.pack(pady=20, padx=40, fill="both", expand=True)
        self.details_labels = {}
        self.details_labels["username"] = Label(container, text="Username: ", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=2)
        self.details_labels["username"].pack(pady=10, padx=10, fill="x")
        self.details_labels["password"] = Label(container, text="Password: ", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=2)
        self.details_labels["password"].pack(pady=10, padx=10, fill="x")
        row1 = Frame(container, bg="white")
        row1.pack(pady=5, padx=10, fill="x")
        self.details_labels["balance"] = Label(row1, text="Balance: ", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=25, height=4)
        self.details_labels["balance"].pack(side="left", padx=5, expand=True, fill="both")
        self.details_labels["phonenumber"] = Label(row1, text="Telephone number:", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=25, height=4)
        self.details_labels["phonenumber"].pack(side="right", padx=5, expand=True, fill="both")
        self.details_labels["address"] = Label(container, text="Address: ", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=4)
        self.details_labels["address"].pack(pady=10, padx=10, fill="x")
        Button(container, text="🔙 Back", font=("Calibri", 14), bg="#e60000", fg="white", width=20, command=lambda: self.show_frame("user")).pack(pady=20)
        Button(container, text="Update", font=("Calibri", 14), bg="#e60000", fg="white", width=20, command=lambda: self.show_frame("update_user_details")).pack(pady=20)
        self.frames["user_details"] = frame

    def show_user_details(self):
        if self.username and self.username in users_dict:
            user = users_dict[self.username]
            self.details_labels["username"].config(text=f"Username: {user.get('username', 'N/A')}")
            self.details_labels["password"].config(text=f"Password: {user.get('password', 'N/A')}")
            self.details_labels["balance"].config(text=f"Balance: RM {user.get('balance', 'Not Provided')}")
            self.details_labels["phonenumber"].config(text=f"Telephone number:\n{user.get('phonenumber', 'Not Provided')}")
            self.details_labels["address"].config(text=f"Address: {user.get('address', 'Not Provided')}")
            self.show_frame("user_details")
        else:
            messagebox.showwarning("Error", "User details not found!")

    def create_update_user_details_frame(self):
        frame = Frame(self.root, bg="white")
        header = Frame(frame, bg="#141885", height=80)
        header.pack(fill="x")
        Label(header, text="Update My Details", font=("Helvetica", 22, "bold"), bg="#141885", fg="white").pack(pady=20)
        container = Frame(frame, bg="white")
        container.pack(pady=20, padx=40, fill="both", expand=True)
        self.user_update_entries = {}

        def create_update_entry(label_text, field_name):
            field_frame = Frame(container, bg="white")
            field_frame.pack(fill="x", pady=10)
            label = Label(field_frame, text=label_text, font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=2)
            label.pack(fill="x")
            entry = Entry(field_frame, font=("Calibri", 14), width=50, bd=0, bg="#D3D3D3")
            entry.pack(fill="x", pady=5)
            if self.username and self.username in users_dict:
                entry.insert(0, users_dict[self.username].get(field_name, ""))
            self.user_update_entries[field_name] = entry
            return entry

        self.user_update_entries["username"] = create_update_entry("Username:", "username")
        self.user_update_entries["password"] = create_update_entry("Password:", "password")
        self.user_update_entries["phonenumber"] = create_update_entry("Telephone number:", "phonenumber")
        self.user_update_entries["address"] = create_update_entry("Address:", "address")

        def save_and_return():
            username = self.user_update_entries["username"].get().strip()
            password = self.user_update_entries["password"].get().strip()
            phone = self.user_update_entries["phonenumber"].get().strip() or "Not Provided"
            address = self.user_update_entries["address"].get().strip() or "Not Provided"
            if not username or not password:
                messagebox.showwarning("Error", "Username and Password must be filled!")
                return
            if not self.username or self.username not in users_dict:
                messagebox.showerror("Error", "User data not found! Ensure you're logged in.")
                return
            users_dict[self.username] = {
                "username": username,
                "password": password,
                "balance": users_dict[self.username]["balance"],
                "address": address,
                "phonenumber": phone
            }
            with open(USER_FILE_PATH, "w") as file:
                for u_id, user in users_dict.items():
                    file.write(f"{u_id}:{user.get('username', 'N/A')}:{user.get('password', 'N/A')}:{user.get('balance', 'Not Provided')}|{user.get('address', 'Not Provided')}|{user.get('phonenumber', 'Not Provided')}\n")
            messagebox.showinfo("Success", "User details updated successfully!")
            clear_entries()
            self.show_user_details()

        def clear_entries():
            for entry in self.user_update_entries.values():
                entry.delete(0, END)

        def back_and_clear():
            clear_entries()
            self.show_frame("user_details")

        button_frame = Frame(container, bg="white")
        button_frame.pack(pady=20)
        Button(button_frame, text="🔙 Back", font=("Calibri", 14), bg="#e60000", fg="white", width=20, command=back_and_clear).pack(pady=5)
        Button(button_frame, text="Save & Return", font=("Calibri", 14), bg="#0073e6", fg="white", width=20, command=save_and_return).pack(pady=5)
        self.frames["update_user_details"] = frame

    # GUIDANCE PART
    def create_guidance_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, text="📘 Guidance Dashboard", font=("Comic Sans MS", 20, "bold"), bg="#141885", fg="white").pack(pady=20)

        Button(frame, text="👥 View User Details", font=("Calibri", 14), bg="#0073e6", fg="white", width=20, command=lambda: self.show_frame("check_user_details_guidance")).pack(pady=10)
        Button(frame, text="📊 View Aid Requests", font=("Calibri", 14), bg="#0073e6", fg="white", width=20, command=lambda: self.show_frame("guidance_view_aid")).pack(pady=10)
        Button(frame, text="👤 View My Details", font=("Calibri", 14), bg="#0073e6", fg="white", width=20, command=self.show_guidance_details).pack(pady=10)
        def logout():
            if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
                self.show_frame("login")
        Button(frame, text="🚪 Logout", font=("Calibri", 14), bg="#e60000", fg="white", width=20, command=logout).pack(pady=20)
        self.frames["guidance"] = frame

    def create_guidance_view_aid_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, text="View Aid Requests", font=("Comic Sans MS", 20, "bold"), bg="#141885", fg="white").pack(pady=20)

        container = Frame(frame, bg="white")
        container.pack(pady=20, padx=40, fill="both", expand=True)

        # Request ID Entry
        request_id_frame = Frame(container, bg="#D3D3D3", padx=10, pady=10)
        request_id_frame.pack(pady=5, fill="x")
        Label(request_id_frame, text="Enter Request ID:", font=("Calibri", 14), bg="#D3D3D3").pack(side="left", pady=5)
        self.guidance_request_id_entry = Entry(request_id_frame, font=("Calibri", 14))
        self.guidance_request_id_entry.pack(side="left", pady=5)

        # View Request Button
        Button(container, text="View Request", command=self.guidance_view_aid_requests, font=("Calibri", 14), bg="#0073e6", fg="white").pack(pady=10)

        # Buttons for Accept / Decline
        button_frame = Frame(container, bg="white")
        button_frame.pack(pady=10)
        Button(button_frame, text="Accept Request", font=("Calibri", 14), bg="green", fg="white", command=self.accept_request).pack(side="left", padx=5)
        Button(button_frame, text="Decline Request", font=("Calibri", 14), bg="red", fg="white", command=self.decline_request).pack(side="left", padx=5)

        # ---
        # **New Code**: Create the details area and document list
        details_frame = Frame(container, bg="#D3D3D3", padx=10, pady=10)
        details_frame.pack(pady=5, fill="both", expand=False)
        self.guidance_details_text = StringVar()  # This variable is used in guidance_view_aid_requests
        Label(details_frame, textvariable=self.guidance_details_text, justify=LEFT, wraplength=400, 
            font=("Calibri", 16), bg="#D3D3D3", anchor="w").pack(pady=10)

        # Documents area
        documents_frame = Frame(container, bg="#D3D3D3", padx=10, pady=10)
        documents_frame.pack(pady=5, fill="x")
        Label(documents_frame, text="Documents:", font=("Calibri", 14), bg="#D3D3D3").pack(side="left", pady=5)
        self.guidance_doc_list = Listbox(documents_frame, height=3, font=("Calibri", 14), bg="#D3D3D3")
        self.guidance_doc_list.pack(side="left", pady=5)


        Button(container, text="Download Selected File", font=("Calibri", 14), bg="#0073e6", fg="white", command=self.download_file).pack(pady=5)
        Button(container, text="Back", font=("Calibri", 14), bg="#e60000", fg="white", command=lambda: self.show_frame("guidance")).pack(pady=5)

        self.frames["guidance_view_aid"] = frame

    def accept_request(self):
        request_id = self.guidance_request_id_entry.get().strip()

        if request_id in aid_requests:
            # Get the department of the logged-in guidance user
            guidance_department = guidance_dict[self.username]["department"]
            
            # Get the department of the aid request
            request_department = aid_requests[request_id]["aid_type"]  # assuming the 'aid_type' corresponds to the department
            
            # Check if the departments match
            if guidance_department == request_department:
                aid_requests[request_id]["status"] = "Accepted"
                self.update_aid_requests_file()
                messagebox.showinfo("Success", f"Request {request_id} has been accepted.")
                
                # Refresh the guidance details label to show the new status.
                self.guidance_view_aid_requests()
                # Optionally, refresh any report frames if necessary:
                self.refresh_report_frames()

                # Make the success message disappear after 2 seconds (2000 ms)
                self.after(2000, lambda: messagebox.showinfo("Success", "Request has been accepted!"))
            else:
                messagebox.showerror("Error", "You can only accept requests that match your department!")

                # Make the error message disappear after 2 seconds (2000 ms)
                self.after(2000, lambda: messagebox.showerror("Error", "Request could not be accepted!"))

        else:
            messagebox.showerror("Error", "Request ID not found!")
            
            # Make the error message disappear after 2 seconds (2000 ms)
            self.after(2000, lambda: messagebox.showerror("Error", "Request ID not found!"))

    def decline_request(self):
        request_id = self.guidance_request_id_entry.get().strip()

        if request_id in aid_requests:
            # Get the department of the logged-in guidance user
            guidance_department = guidance_dict[self.username]["department"]
            
            # Get the department of the aid request
            request_department = aid_requests[request_id]["aid_type"]  # assuming the 'aid_type' corresponds to the department
            
            # Check if the departments match
            if guidance_department == request_department:
                aid_requests[request_id]["status"] = "Declined"
                self.update_aid_requests_file()
                
                # Refresh the guidance details label to show the new status.
                self.guidance_view_aid_requests()
                # Optionally, refresh any report frames if necessary:
                self.refresh_report_frames()
                messagebox.showinfo("Success", f"Request {request_id} has been declined.")
            else:
                # Pop-up error message if departments don't match
                messagebox.showerror("Error", "You can only decline requests that match your department!")

        else:
            # Create a pop-up error message if request ID is not found
            messagebox.showerror("Error", "Request ID not found!")

    def download_file(self):
        selected_index = self.guidance_doc_list.curselection()
        if not selected_index:
            messagebox.showerror("Error", "No file selected!")
            return
        # Get the displayed filename from the listbox.
        filename = self.guidance_doc_list.get(selected_index)
        
        # Get the current aid request ID.
        request_id = self.guidance_request_id_entry.get().strip()
        if request_id not in aid_requests:
            messagebox.showerror("Error", "Aid Request not found!")
            return
        
        # Find the stored file path that corresponds to the selected filename.
        file_path = None
        for doc in aid_requests[request_id]['documents']:
            if os.path.basename(doc) == filename:
                file_path = os.path.join(BASE_DIR, doc)  # Build absolute path
                break
                
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "File not found on disk!")
            return
        
        # Ask the user where to save (download) the file.
        dest = filedialog.asksaveasfilename(initialfile=filename, defaultextension=os.path.splitext(filename)[1])
        if dest:
            import shutil
            shutil.copy(file_path, dest)
            messagebox.showinfo("Success", f"File downloaded to:\n{dest}")

    def update_aid_requests_file(self):
        with open(AID_REQUESTS_FILE, "w") as file:
            formatted_requests = []
            for req_id, details in aid_requests.items():
                formatted_requests.append({
                    "request_id": req_id,
                    "username": details["username"],
                    "aid_type": details["aid_type"],
                    "description": details["description"],
                    "documents": details["documents"],
                    "status": details["status"]
                })
            json.dump(formatted_requests, file, indent=4)

    def guidance_view_aid_requests(self):
        request_id = self.guidance_request_id_entry.get().strip()
        if request_id in aid_requests:
            request = aid_requests[request_id]
            self.guidance_details_text.set(
                f"Username: {request['username']}\n"
                f"Aid Type: {request['aid_type']}\n"
                f"Status: {request['status']}\n"
                f"Description: {request['description']}"
            )
            self.guidance_doc_list.delete(0, END)
            for doc in request['documents']:
                self.guidance_doc_list.insert(END, os.path.basename(doc))

        else:
            messagebox.showerror("Error", "Request ID not found!")

    def create_guidance_user_details_frame(self):
        frame = Frame(self.root, bg="white")
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, text="User's detail", font=("Comic Sans MS", 20, "bold"), bg="#141885", fg="white").pack(pady=20)
        
        container = Frame(frame, bg="white")
        container.pack(pady=20, padx=40, fill="both", expand=True)
        self.guidance_details_labels = {}
        self.guidance_details_labels["username"] = Label(container, text="Username: ", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=2)
        self.guidance_details_labels["username"].pack(pady=10, padx=10, fill="x")
        self.guidance_details_labels["password"] = Label(container, text="Password: ", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=2)
        self.guidance_details_labels["password"].pack(pady=10, padx=10, fill="x")
        row1 = Frame(container, bg="white")
        row1.pack(pady=5, padx=10, fill="x")
        self.guidance_details_labels["balance"] = Label(row1, text="Balance: ", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=25, height=4)
        self.guidance_details_labels["balance"].pack(side="left", padx=5, expand=True, fill="both")
        self.guidance_details_labels["phonenumber"] = Label(row1, text="Telephone number:", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=25, height=4)
        self.guidance_details_labels["phonenumber"].pack(side="right", padx=5, expand=True, fill="both")
        self.guidance_details_labels["address"] = Label(container, text="Address: ", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=4)
        self.guidance_details_labels["address"].pack(pady=10, padx=10, fill="x")
        Button(container, text="🔙 Back", font=("Calibri", 14), bg="#e60000", fg="white", width=20, command=lambda: self.show_frame("check_user_details_guidance")).pack(pady=20)
        self.frames["user_details_guidance"] = frame

    def show_user_details_guidance(self, user_id):
        if "balance" not in self.guidance_details_labels:
            self.create_guidance_user_details_frame()
        if user_id in users_dict:
            user = users_dict[user_id]
            self.guidance_details_labels["username"].config(text=f"Username: {user.get('username', 'N/A')}")
            self.guidance_details_labels["password"].config(text=f"Password: {user.get('password', 'N/A')}")
            self.guidance_details_labels["balance"].config(text=f"Balance: RM {user.get('balance', 'Not Provided')}")
            self.guidance_details_labels["phonenumber"].config(text=f"Telephone number: {user.get('phonenumber', 'Not Provided')}")
            self.guidance_details_labels["address"].config(text=f"Address: {user.get('address', 'Not Provided')}")
            self.show_frame("user_details_guidance")
        else:
            messagebox.showwarning("Error", "User details not found!")

    def create_select_user_for_details_guidance_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, text="Search Users", font=("Comic Sans MS", 20, "bold"), bg="#141885", fg="white").pack(pady=20)

        name_entry = Entry(frame, font=("Calibri", 14))
        name_entry.pack(pady=10)
        name_entry.focus()
        name_list = Listbox(frame, width=50)
        name_list.pack(pady=10)

        def update(data=None):
            name_list.delete(0, END)
            for item in (data or users_dict.keys()):
                name_list.insert(END, item)

        def fillblank(event):
            name_entry.delete(0, END)
            name_entry.insert(0, name_list.get(ACTIVE))

        def check(event):
            typed = name_entry.get().strip().lower()
            update([user_id for user_id in users_dict if typed in user_id.lower()])

        def view_user_details():
            selected_user = name_list.get(ACTIVE)
            if selected_user in users_dict:
                self.show_user_details_guidance(selected_user)
            else:
                messagebox.showwarning("Error", "No user selected. Please select a user from the list.")

        Button(frame, text="View Details", font=("Calibri", 14), bg="#0073e6", fg="white", command=view_user_details).pack(pady=10)
        Button(frame, text="Back", font=("Calibri", 14), bg="#e60000", fg="white", command=lambda: self.show_frame("guidance")).pack(pady=5)
        name_list.bind("<<ListboxSelect>>", fillblank)
        name_entry.bind("<KeyRelease>", check)
        update()
        self.frames["check_user_details_guidance"] = frame

    def create_guidance_details_frame(self):
        frame = Frame(self.root, bg="white")
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, text="My Details", font=("Comic Sans MS", 20, "bold"), bg="#141885", fg="white").pack(pady=20)
        
        container = Frame(frame, bg="white")
        container.pack(pady=20, padx=40, fill="both", expand=True)
        self.guidance_details_labels = {}
        self.guidance_details_labels["username"] = Label(container, text="Username: ", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=2)
        self.guidance_details_labels["username"].pack(pady=10, padx=10, fill="x")
        self.guidance_details_labels["password"] = Label(container, text="Password: ", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=2)
        self.guidance_details_labels["password"].pack(pady=10, padx=10, fill="x")
        self.guidance_details_labels["phonenumber"] = Label(container, text="Phone Number: ", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=2)
        self.guidance_details_labels["phonenumber"].pack(pady=10, padx=10, fill="x")
        self.guidance_details_labels["department"] = Label(container, text="Department: ", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=2)
        self.guidance_details_labels["department"].pack(pady=10, padx=10, fill="x")
        Button(container, text="🔙 Back", font=("Calibri", 14), bg="#e60000", fg="white", width=20, command=lambda: self.show_frame("guidance")).pack(pady=20)
        Button(container, text="Update", font=("Calibri", 14), bg="#0073e6", fg="white", width=20, command=lambda: self.show_frame("update_guidance_details")).pack(pady=10)
        self.frames["guidance_details"] = frame

    def show_guidance_details(self):
        if not self.guidance_details_labels or "department" not in self.guidance_details_labels:
            self.create_guidance_details_frame()
        if self.username and self.username in guidance_dict:
            user_data = guidance_dict[self.username]
            guidance_phone = user_data.get("phonenumber", "Not Available")
            guidance_department = user_data.get("department", "Not Available")
            self.guidance_details_labels["username"].config(text=f"Username: {user_data.get('username', 'N/A')}")
            self.guidance_details_labels["password"].config(text=f"Password: {user_data.get('password', 'N/A')}")
            self.guidance_details_labels["phonenumber"].config(text=f"Phone Number: {guidance_phone}")
            self.guidance_details_labels["department"].config(text=f"Department: {guidance_department}")
            self.show_frame("guidance_details")
        else:
            messagebox.showwarning("Error", "Guidance user details not found!")

    def create_update_guidance_details_frame(self):
        frame = Frame(self.root, bg="white")
        if not hasattr(self, "guidance_department"):
            self.guidance_department = "Finance"
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, text="Update My Details", font=("Comic Sans MS", 20, "bold"), bg="#141885", fg="white").pack(pady=20)
        
        container = Frame(frame, bg="white")
        container.pack(pady=20, padx=40, fill="both", expand=True)
        self.guidance_update_entries = {}

        def create_update_entry(label_text, field_name, is_dropdown=False):
            field_frame = Frame(container, bg="white")
            field_frame.pack(fill="x", pady=10)
            label = Label(field_frame, text=label_text, font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=2)
            label.pack(fill="x")
            if is_dropdown:
                department_options = ["Finance", "Scholarship", "Hostel", "Counseling"]
                selected_department = StringVar()
                selected_department.set(self.guidance_department)
                dropdown = OptionMenu(field_frame, selected_department, *department_options)
                dropdown.config(font=("Calibri", 14), width=48, bg="#D3D3D3", bd=0)
                dropdown.pack(fill="x", pady=5)
                self.guidance_update_entries[field_name] = selected_department
            else:
                entry = Entry(field_frame, font=("Calibri", 14), width=50, bd=0, bg="#D3D3D3")
                entry.pack(fill="x", pady=5)
                if self.username in guidance_dict:
                    entry.insert(0, guidance_dict[self.username].get(field_name, ""))
                self.guidance_update_entries[field_name] = entry

        create_update_entry("Username:", "username")
        create_update_entry("Password:", "password")
        create_update_entry("Phone Number:", "phonenumber")
        create_update_entry("Department:", "department", is_dropdown=True)

        def clear_entries():
            for key, entry in self.guidance_update_entries.items():
                if isinstance(entry, StringVar):
                    entry.set("Finance")
                else:
                    entry.delete(0, END)

        def save_and_return():
            new_username = self.guidance_update_entries["username"].get().strip()
            new_password = self.guidance_update_entries["password"].get().strip()
            new_phonenumber = self.guidance_update_entries["phonenumber"].get().strip()
            new_department = self.guidance_update_entries["department"].get().strip()
            if not new_username or not new_password or not new_phonenumber or not new_department:
                messagebox.showwarning("Error", "All fields must be filled!")
                return
            if new_department not in ["Finance", "Scholarship", "Hostel", "Counseling"]:
                messagebox.showwarning("Error", "Invalid department selected!")
                return
            if self.username not in guidance_dict:
                messagebox.showerror("Error", "Could not find user data!")
                return
            guidance_dict[new_username] = {
                "username": new_username,
                "password": new_password,
                "phonenumber": new_phonenumber,
                "department": new_department
            }
            if new_username != self.username:
                del guidance_dict[self.username]
            with open(GUIDANCE_FILE_PATH, "w") as file:
                for user_id, user_data in guidance_dict.items():
                    file.write(f"{user_data['username']}:{user_data['password']}:{user_data['phonenumber']}:{user_data['department']}\n")
            messagebox.showinfo("Success", "Details updated successfully!")
            clear_entries()
            self.username = new_username
            self.show_guidance_details()

        def back_and_clear():
            clear_entries()
            self.show_guidance_details()

        button_frame = Frame(container, bg="white")
        button_frame.pack(pady=20)
        Button(button_frame, text="🔙 Back", font=("Calibri", 14), bg="#e60000", fg="white", width=20, command=back_and_clear).pack(pady=5)
        Button(button_frame, text="Save & Return", font=("Calibri", 14), bg="#0073e6", fg="white", width=20, command=save_and_return).pack(pady=5)
        self.frames["update_guidance_details"] = frame

    # HEADMINISTER PART
    def create_headminister_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, text="🏛 Head Minister Dashboard", font=("Comic Sans MS", 20, "bold"), bg="#141885", fg="white").pack(pady=20)
        
        # Existing buttons:
        Button(frame, text="🔧 Manage Accounts", font=("Calibri", 14),
            bg="#0073e6", fg="white", width=20, command=lambda: self.show_frame("headminister_manage_account")).pack(pady=10)
        Button(frame, text="👥 View User Details", font=("Calibri", 14),
            bg="#0073e6", fg="white", width=20, command=lambda: self.show_frame("check_user_details_headminister")).pack(pady=10)
        
        # --- NEW: Report button for headminister ---
        Button(frame, text="📊 Report List", font=("Calibri", 14),
            bg="#0073e6", fg="white", width=20, command=lambda: self.show_frame("report_headminister")).pack(pady=10)
        
        def logout():
            if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
                self.show_frame("login")
        Button(frame, text="🚪 Logout", font=("Calibri", 14),
            bg="#e60000", fg="white", width=20, command=logout).pack(pady=20)
        
        self.frames["headminister"] = frame

    def create_select_user_for_details_headminister_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, text="Search Users", font=("Comic Sans MS", 20, "bold"), bg="#141885", fg="white").pack(pady=20)

        name_entry = Entry(frame, font=("Calibri", 14))
        name_entry.pack(pady=10)
        name_entry.focus()
        name_list = Listbox(frame, width=50)
        name_list.pack(pady=10)
        def update(data=None):
            name_list.delete(0, END)
            if data is None:
                data = list(users_dict.keys())
            for item in data:
                display_text = f"{users_dict[item]['username']} - {item}"
                name_list.insert(END, display_text)
        def fillblank(event):
            selected = name_list.get(ACTIVE)
            user_id = selected.split(" - ")[1]
            name_entry.delete(0, END)
            name_entry.insert(0, user_id)
        def check(event):
            typed = name_entry.get().strip().lower()
            data = [user_id for user_id in users_dict if typed in user_id.lower() or typed in users_dict[user_id]['username'].lower()]
            update(data)
        def view_user_details():
            selected = name_list.get(ACTIVE)
            if selected:
                user_id = selected.split(" - ")[1]
                if user_id in users_dict:
                    self.show_user_details_headminister(user_id)
                else:
                    messagebox.showwarning("Error", "Invalid user selection.")
            else:
                messagebox.showwarning("Error", "No user selected. Please select a user from the list.")
        Button(frame, text="View Details", font=("Calibri", 14), bg="#0073e6", fg="white", command=view_user_details).pack(pady=10)
        Button(frame, text="Back", font=("Calibri", 14), bg="#e60000", fg="white", command=lambda: self.show_frame("headminister")).pack(pady=5)
        name_list.bind("<<ListboxSelect>>", fillblank)
        name_entry.bind("<KeyRelease>", check)
        update()
        self.frames["check_user_details_headminister"] = frame

    def create_headminister_user_details_frame(self):
        frame = Frame(self.root, bg="white")
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, text="User's detail", font=("Comic Sans MS", 20, "bold"), bg="#141885", fg="white").pack(pady=20)
        container = Frame(frame, bg="white")
        container.pack(pady=20, padx=40, fill="both", expand=True)
        self.headminister_details_labels = {}
        self.headminister_details_labels["username"] = Label(container, text="Username: ", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=2)
        self.headminister_details_labels["username"].pack(pady=10, padx=10, fill="x")
        self.headminister_details_labels["password"] = Label(container, text="Password: ", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=2)
        self.headminister_details_labels["password"].pack(pady=10, padx=10, fill="x")
        row1 = Frame(container, bg="white")
        row1.pack(pady=5, padx=10, fill="x")
        self.headminister_details_labels["balance"] = Label(row1, text="Balance: ", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=25, height=4)
        self.headminister_details_labels["balance"].pack(side="left", padx=5, expand=True, fill="both")
        self.headminister_details_labels["phonenumber"] = Label(row1, text="Telephone number:", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=25, height=4)
        self.headminister_details_labels["phonenumber"].pack(side="right", padx=5, expand=True, fill="both")
        self.headminister_details_labels["address"] = Label(container, text="Address: ", font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=4)
        self.headminister_details_labels["address"].pack(pady=10, padx=10, fill="x")
        Button(container, text="🔙 Back", font=("Calibri", 14), bg="#e60000", fg="white", width=20, command=lambda: self.show_frame("check_user_details_headminister")).pack(pady=20)
        Button(container, text="Update", font=("Calibri", 14), bg="#e60000", fg="white", width=20, command=lambda: self.show_frame("update_user_details_headminister")).pack(pady=20)
        self.frames["user_details_headminister"] = frame

    def show_user_details_headminister(self, user_id):
        self.selected_user_id = user_id
        user = users_dict[user_id]
        self.headminister_details_labels["username"].config(text=f"Username: {user.get('username', 'N/A')}")
        self.headminister_details_labels["password"].config(text=f"Password: {user.get('password', 'N/A')}")
        self.headminister_details_labels["balance"].config(text=f"Balance: RM {user.get('balance', 'Not Provided')}")
        self.headminister_details_labels["phonenumber"].config(text=f"Telephone number:\n{user.get('phonenumber', 'Not Provided')}")
        self.headminister_details_labels["address"].config(text=f"Address: {user.get('address', 'Not Provided')}")
        self.show_frame("user_details_headminister")

    def create_headminister_update_user_details_frame(self):
        frame = Frame(self.root, bg="white")
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, text="Update User's Details", font=("Comic Sans MS", 20, "bold"), bg="#141885", fg="white").pack(pady=20)
        
        container = Frame(frame, bg="white")
        container.pack(pady=20, padx=40, fill="both", expand=True)
        self.headminister_update_entries = {}

        def create_update_entry(label_text, current_value):
            field_frame = Frame(container, bg="white")
            field_frame.pack(fill="x", pady=10)
            label = Label(field_frame, text=label_text, font=("Calibri", 14, "bold"), bg="#D3D3D3", fg="black", anchor="w", padx=10, width=50, height=2)
            label.pack(fill="x")
            entry = Entry(field_frame, font=("Calibri", 14), width=50, bd=0, bg="#D3D3D3")
            entry.pack(fill="x", pady=5)
            entry.insert(0, current_value)
            return entry

        self.headminister_update_entries["username"] = create_update_entry("Username:", "")
        self.headminister_update_entries["password"] = create_update_entry("Password:", "")
        self.headminister_update_entries["phonenumber"] = create_update_entry("Telephone number:", "")
        self.headminister_update_entries["address"] = create_update_entry("Address:", "")

        def clear_entries():
            for entry in self.headminister_update_entries.values():
                entry.delete(0, END)

        def save_and_return():
            username = self.headminister_update_entries["username"].get().strip()
            password = self.headminister_update_entries["password"].get().strip()
            phone = self.headminister_update_entries["phonenumber"].get().strip() or "Not Provided"
            address = self.headminister_update_entries["address"].get().strip() or "Not Provided"
            if not username or not password:
                messagebox.showwarning("Error", "Username and Password must be filled!")
                return
            users_dict[self.selected_user_id] = {
                "username": username,
                "password": password,
                "balance": users_dict[self.selected_user_id]["balance"],
                "address": address,
                "phonenumber": phone
            }
            with open(USER_FILE_PATH, "w") as file:
                for u_id, user in users_dict.items():
                    file.write(f"{u_id}:{user.get('username', 'N/A')}:{user.get('password', 'N/A')}:{user.get('balance', 'Not Provided')}|{user.get('address', 'Not Provided')}|{user.get('phonenumber', 'Not Provided')}\n")
            messagebox.showinfo("Success", "User details updated successfully!")
            clear_entries()
            self.frames["headminister"].destroy()
            self.frames["check_user_details_headminister"].destroy()
            self.frames["user_details_headminister"].destroy()
            self.create_headminister_frame()
            self.create_select_user_for_details_headminister_frame()
            self.create_headminister_user_details_frame()
            self.show_user_details_headminister(self.selected_user_id)

        def back_and_clear():
            clear_entries()
            self.show_frame("user_details_headminister")

        button_frame = Frame(container, bg="white")
        button_frame.pack(pady=20)
        Button(button_frame, text="🔙 Back", font=("Calibri", 14), bg="#e60000", fg="white", width=20, command=back_and_clear).pack(pady=5)
        Button(button_frame, text="Save & Return", font=("Calibri", 14), bg="#0073e6", fg="white", width=20, command=save_and_return).pack(pady=5)
        self.frames["update_user_details_headminister"] = frame

    def create_headminister_manage_account_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        title_bar = Frame(frame, bg="darkblue", height=60)
        title_bar.pack(fill="x")
        Label(title_bar, text="Manage User Accounts", font=("Comic Sans MS", 20, "bold"), bg="darkblue", fg="white").pack(pady=10)
        Button(frame, text="➕ Add User", font=("Calibri", 14), bg="#0073e6", fg="white", width=20, command=lambda: self.show_frame("headminister_add_user")).pack(pady=10)
        Button(frame, text="🗑 Delete User", font=("Calibri", 14), bg="#e60000", fg="white", width=20, command=lambda: self.show_frame("headminister_delete_user")).pack(pady=10)
        Button(frame, text="🔙 Back", font=("Calibri", 14), bg="#e60000", fg="white", width=20, command=lambda: self.show_frame("headminister")).pack(pady=10)
        self.frames["headminister_manage_account"] = frame

    def create_headminister_add_user_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, text="Add New User", font=("Comic Sans MS", 20, "bold"), bg="#141885", fg="white").pack(pady=20)

        Label(frame, text="New User ID:", font=("Calibri", 14), bg="#f4f4f9").pack(pady=5)
        new_user_id_input = Entry(frame, font=("Calibri", 14))
        new_user_id_input.pack(pady=5)
        Label(frame, text="New User Username:", font=("Calibri", 14), bg="#f4f4f9").pack(pady=5)
        new_username_input = Entry(frame, font=("Calibri", 14))
        new_username_input.pack(pady=5)
        Label(frame, text="New User Password:", font=("Calibri", 14), bg="#f4f4f9").pack(pady=5)
        new_password_input = Entry(frame, font=("Calibri", 14), show="*")
        new_password_input.pack(pady=5)
        add_notif = Label(frame, text="", font=("Calibri", 12), bg="#f4f4f9", fg="red")
        add_notif.pack(pady=10)

        def save_user():
            user_id = new_user_id_input.get().strip()
            newuser_username = new_username_input.get().strip()
            newuser_password = new_password_input.get().strip()
            if user_id == "" or newuser_username == "" or newuser_password == "":
                add_notif.config(text="Please fill in all fields.", fg="red")
            elif user_id in users_dict:
                add_notif.config(text="User ID already exists. Please choose a different ID.", fg="red")
            else:
                users_dict[user_id] = {
                    "username": newuser_username,
                    "password": newuser_password,
                    "balance": 0,
                    "address": "Not Provided",
                    "phonenumber": "Not Provided"
                }
                with open(USER_FILE_PATH, 'a') as file:
                    file.write(f"{user_id}:{newuser_username}:{newuser_password}:0.0|Not Provided|Not Provided\n")
                add_notif.config(text="User added successfully!", fg="green")
                frame.after(3000, lambda: add_notif.config(text=""))
                self.refresh_frames()
                self.frames["admin_delete_user"].destroy()
                self.create_admin_delete_user_frame()
                self.frames["headminister_delete_user"].destroy()
                self.create_headminister_delete_user_frame()
                self.frames["check_user_details_headminister"].destroy()
                self.frames["user_details_headminister"].destroy()
                self.create_headminister_frame()
                self.create_select_user_for_details_headminister_frame()
                self.create_headminister_user_details_frame()
                new_user_id_input.delete(0, END)
                new_username_input.delete(0, END)
                new_password_input.delete(0, END)

        Button(frame, text="Save", font=("Calibri", 14), bg="#0073e6", fg="white", command=save_user).pack(pady=10)
        Button(frame, text="Back", font=("Calibri", 14), bg="#e60000", fg="white", command=lambda: self.show_frame("headminister_manage_account")).pack(pady=5)
        self.frames["headminister_add_user"] = frame

    def create_headminister_delete_user_frame(self):
        frame = Frame(self.root, bg="#f4f4f9")
        title_bar = Frame(frame, bg="#141885", height=80)
        title_bar.pack(fill="x")
        Label(title_bar, text="Search Users to Delete", font=("Comic Sans MS", 20, "bold"), bg="#141885", fg="white").pack(pady=20)
        
        name_entry = Entry(frame, font=("Calibri", 14))
        name_entry.pack(pady=10)
        name_entry.focus()
        name_list = Listbox(frame, width=50)
        name_list.pack(pady=10)
        delete_notif = Label(frame, text="", font=("Calibri", 12), bg="#f4f4f9", fg="red")
        delete_notif.pack(pady=10)

        def update(data=None):
            name_list.delete(0, END)
            if data is None:
                data = list(users_dict.keys())
            for item in data:
                name_list.insert(END, item)

        def fillblank(event):
            name_entry.delete(0, END)
            name_entry.insert(0, name_list.get(ACTIVE))

        def check(event):
            typed = name_entry.get()
            if typed == "":
                data = list(users_dict.keys())
            else:
                data = [item for item in users_dict.keys() if typed.lower() in item.lower()]
            update(data)

        def delete_user():
            selected_user = name_list.get(ACTIVE)
            if not selected_user:
                delete_notif.config(text="No user selected!", fg="red")
                return
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {selected_user}? This action cannot be undone.")
            if not confirm:
                return
            if selected_user in users_dict:
                del users_dict[selected_user]
                with open(USER_FILE_PATH, "w") as file:
                    for user_id, user in users_dict.items():
                        file.write(f"{user_id}:{user.get('username', 'N/A')}:{user.get('password', 'N/A')}:{user.get('balance', 'Not Provided')}|{user.get('address', 'Not Provided')}|{user.get('phonenumber', 'Not Provided')}\n")
                delete_notif.config(text="User deleted successfully!", fg="green")
                frame.after(3000, lambda: delete_notif.config(text=""))
                update()
                self.refresh_frames()
                self.frames["admin_delete_user"].destroy()
                self.create_admin_delete_user_frame()
            else:
                delete_notif.config(text="User not found!", fg="red")

        Button(frame, text="Delete", font=("Calibri", 14), bg="#e60000", fg="white", command=delete_user).pack(pady=10)
        Button(frame, text="Back", font=("Calibri", 14), bg="#0073e6", fg="white", command=lambda: self.show_frame("headminister_manage_account")).pack(pady=5)
        name_list.bind("<<ListboxSelect>>", fillblank)
        name_entry.bind("<KeyRelease>", check)
        update()
        self.frames["headminister_delete_user"] = frame

# Load data
readadmin()
readuser()
readguidance()
readheadminister()


# Run application
root = Tk()
app = UniversityAidApp(root)
root.mainloop()
