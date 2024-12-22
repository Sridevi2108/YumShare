from tkinter import *
from tkinter import messagebox
import re
from PIL import Image, ImageTk
import mysql.connector

def show_login():
    root.destroy()
    import Login  # Assuming the login script is named login_script.py

def sign_up():
    name = entry_name.get()
    email = entry_email.get()
    password = entry_password.get()
    phone = entry_phone.get()

    if not name or not email or not password or not phone:
        messagebox.showerror("Error", "All fields are required")
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        messagebox.showerror("Error", "Invalid email address")
    else:
        try:
            # Connect to the database
            db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="password",
                database="yumshare"
            )
            cursor = db.cursor()

            # Insert user data into the database
            cursor.execute("INSERT INTO users (name, email, password, phone) VALUES (%s, %s, %s, %s)",
                           (name, email, password, phone))
            db.commit()

            messagebox.showinfo("Success", "Sign Up Successful")
            entry_name.delete(0, END)
            entry_email.delete(0, END)
            entry_password.delete(0, END)
            entry_phone.delete(0, END)
            show_login()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")
        finally:
            if db.is_connected():
                cursor.close()
                db.close()

# Window
root = Tk()
root.geometry("700x500+300+150")
root.title("Sign Up")

# Background
image_0 = Image.open('bg1.jpg')
bck_pic = ImageTk.PhotoImage(image_0.resize((700, 500)))

lbl = Label(root, image=bck_pic)
lbl.place(x=0, y=0, relwidth=1, relheight=1)

frame = Frame(root, bg='floral white')
frame.place(relx=0.5, rely=0.5, anchor=CENTER)

heading = Label(frame, text='Sign up', fg='#57a1f8', bg='floral white', font=('Calibre', 23, 'bold'))
heading.pack(pady=10)

# Name entry
label_name = Label(frame, text="Name", font=('Helvetica', 12), bg='floral white')
label_name.pack(pady=5)
entry_name = Entry(frame, font=('Helvetica', 12))
entry_name.pack(pady=5)

# Email entry
label_email = Label(frame, text="Email", font=('Helvetica', 12), bg='floral white')
label_email.pack(pady=5)
entry_email = Entry(frame, font=('Helvetica', 12))
entry_email.pack(pady=5)

# Password entry
label_password = Label(frame, text="Password", font=('Helvetica', 12), bg='floral white')
label_password.pack(pady=5)
entry_password = Entry(frame, font=('Helvetica', 12), show='*')
entry_password.pack(pady=5)

# Phone number entry
label_phone = Label(frame, text="Phone Number", font=('Helvetica', 12), bg='floral white')
label_phone.pack(pady=5)
entry_phone = Entry(frame, font=('Helvetica', 12))
entry_phone.pack(pady=5)

# Sign Up button
button_sign_up = Button(frame, text="Sign Up", font=('Helvetica', 12), command=sign_up)
button_sign_up.pack(pady=20)

# Login button
Login = Button(frame, width=6, text='Login', border=0, bg='floral white', cursor='hand2', fg='#57a1f8', command=show_login)
Login.pack(side=RIGHT, padx=10)

root.mainloop()