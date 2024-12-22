from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector


def show_sign_up():
    root.destroy()


def on_entry(e):
    if user.get() == 'Username':
        user.delete(0, 'end')
        user.config(fg='black')


def on_password(e):
    if user.get() == '':
        user.insert(0, 'Username')
        user.config(fg='grey')


def on_enter(e):
    if code.get() == 'Password':
        code.delete(0, 'end')
        code.config(show='*', fg='black')


def on_leave(e):
    if code.get() == '':
        code.insert(0, 'Password')
        code.config(show='', fg='grey')


def check_login():
    username = user.get()
    password = code.get()

    if username == 'Username' or password == 'Password':
        messagebox.showerror("Error", "Please fill out both fields")
        return

    try:
        # Connect to the database
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="yumshare"
        )
        cursor = db.cursor()

        # Check if the user exists in the database
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (username, password))
        result = cursor.fetchone()

        if result:
            messagebox.showinfo("Success", "Login Successful")
            root.destroy()
            import MainPage
            MainPage.main_page()# Assuming the main page script is named MainPage.py
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Database error: {err}")

    finally:
        if db.is_connected():
            cursor.close()
            db.close()


root = Tk()
root.geometry("700x500+300+150")
root.title("Login System")

image_0 = Image.open('bg1.jpg')
bck_pic = ImageTk.PhotoImage(image_0.resize((700, 500)))

lbl = Label(root, image=bck_pic)
lbl.place(x=0, y=0, relwidth=1, relheight=1)

frame = Frame(root, bg='floral white')
frame.place(relx=0.5, rely=0.5, anchor=CENTER)

heading = Label(frame, text='Sign in', fg='#57a1f8', bg='floral white', font=('Calibre', 23, 'bold'))
heading.pack(pady=10)

uservalue = StringVar()
user = Entry(frame, textvariable=uservalue, width=25, fg='grey', border=1, bg='white', font=('Harrington', 11, 'bold'))
user.insert(0, 'Username')
user.bind('<FocusIn>', on_entry)
user.bind('<FocusOut>', on_password)
user.pack(pady=10)

Frame(frame, width=295, height=2, bg='black').pack(pady=5)

codevalue = StringVar()
code = Entry(frame, textvariable=codevalue, width=25, fg='grey', border=1, bg='white', font=('Harrington', 11, 'bold'))
code.insert(0, 'Password')
code.bind('<FocusIn>', on_enter)
code.bind('<FocusOut>', on_leave)
code.pack(pady=10)

Frame(frame, width=295, height=2, bg='black').pack(pady=5)

Button(frame, width=30, pady=7, text='Sign in', bg='#57a1f8', fg='white', cursor='hand2', border=0,
       command=check_login).pack(pady=20)

label = Label(frame, text="Don't have an account?", fg='black', bg='floral white', cursor='hand2', font=('Calibre', 9))
label.pack(side=LEFT, padx=10)

sign_up = Button(frame, width=6, text='Sign up', border=0, bg='floral white', cursor='hand2', fg='#57a1f8',
                 command=show_sign_up)
sign_up.pack(side=RIGHT, padx=10)

root.mainloop()