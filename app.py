from flask import Flask, render_template, redirect, request, session, flash
import random
import sqlite3
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = "abc@123"

# ---------------- DB CONNECTION ----------------
def get_connection():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    return con

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('login.html')

# ---------------- REGISTER ----------------
# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        con = get_connection()
        cur = con.cursor()

        try:
            cur.execute(
                "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                (username, email, password, role)
            )
            con.commit()
            flash("Registered successfully!", "success")
            return redirect('/')

        except sqlite3.IntegrityError:
            flash("Email or Username already exists!", "danger")
            return redirect('/register')

        finally:
            con.close()

    return render_template('register.html')

# ---------------- ABOUT ----------------
@app.route('/about')
def about():
    return render_template('about.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def Login():
    username = request.form['username']
    password = request.form['password']

    con = get_connection()
    cur = con.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cur.fetchone()
    con.close()

    if user:
        session["admin"] = username
        flash("Login successful!", "success")
        return redirect("/view")
    else:
        flash("Invalid username or password", "danger")
        return redirect('/')

# ---------------- VIEW ----------------
@app.route('/view')
def View():
    if "admin" not in session:
        flash("Please login first!", "warning")
        return redirect('/')

    search = request.args.get('search')

    con = get_connection()
    cur = con.cursor()

    if search:
        cur.execute(
            "SELECT * FROM employye WHERE ename LIKE ?",
            (search + "%",)
        )
    else:
        cur.execute("SELECT * FROM employye")

    data = cur.fetchall()
    con.close()

    return render_template('view_employe.html', employyes=data)

# ---------------- ADD EMPLOYEE ----------------
@app.route('/add_employee', methods=['GET', 'POST'])
def Add_employee():
    if "admin" not in session:
        flash("Login required!", "warning")
        return redirect('/')

    if request.method == 'POST':
        data = (
            request.form['ename'],
            request.form['edept'],
            request.form['esalary'],
            request.form['ephone']
        )

        con = get_connection()
        cur = con.cursor()

        cur.execute(
            "INSERT INTO employye (ename, edept, esalary, ephone) VALUES (?, ?, ?, ?)",
            data
        )

        con.commit()
        con.close()

        flash("Employee added successfully!", "success")
        return redirect('/view')

    return render_template('add_employee.html')

# ---------------- EDIT ----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    if "admin" not in session:
        flash("Login required!", "warning")
        return redirect('/')

    con = get_connection()
    cur = con.cursor()

    if request.method == 'POST':
        ename = request.form['ename']
        edept = request.form['edept']
        esalary = request.form['esalary']
        ephone = request.form['ephone']

        cur.execute("""
            UPDATE employye 
            SET ename=?, edept=?, esalary=?, ephone=? 
            WHERE eid=?
        """, (ename, edept, esalary, ephone, id))

        con.commit()
        con.close()

        flash("Employee updated successfully!", "info")
        return redirect('/view')

    cur.execute("SELECT * FROM employye WHERE eid=?", (id,))
    data = cur.fetchone()
    con.close()

    return render_template('edit.html', emp=data)

# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete_employee(id):
    if "admin" not in session:
        flash("Login required!", "warning")
        return redirect('/')

    con = get_connection()
    cur = con.cursor()

    cur.execute("DELETE FROM employye WHERE eid=?", (id,))
    con.commit()
    con.close()

    flash("Employee deleted successfully!", "warning")
    return redirect('/view')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def Logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect('/')

# ---------------- FORGOT ----------------
otp_store = {}
sender_email = "kmahendra1891@gmail.com"
app_password = "qwzf iqbu olzm vbzr"

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form["email"]

        con = get_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cur.fetchone()
        con.close()

        if user:
            otp = random.randint(100000, 999999)
            otp_store[email] = otp

            msg = EmailMessage()
            msg.set_content(f"Your OTP is: {otp}")
            msg['Subject'] = "OTP Verification"
            msg['From'] = sender_email
            msg['To'] = email

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(sender_email, app_password)
                smtp.send_message(msg)

            session["reset_email"] = email
            flash("OTP sent!", "success")
            return redirect("/verify")

        flash("Email not found!", "danger")
        return redirect('/forgot')

    return render_template("forgot.html")

# ---------------- VERIFY ----------------
@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        user_otp = request.form["otp"]
        email = session.get("reset_email")

        if str(user_otp) == str(otp_store.get(email)):
            return redirect("/reset")
        else:
            flash("Invalid OTP!", "danger")

    return render_template("verify.html")

# ---------------- RESET ----------------
@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        new_password = request.form["password"]
        email = session.get("reset_email")

        con = get_connection()
        cur = con.cursor()
        cur.execute("UPDATE users SET password=? WHERE email=?",
                    (new_password, email))
        con.commit()
        con.close()

        flash("Password reset successful!", "success")
        return redirect('/')

    return render_template("reset.html")



# ---------------- CONTACT ----------------
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        reason = request.form.get('reason')   # ✅ FIXED HERE

        sender_email = "kmahendra1891@gmail.com"
        app_password = "qwzf iqbu olzm vbzr"
        receiver_email = "kmahendra1891@gmail.com"

        msg = EmailMessage()
        msg['Subject'] = "New Contact Form Message"
        msg['From'] = sender_email
        msg['To'] = receiver_email

        msg.set_content(f"""
Name: {name}
Phone: {phone}
Email: {email}
Reason: {reason}
""")

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(sender_email, app_password)
                smtp.send_message(msg)

            flash("Message sent successfully!", "success")
            return redirect('/contact')

        except Exception as e:
            flash("Something went wrong!", "danger")
            return redirect('/contact')

    return render_template('contact.html')

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)