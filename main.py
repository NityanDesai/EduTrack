from cgitb import reset
from distutils.command.config import config
from distutils.command.install_egg_info import safe_name
from email import message_from_string
from multiprocessing.sharedctypes import Value
from optparse import Values
from tracemalloc import start
from unittest import result
from xml.etree.ElementTree import tostring
from flask import Flask, render_template, request, session, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import random, string, json, time, requests, datetime, calendarific, calendar, time, timedelta, cryptocode

# Using CONFIG file 
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True

# Flask modules setup 
app = Flask(__name__)

# Email sending setup
app.secret_key = 'super-secret-key'
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params["gmail-user"],
    MAIL_PASSWORD = params["gmail-password"]
)
mail = Mail(app)

# Database connectivity
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Encryption/Decryption
passKey = params["passKey"]
# Method to generate new passwords 
def generatePasswords():
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(8))
    return result_str

# Users table table 
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subjects = db.Column(db.JSON, nullable=True)
    salary = db.Column(db.Integer, nullable=False)
    is_superuser = db.Column(db.Integer, nullable=True)
    sl = db.Column(db.Integer, nullable=False)
    cl = db.Column(db.Integer, nullable=False)
    el = db.Column(db.Integer, nullable=False)

# Subjects table class 
class Subjects(db.Model):
    subject_id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(80), unique=False, nullable=False)
    stream_id = db.Column(db.Integer, nullable=False)
    sem = db.Column(db.Integer, nullable=False)

# Stream table class
class Stream(db.Model):
    stream_id = db.Column(db.Integer, primary_key=True)
    stream = db.Column(db.String(80), unique=False, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    course = db.Column(db.String(80), unique=False, nullable=False)
    fees = db.Column(db.Integer, nullable=False)

# Leave table class
class Leaves(db.Model):
    leave_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(100), unique=False, nullable=False)
    leavetype = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.String(80), unique=False, nullable=False)
    end_date = db.Column(db.String(80), unique=False, nullable=False)
    no_of_leaves = db.Column(db.Integer, nullable=False)
    display = db.Column(db.Integer, nullable=False)

# Parents table class    
class Parents(db.Model):
    p_id = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.String(80), unique=True, nullable=False)
    s_name = db.Column(db.String(80), unique=False, nullable=False)
    p_name = db.Column(db.String(80), unique=False, nullable=False)
    s_email = db.Column(db.String(120), nullable=False)
    s_password = db.Column(db.String(80), nullable=False)
    p_email = db.Column(db.String(120), nullable=False)
    p_password = db.Column(db.String(80), nullable=False)
    stream_id = db.Column(db.Integer, nullable=False)
    sem = db.Column(db.Integer, nullable=False)
    attend_ind = db.Column(db.Integer, nullable=False)
    leave_bal = db.Column(db.Integer, nullable=False)
    fee_status = db.Column(db.Integer, nullable=False)
    
# Student leaves table class
class Studentleave(db.Model):
    leave_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, nullable=False)
    from_date = db.Column(db.String(80), unique=False, nullable=False)
    to_date = db.Column(db.String(80), unique=False, nullable=False)
    no_of_days = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(100), unique=False, nullable=False)
    
# Exams table class 
class Exams(db.Model):
    test_id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(80), unique=False, nullable=False)
    date = db.Column(db.String(80), unique=False, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    stream_id = db.Column(db.Integer, nullable=False)
    sem = db.Column(db.Integer, nullable=False)

# Results table class 
class Results(db.Model):
    result_id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, nullable=False)
    s_id = db.Column(db.Integer, nullable=False)
    given_marks = db.Column(db.Integer, nullable=False)
    
# Remarks table class     
class Remarks(db.Model):
    r_id = db.Column(db.Integer, primary_key=True)
    remarks = db.Column(db.String(80), nullable=False)
    s_id = db.Column(db.Integer, nullable=False)

# Updates table class 
class Updates(db.Model):
    update_id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, nullable=False)
    note_updates = db.Column(db.String(100), nullable=False)
    
# Username and passwords
admin_pass, admin_uname, fac_pass, fac_uname, par_email, par_pass, stu_email, stu_pass  = {}, {}, {}, {}, {}, {}, {}, {}
all_fac = Users.query.all()
all_par = Parents.query.all()
for fac in all_fac:
    if fac.is_superuser == 1:
        admin_uname[fac.username] = fac.password
    elif fac.is_superuser == 0:
        fac_uname[fac.username] = fac.password
for par in all_par:
    par_email[par.p_email] = par.p_password
for stu in all_par:
    stu_email[stu.s_email] = stu.s_password
    
# Leaves reset     
while(datetime.datetime.now().month == 1 and  datetime.datetime.now().day == 1):
    all_fac = Users.query.all()
    for fac in all_fac:
        fac.sl = params["default_sl"]
        fac.cl = params["default_cl"]
        fac.el = fac.el + params["default_el"]
    db.session.commit()
    break

while(datetime.datetime.now().month == 1 and  datetime.datetime.now().day == 1):
    all_leaves = Leaves.query.all()
    for leave in all_leaves:
        if (leave.end_date.year == (datetime.datetime.now().year - 1)) and (leave.display == 0):
            Leaves.query.filter_by(leave_id=leave.leave_id).delete()
    db.session.commit()
    break

while(datetime.datetime.now().month == 1 or datetime.datetime.now().month == 6 and  datetime.datetime.now().day == 1):
    all_pars = Parents.query.all()
    for par in all_pars:
        par.fee_status = par.fee_status + 1
    db.session.commit()
    break

# 404 page not found exception handling 
@app.errorhandler(404)
def not_found(e):
    flash("404! Page not found, redirecting to home...", "danger")
    return render_template("404.html")


# LOGIN Module 
@app.route("/", methods = ["GET", "POST"])
def login():
    if "admin" in session and session['admin'] in admin_uname:
        return redirect(request.args.get("next") or "/admin_dash")
    
    if "user" in session and session['user'] in fac_uname:
        return redirect(request.args.get("next") or "/faculty_dash")
    
    if "parent" in session and session['parent'] in par_email:
        return redirect(request.args.get("next") or "/parent_dash")
    
    if "student" in session and session['student'] in stu_email:
        return redirect(request.args.get("next") or "/student_dash")

    if request.method=="POST":
        username = request.form.get("uname")
        userpass = request.form.get("upass")
        if username in admin_uname.keys() and (admin_uname[username] == userpass or cryptocode.decrypt(admin_uname[username], passKey) == userpass):
            # set the session variable for admin
            session['admin'] = username
            return redirect(request.args.get("next") or "/admin_dash")
        elif username in fac_uname.keys() and (fac_uname[username] == userpass or cryptocode.decrypt(fac_uname[username], passKey) == userpass):
            # set the session variable for faculty
            session['user'] = username
            return redirect(request.args.get("next") or "/faculty_dash")
        elif username in par_email.keys() and (par_email[username] == userpass or cryptocode.decrypt(par_email[username], passKey) == userpass):
            # set the session variable for parent
            session['parent'] = username
            return redirect(request.args.get("next") or "/parent_dash")
        elif username in stu_email.keys() and (stu_email[username] == userpass or cryptocode.decrypt(stu_email[username], passKey) == userpass):
            # set the session variable for parent
            session['student'] = username
            return redirect(request.args.get("next") or "/student_dash")
        else:
            flash("Wrong username or password!", "danger")
            return render_template("login.html")
    else:
        return render_template("login.html")

# LOGOUT Module 
@app.route("/logout")
def logout():
    if "admin" in session:
        session.pop("admin")
    elif "user" in session:
        session.pop("user")
    elif "parent" in session:
        session.pop("parent")
    elif "student" in session:
        session.pop("student")
    flash("You were logged out successfully.", "success")
    return redirect("/")

# Admin's Dashboard 
@app.route("/admin_dash", methods = ["GET", "POST"])
def admin_dash():
    if "admin" in session and session['admin'] in admin_uname:
        all_fac = Users.query.all()
        subs = Subjects.query.all()
        sts = Stream.query.all()
        students = Parents.query.all()
        admin = session['admin']
        return render_template("index.html", len_fac=len(all_fac), all_fac=all_fac, len_sub=len(subs), subs=subs, len_st = len(sts), sts=sts, len_students = len(students), students = students, admin=admin)
    else:
        return redirect("/")

# Faculty's Dashboard 
@app.route("/faculty_dash", methods = ["GET", "POST"])
def faculty_dash():
    if "user" in session and session['user'] in fac_uname:
        username = session['user']
        fac = Users.query.filter_by(username=username).first()
        subs = Subjects.query.all()
        sts = Stream.query.all()
        return render_template("dashboard.html", fac=fac, len_sub=len(fac.subjects["subjects"]), subs=subs, sts=sts)
    else:
        return redirect("/")

# Parent's Dashboard     
@app.route("/parent_dash", methods = ["GET", "POST"])
def parent_dash():
    if "parent" in session and session['parent'] in par_email:
        p_email = session['parent']
        par = Parents.query.filter_by(p_email=p_email).first()
        if datetime.time(1, 0, 0, 0) < datetime.datetime.now().time() < datetime.time(8, 0, 0, 0) or datetime.datetime.today().weekday() in [2, 1]:
            par.attend_ind = 0
            db.session.commit()
        subs = Subjects.query.all()
        sts = Stream.query.all()
        return render_template("parent_dash.html", par=par, len_sub=len(fac.subjects["subjects"]), subs=subs, sts=sts)
    else:
        return redirect("/")

# Student's Dashboard     
@app.route("/student_dash", methods = ["GET", "POST"])
def student_dash():
    if "student" in session and session['student'] in stu_email:
        s_email = session['student']
        par = Parents.query.filter_by(s_email=s_email).first()
        subs = Subjects.query.all()
        len_sub = 0
        sublist = []
        for sub in subs:
            if par.stream_id == sub.stream_id and par.sem == sub.sem:
                sublist.append(sub.subject_id)
                len_sub = len(sublist)
        sts = Stream.query.all()
        return render_template("student_dash.html", par=par, len_sub=len_sub, subs=subs, sts=sts)
    else:
        return redirect("/")

# Student's Faculty details page     
@app.route("/faculties_details", methods = ["GET", "POST"])
def faculties_details():
    if "student" in session and session['student'] in stu_email:
        s_email = session['student']
        par = Parents.query.filter_by(s_email=s_email).first()
        subs = Subjects.query.all()
        all_facs = Users.query.all()
        len_sub = 0
        len_fac = 0
        facs = []
        facsdict = {}
        sublist = []
        for sub in subs:
            if par.stream_id == sub.stream_id and par.sem == sub.sem:
                sublist.append(sub.subject_id)
                len_sub = len(sublist)
                for fac in all_facs:
                    for key, value in fac.subjects.items():
                        if sub.subject_id in value:
                            facsdict[fac.id] = sub.subject_id
        facs = [(k, facsdict[k]) for k in facsdict]
        len_fac = len(facs)
        return render_template("faculties_details.html", par=par, len_sub=len_sub, len_fac=len_fac, subs=subs, facs=facs, all_facs=all_facs)
    else:
        return redirect("/")

# Parent's Faculty details page     
@app.route("/faculty_details", methods = ["GET", "POST"])
def faculty_details():
    if "parent" in session and session['parent'] in par_email:
        p_email = session['parent']
        par = Parents.query.filter_by(p_email=p_email).first()
        subs = Subjects.query.all()
        all_facs = Users.query.all()
        len_sub = 0
        facs = []
        facsdict = {}
        sublist = []
        for sub in subs:
            if par.stream_id == sub.stream_id and par.sem == sub.sem:
                sublist.append(sub.subject_id)
                len_sub = len(sublist)
                for fac in all_facs:
                    for key, value in fac.subjects.items():
                        if sub.subject_id in value:
                            facsdict[fac.id] = sub.subject_id
        facs = [(k, facsdict[k]) for k in facsdict]
        len_fac = len(facs)
        return render_template("faculty_details.html", par=par, len_sub=len_sub, len_fac=len_fac, subs=subs, facs=facs, all_facs=all_facs)
    else:
        return redirect("/")

# Faculty's list of students     
@app.route("/students", methods = ["GET", "POST"])
def students():
    if "user" in session and session['user'] in fac_uname:
        f_uname = session['user']
        fac = Users.query.filter_by(username=f_uname).first()
        subs = Subjects.query.all()
        all_pars = Parents.query.all()
        pars = []
        parsdict = {}
        for sub in subs:
            if sub.subject_id in fac.subjects["subjects"]:
                for par in all_pars:
                    if par.stream_id == sub.stream_id and par.sem == sub.sem:
                        parsdict[sub.subject_id] = par.p_id
        pars = [(k, parsdict[k]) for k in parsdict]
        len_par = len(pars)
        return render_template("student_list.html", len_par=len_par, subs=subs, pars=pars, fac=fac, all_pars=all_pars)
    else:
        return redirect("/")

# Presence    
@app.route("/present", methods = ["GET", "POST"])
def present():
    if "user" in session and session['user'] in fac_uname:
        f_uname = session['user']
        fac = Users.query.filter_by(username=f_uname).first()
        subs = Subjects.query.all()
        all_pars = Parents.query.all()
        pars = []
        parsdict = {}
        for sub in subs:
            if sub.subject_id in fac.subjects["subjects"]:
                for par in all_pars:
                    if par.stream_id == sub.stream_id and par.sem == sub.sem:
                        parsdict[sub.subject_id] = par.p_id
        pars = [(k, parsdict[k]) for k in parsdict]
        len_par = len(pars)
        if(request.method == 'POST'):
            attend = request.form.get('attend')
            stu = Parents.query.filter_by(p_id=attend).first()
            if stu.leave_bal > 0:
                stu.attend_ind = 2
                db.session.commit()
            return redirect("/students")
        return render_template("student_list.html", len_par=len_par, subs=subs, pars=pars, fac=fac, all_pars=all_pars)
    else:
        return redirect("/")

# Absence  
@app.route("/absent", methods = ["GET", "POST"])
def absent():
    if "user" in session and session['user'] in fac_uname:
        f_uname = session['user']
        fac = Users.query.filter_by(username=f_uname).first()
        subs = Subjects.query.all()
        all_pars = Parents.query.all()
        pars = []
        parsdict = {}
        for sub in subs:
            if sub.subject_id in fac.subjects["subjects"]:
                for par in all_pars:
                    if par.stream_id == sub.stream_id and par.sem == sub.sem:
                        parsdict[sub.subject_id] = par.p_id
        pars = [(k, parsdict[k]) for k in parsdict]
        len_par = len(pars)
        if(request.method == 'POST'):
            attend = request.form.get('attend')
            stu = Parents.query.filter_by(p_id=attend).first()
            if stu.leave_bal > 0:
                stu.attend_ind = 1
                stu.leave_bal = stu.leave_bal - 1
                db.session.commit()
            return redirect("/students")
        return render_template("student_list.html", len_par=len_par, subs=subs, pars=pars, fac=fac, all_pars=all_pars)
    else:
        return redirect("/")


# Edit Faculty page 
@app.route("/edit_faculty/<int:pk>", methods = ["GET", "POST"])
def edit_faculty(pk):
    if "admin" in session and session['admin'] in admin_uname:
        admin = session['admin']
        fac = Users.query.filter_by(id=pk).first()
        subs = Subjects.query.all()
        if(request.method == 'POST'):
            name = request.form.get('name')
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            salary = request.form.get('salary')
            subjects = request.form.getlist('subject')
            subjects = map(int, subjects)
            subjects = list(subjects)
            subjects = json.dumps(subjects)
            subjects = json.loads('{"subjects":' + subjects +"}")
            if(email != fac.email and email != "" and email != None and email != " "):
                fac.email = email
                message = "Your email id was changed. This is your new registered email id. Your credentials are:\nUsername: " + fac.username + "\nPassword: " + fac.password
                print(message)
                # mail.send_message("This is your new official email id registered with your college.", 
                #             sender = params['gmail-user'], 
                #             recipients=[email],
                #             body = message
                #         )
            fac.name = name
            if salary != None:
                fac.salary = salary
            if(username != "" and username != " " and username != None and username != fac.username):
                fac.username = username
                message = "Your username was changed. Your new credentials are:\nUsername: " + username + "\nPassword: " + password
                print(message)
                # mail.send_message("This is your new username to your college.", 
                #                 sender = params['gmail-user'], 
                #                 recipients=[email],
                #                 body = message
                #             )
                flash("Username/Password was changed. Please logout & relogin after 10 mins.", "warning")
            if(password != "" and password != " " and password != None and password != fac.username):
                fac.password = cryptocode.encrypt(password, passKey)
                message = "Your password was changed. Your new credentials are:\nUsername: " + username + "\nPassword: " + password
                print(message)
                # mail.send_message("This is your new password to your college.",
                #                 sender = params["gmail-user"], 
                #                 recipients=[email],
                #                 body = message
                #             )
                flash("Username/Password was changed. Please logout & relogin after 10 mins.", "warning")
            if subjects != None:
                fac.subjects = subjects
            db.session.commit()
            flash("Details were successfully updated.", "success")
            return redirect("/faculties")
        return render_template("edit_faculty.html", fac=fac, subs=subs, admin=admin, admin_uname=admin_uname)
    elif "user" in session and session['user'] in fac_uname:
        user = session['user']
        fac = Users.query.filter_by(id=pk).first()
        subs = Subjects.query.all()
        if(request.method == 'POST'):
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            if(email != fac.email and email != None and email != "" and email != " "):
                fac.email = email
                message = "Your email id was changed. This is your new official email id."
                print(message)
                # mail.send_message("This is your new official email id registered with your college.", 
                #             sender = params['gmail-user'], 
                #             recipients=[email],
                #             body = message
                #         )
            if(username != "" and username != " " and username != None and username != fac.username):
                fac.username = username
                message = "Your username was changed. Your new credentials are:\nUsername: " + username + "\nPassword: " + password
                print(message)
                # mail.send_message("This is your new username to your college.", 
                #             sender = params['gmail-user'], 
                #             recipients=[email],
                #             body = message
                #         )
                flash("Username/Password was changed. Please logout & relogin after 10 mins.", "warning")
            if (password != "" and password != " " and password != None and password != fac.username):
                fac.password = password
                message = "Your password was changed. Your credentials are:\nUsername: " + username + "\nPassword: " + fac.password
                print(message)
                # mail.send_message("This is your new password to your college.", 
                #             sender = params['gmail-user'], 
                #             recipients=[email],
                #             body = message
                #         )
                flash("Username/Password was changed. Please logout & relogin after 10 mins.", "warning")
            db.session.commit()
            flash("Details were successfully updated.", "success")
            return redirect("/faculties")
        return render_template("edit_faculty.html", fac=fac, subs=subs, user=user)
    else:
        return redirect("/")

# Edit Parent page 
@app.route("/edit_parent/<int:pk>", methods = ["GET", "POST"])
def edit_parent(pk):
    if "admin" in session and session['admin'] in admin_uname:
        admin = session['admin']
        par = Parents.query.filter_by(p_id=pk).first()
        sts = Stream.query.all()
        if(request.method == 'POST'):
            p_name = request.form.get('p_name')
            s_name = request.form.get('s_name')
            p_email = request.form.get('p_email')
            s_email = request.form.get('s_email')
            stream_id = request.form.get('stream_id')
            sem = request.form.get('sem')
            if(p_email != par.p_email and p_email != "" and p_email != None and p_email != " "):
                par.p_email = p_email
                message = "Your email id was changed. This is your new registered email id. Your credentials are:\nUsername: " + p_email + "\nPassword: " + par.p_password
                print(message)
                # mail.send_message("This is your new official email id registered with your college.", 
                #             sender = params['gmail-user'], 
                #             recipients=[p_email],
                #             body = message
                #         )
            if(s_email != par.s_email and s_email != "" and s_email != None and s_email != " "):
                par.s_email = s_email
                message = "Your email id was changed. This is your new registered email id. Your credentials are:\nUsername: " + s_email + "\nPassword: " + par.s_password
                print(message)
                # mail.send_message("This is your new official email id registered with your college.", 
                #             sender = params['gmail-user'], 
                #             recipients=[s_email],
                #             body = message
                #         )
            par.p_name = p_name
            par.s_name = s_name
            if stream_id != None or stream_id != 0:
                par.stream_id = stream_id
            par.sem = sem
            db.session.commit()
            flash("Details were successfully updated.", "success")
            return redirect("/student")
        return render_template("edit_parent.html", par=par, sts=sts, admin=admin, admin_uname=admin_uname)
    elif "parent" in session and session['parent'] in par_email:
        parent = session['parent']
        par = Parents.query.filter_by(p_id=pk).first()
        if(request.method == 'POST'):
            p_password = request.form.get('p_password')
            p_email = request.form.get('p_email')
            if(p_email != par.p_email and p_email != None and p_email != "" and p_email != " "):
                par.p_email = p_email
                message = "Your email id was changed. This is your new official email id."
                print(message)
                # mail.send_message("This is your new official email id registered with your college.", 
                #             sender = params['gmail-user'], 
                #             recipients=[p_email],
                #             body = message
                #         )
                flash("Email ID was changed. Please logout & relogin after 10 mins.", "warning")
            if (p_password != "" and p_password != " " and p_password != None and p_password != par.p_password):
                par.p_password = cryptocode.encrypt(p_password, passKey)
                message = "Your password was changed. Your credentials are:\nUsername: " + p_email + "\nPassword: " + p_password
                print(message)
                # mail.send_message("This is your new password to your college.", 
                #             sender = params['gmail-user'], 
                #             recipients=[p_email],
                #             body = message
                #         )
                flash("Password was changed. Please logout & relogin after 10 mins.", "warning")
            db.session.commit()
            flash("Details were successfully updated.", "success")
            return redirect("/logout")
        return render_template("edit_parent.html", par=par, parent=parent)
    elif "student" in session and session['student'] in stu_email:
        student = session['student']
        par = Parents.query.filter_by(p_id=pk).first()
        if(request.method == 'POST'):
            s_password = request.form.get('s_password')
            if (s_password != "" and s_password != " " and s_password != None and s_password != par.s_password):
                par.s_password = cryptocode.encrypt(s_password, passKey)
                message = "Your password was changed. Your credentials are:\nUsername: " + par.s_email + "\nPassword: " + s_password
                print(message)
                # mail.send_message("This is your new password to your college.", 
                #             sender = params['gmail-user'], 
                #             recipients=[s_email],
                #             body = message
                #         )
                flash("Password was changed. Please logout & relogin after 10 mins.", "warning")
            db.session.commit()
            flash("Details were successfully updated.", "success")
            return redirect("/student_dash")
        return render_template("edit_parent.html", par=par, student=student)
    else:
        return redirect("/")

# Delete faculty 
@app.route("/delete_faculty/<int:pk>")
def delete_faculty(pk):
    if "admin" in session and session['admin'] in admin_uname:
        fac = Users.query.filter_by(id=pk).first()
        db.session.delete(fac)
        db.session.commit()
        flash("Details were successfully deleted.", "success")
        return redirect("/faculties")
    else:
        return redirect("/")

# Edit Subject 
@app.route("/edit_subject/<int:pk>", methods = ["GET", "POST"])
def edit_subject(pk):
    if "admin" in session and session['admin'] in admin_uname:
        sub = Subjects.query.filter_by(subject_id=pk).first()
        sts = Stream.query.all()
        if(request.method == 'POST'):
            subject = request.form.get('subject')
            stream_id = request.form.get('stream_id')
            sem = request.form.get('sem')
            sub.subject = subject
            sub.stream_id = stream_id
            sub.sem = sem
            db.session.commit()
            flash("Details were successfully updated.", "success")
            return redirect("/subjects")
        return render_template("edit_subject.html", sub=sub, sts=sts)
    else:
        return redirect("/")

# Delete Subject
@app.route("/delete_subject/<int:pk>")
def delete_subject(pk):
    if "admin" in session and session['admin'] in admin_uname:
        sub = Subjects.query.filter_by(subject_id=pk).first()
        db.session.delete(sub)
        db.session.commit()
        flash("Details were successfully deleted.", "success")
        return redirect("/subjects")
    else:
        return redirect("/")

# Edit Stream 
@app.route("/edit_stream/<int:pk>", methods = ["GET", "POST"])
def edit_stream(pk):
    if "admin" in session and session['admin'] in admin_uname:
        st = Stream.query.filter_by(stream_id=pk).first()
        if(request.method == 'POST'):
            stream = request.form.get('stream')
            course = request.form.get('course')
            duration = request.form.get('duration')
            fees = request.form.get('fees')
            st.stream = stream
            st.course = course
            st.duration = duration
            st.fees = fees
            db.session.commit()
            flash("Details were successfully updated.", "success")
            return redirect("/stream")
        return render_template("edit_stream.html", st=st)
    else:
        return redirect("/")

# Delete stream 
@app.route("/delete_stream/<int:pk>")
def delete_stream(pk):
    if "admin" in session and session['admin'] in admin_uname:
        st = Stream.query.filter_by(stream_id=pk).first()
        db.session.delete(st)
        db.session.commit()
        flash("Details were successfully deleted.", "success")
        return redirect("/stream")
    else:
        return redirect("/")

# Delete student 
@app.route("/delete_parent/<int:pk>")
def delete_parent(pk):
    if "admin" in session and session['admin'] in admin_uname:
        par = Parents.query.filter_by(p_id=pk).first()
        db.session.delete(par)
        db.session.commit()
        flash("Details were successfully deleted.", "success")
        return redirect("/student")
    else:
        return redirect("/")

# Delete exam
@app.route("/delete_exam/<int:pk>")
def delete_exam(pk):
    if "admin" in session and session['admin'] in admin_uname:
        exms = Exams.query.filter_by(test_id=pk).first()
        db.session.delete(exms)
        db.session.commit()
        flash("Details were successfully deleted.", "success")
        return redirect("/exams")
    else:
        return redirect("/")

# Fees paaid request to check and clear 
@app.route("/fee_pay_req/<int:pk>")
def fee_pay_req(pk):
    if "parent" in session and session['parent'] in par_email:
        par = Parents.query.filter_by(p_id=pk).first()
        message = f"Hi Admin, \n\nI have paid fees for {par.s_name} who's Roll no is {par.rollno}. \n\nCould you please check and mark the payment as done from your side.\n\n{par.p_name}\n\nParent."
        print(message)
        # mail.send_message("Payment was made, request to check.", 
        #                     sender = [p_email], 
        #                     recipients=params['gmail-user'],
        #                     body = message
        #                 )
        flash("Request for checking is sent. I t will be reflected below once request is processed.", "success")
        return redirect("/parent_dash")
    else:
        return redirect("/")

# Fees paid request to check and clear 
@app.route("/fee_paid/<int:pk>")
def fee_paid(pk):
    if "admin" in session and session['admin'] in admin_uname:
        par = Parents.query.filter_by(p_id=pk).first()
        par.fee_status = par.fee_status - 1
        db.session.commit()
        message = f"Hi {par.p_name}, \n\nI have checked and could confirm fees were received for {par.s_name} who's Roll no is {par.rollno}.\n\nAdmin."
        print(message)
        # mail.send_message("Payment was successful.", 
        #                     sender = params['gmail-user'], 
        #                     recipients=[p_email],
        #                     body = message
        #                 )
        flash("Payment was marked as received.", "success")
        return redirect("/parent_dash")
    else:
        return redirect("/")

# Faculty details page for Admin 
@app.route("/faculties")
def faculties():
    if "admin" in session and session['admin'] in admin_uname:
        all_fac = Users.query.filter(Users.is_superuser==0).all()
        subs = Subjects.query.all()
        sts = Stream.query.all()
        return render_template("faculties.html", all_fac=all_fac, subs=subs, sts=sts)
    else:
        return redirect("/")

# Students details page for Admin 
@app.route("/student")
def student():
    if "admin" in session and session['admin'] in admin_uname:
        all_pars = Parents.query.all()
        sts = Stream.query.all()
        return render_template("students.html", all_pars=all_pars, sts=sts)
    else:
        return redirect("/")

# Add Faculty page 
@app.route("/add_f", methods = ["GET", "POST"])
def add_f():
    if "admin" in session and session['admin'] in admin_uname:
        subs = Subjects.query.all()
        sts = Stream.query.all()
        if(request.method == 'POST'):
            name = request.form.get('name')
            email = request.form.get('email')
            subjects = request.form.getlist('subject')
            username = str(name.split()[0]) + str(random.randint(0,999))
            password = str(generatePasswords())
            is_superuser = 0
            subjects = map(int, subjects)
            subjects = list(subjects)
            subjects = json.dumps(subjects)
            subjects = json.loads('{"subjects":' + subjects +"}")
            salary = request.form.get('salary')
            sl = params['default_sl']
            cl = params['default_cl']
            el = params['default_el']
            entry = Users(name=name, username=username, password=password, email=email, subjects=subjects, salary=salary, is_superuser=is_superuser, sl=sl, cl=cl, el=el)
            db.session.add(entry)
            db.session.commit()
            message = "You were added as a faculty. Your credentials are:\nUsername: " + username + "\nPassword: " + password + "\nPlease change the password when you first login."
            print(message)
            # mail.send_message("Your college has added you as a faculty.", 
            #                     sender = params['gmail-user'], 
            #                     recipients=[email],
            #                     body = message
            #                 )
            flash("Details were successfully added.", "success")
            return redirect("/add_f")
        return render_template("setting.html", subs=subs, sts=sts)
    else:
        return redirect("/")

# Add Student page
@app.route("/add_stu", methods = ["GET", "POST"])
def add_stu():
    if "admin" in session and session['admin'] in admin_uname:
        subs = Subjects.query.all()
        sts = Stream.query.all()
        if(request.method == 'POST'):
            sname = request.form.get('sname')
            rollno = "IGNUVAD" + str(datetime.date.today().year) + (str(sname.split()[0])).upper() + str(random.randrange(999))
            semail = request.form.get('semail')
            pname = request.form.get('pname')
            pemail = request.form.get('pemail')
            stream = request.form.get('stream')
            s_password = str(generatePasswords())
            p_password = str(generatePasswords())
            sem = request.form.get('sem')
            attend_ind = 0
            leave_bal = params["leave_bal"]
            entry = Parents(rollno=rollno, s_name=sname, p_name=pname, s_password=s_password, p_password=p_password, s_email=semail, p_email=pemail, stream_id=stream, sem=sem, attend_ind=attend_ind, leave_bal=leave_bal)
            db.session.add(entry)
            db.session.commit()
            message = "Student profile is created on EduTrack portal. Your credentials are:\nUsername: Your email id\nPassword: " + s_password + "\nPlease change the password when you first login."
            print(message)
            # mail.send_message("Your admission in the college was successful.", 
            #                     sender = params['gmail-user'], 
            #                     recipients=[semail],
            #                     body = message
            #                 )
            # message = "Parent profile is created on EduTrack portal. Your credentials are:\nUsername: Your email id\nPassword: " + p_password + "\nPlease change the password when you first login."
            # mail.send_message(sname + " was admitted in the college.", 
            #                     sender = params['gmail-user'], 
            #                     recipients=[pemail],
            #                     body = message
            #                 )
            flash("Details were successfully added.", "success")
            return redirect("/add_stu")
        return render_template("setting.html", subs=subs, sts=sts)
    else:
        return redirect("/")

# Add subjects 
@app.route("/add_s", methods = ["GET", "POST"])
def add_s():
    if "admin" in session and session['admin'] in admin_uname:
        sts = Stream.query.all()
        if(request.method == 'POST'):
            subject = request.form.get('subject')
            sem = request.form.get('sem')
            stream = request.form.get('stream')
            fees = request.form.get('fees')
            duration = 0
            for st in sts:
                if st.stream_id == int(stream):
                    duration = int(st.duration)
            if int(sem) > duration:
                flash("Semester should be less than duration of the stream selected.", "warning")
            else:
                entry = Subjects(subject=subject, stream_id=stream, sem=sem, fees=fees)
                db.session.add(entry)
                db.session.commit()
                flash("Details were successfully added.", "success")
            return redirect("/add_s")
        return render_template("profile.html", sts=sts)
    else:
        return redirect("/")

# Add Exams 
@app.route("/add_e", methods = ["GET", "POST"])
def add_e():
    if "admin" in session and session['admin'] in admin_uname:
        sts = Stream.query.all()
        if(request.method == 'POST'):
            test_name = request.form.get('test_name')
            sem = request.form.get('sem')
            date = request.form.get('date')
            stream = request.form.get('stream')
            total_marks = request.form.get('total_marks')
            for st in sts:
                if st.stream_id == int(stream):
                    duration = int(st.duration)
            if int(sem) > duration:
                flash("Semester should be less than duration of the stream selected.", "warning")
                return redirect("/add_e")
            else:
                entry = Exams(test_name=test_name, date=date, stream_id=stream, sem=sem, total_marks=total_marks)
                db.session.add(entry)
                db.session.commit()
                flash("Details were successfully added.", "success")
            return redirect("/exams")
        return render_template("add_e.html", sts=sts)
    else:
        return redirect("/")

# Add streams 
@app.route("/add_st", methods = ["POST"])
def add_st():
    if "admin" in session and session['admin'] in admin_uname:
        if(request.method == 'POST'):
            stream = request.form.get('stream')
            duration = request.form.get('duration')
            course = request.form.get('course')
            entry = Stream(stream=stream, duration=duration, course=course)
            db.session.add(entry)
            db.session.commit()
            flash("Details were successfully added.", "success")
            return redirect("/add_s")
    else:
        return redirect("/")

# Subjects details page 
@app.route("/subjects")
def subjects():
    if "admin" in session and session['admin'] in admin_uname:
        subs = Subjects.query.all()
        sts = Stream.query.all()
        return render_template("subjects.html", subs=subs, sts=sts)
    else:
        return redirect("/")

# Subjects details page 
@app.route("/exams")
def exams():
    exs = Exams.query.all()
    sts = Stream.query.all()
    if "admin" in session and session['admin'] in admin_uname:
        return render_template("exams.html", exs=exs, sts=sts)
    elif "parent" in session and session['parent'] in par_email:
        par = Parents.query.filter_by(p_email=session['parent']).first()    
        return render_template("exam.html", exs=exs, sts=sts, par=par)
    elif "student" in session and session['student'] in stu_email:
        par = Parents.query.filter_by(s_email=session['student']).first()
        return render_template("exm.html", exs=exs, sts=sts, par=par)
    else:
        return redirect("/")

# Streams details page 
@app.route("/stream")
def stream():
    if "admin" in session and session['admin'] in admin_uname:
        sts = Stream.query.all()
        return render_template("stream.html", sts=sts)
    else:
        return redirect("/")

# Holidays page 
@app.route("/holiday_list")
def holiday_list():
    if "user" in session and session['user'] in fac_uname or "student" in session and session['student'] in stu_email or "parent" in session and session['parent'] in par_email:
        year = datetime.datetime.now().year
        response = requests.get(f"https://calendarific.com/api/v2/holidays?&api_key=a5a29022d3c1e0b50421e5b919de8d4757dad055&country=IN&year={year}")
        holiday_dict = json.loads(response.content.decode('utf-8'))
        holidays = []
        for i in range(len(holiday_dict['response']['holidays'])) :
            h = holiday_dict['response']['holidays'][i]['type'][0]
            hd = []
            if h != 'Observance' and h != 'Optional holiday' and h != 'Season' and h != 'Hinduism' and h != 'Muslim' and h != 'Christian':
                hd.append(holiday_dict['response']['holidays'][i]['name'])
                hd.append(holiday_dict['response']['holidays'][i]['date']['datetime']['day'])
                hd.append(holiday_dict['response']['holidays'][i]['date']['datetime']['month'])
                hd.append(holiday_dict['response']['holidays'][i]['date']['datetime']['year'])
                hd.append(calendar.weekday(holiday_dict['response']['holidays'][i]['date']['datetime']['year'], holiday_dict['response']['holidays'][i]['date']['datetime']['month'], holiday_dict['response']['holidays'][i]['date']['datetime']['day']))
                holidays.append(hd)
        if "user" in session and session['user'] in fac_uname: 
            username = session['user']
        elif "student" in session and session['student'] in stu_email:
            username = session['student']
        elif "parent" in session and session['parent'] in par_email:
            username = session['parent']
        fac = Users.query.filter_by(username=username).first()
        return render_template("holiday_list.html", fac=fac, holidays=holidays)
    else:
        return redirect("/")

# Apply leave page 
@app.route("/apply_leave", methods = ["GET", "POST"])
def apply_leave():
    if "user" in session and session['user'] in fac_uname:
        username = session['user']
        fac = Users.query.filter_by(username=username).first()
        if(request.method == 'POST'):
            id = fac.id
            email = fac.email
            reason = request.form.get('reason')
            leavetype = request.form.get('leavetype')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            display = 1
            p = start_date.split("-")
            q = end_date.split("-")
            r = datetime.datetime(int(p[0]), int(p[1]), int(p[2]))
            s = datetime.datetime(int(q[0]), int(q[1]), int(q[2]))
            t = int(r.strftime("%d"))
            u = int(s.strftime("%d"))
            count = 0
            if t > u:
                if int(p[1]) in [1, 3, 5, 7, 8, 10, 12]:
                    for i in range(int(p[2]), 32):
                        if datetime.datetime(int(p[0]), int(p[1]), i).strftime("%a") in params['weekdays']:
                            count = count + 1
                elif int(p[1]) in [4, 6, 9, 11]:
                    for i in range(int(p[2]), 31):
                        if datetime.datetime(int(p[0]), int(p[1]), i).strftime("%a") in params['weekdays']:
                            count = count + 1      
                else:
                    if (calendar.isleap(int(p[0]))):
                        for i in range(int(p[2]), 30):
                            if datetime.datetime(int(p[0]), int(p[1]), i).strftime("%a") in params['weekdays']:
                                count = count + 1
                    else:
                        for i in range(int(p[2]), 29):
                            if datetime.datetime(int(p[0]), int(p[1]), i).strftime("%a") in params['weekdays']:
                                count = count + 1

                for i in range(1, u+1):
                    if datetime.datetime(int(p[0]), int(p[1]), i).strftime("%a") in params['weekdays']:
                        count = count + 1
            else:
                for i in range(int(p[2]), u+1):
                    if datetime.datetime(int(p[0]), int(p[1]), i).strftime("%a") in params['weekdays']:
                        count = count + 1
            v = s - r
            no_of_leaves = v.days + 1 - count
            entry = Leaves(id=id, reason=reason, leavetype=leavetype, start_date=start_date, end_date=end_date, no_of_leaves=no_of_leaves, display=display)  
            if leavetype == "sl":
                tot_leave = fac.sl
            elif leavetype == "cl":
                tot_leave = fac.cl
            elif leavetype == "el":
                tot_leave = fac.el
            if tot_leave >= no_of_leaves:
                if int(p[1]) == int(q[1]) and t > u:
                    flash("Change End Date, because End date cannot be before start date.", "danger")
                elif int(p[1]) > int(q[1]) and t < u:
                    flash("Change End Date, because End date cannot be before start date.", "danger")
                elif int(p[1]) in [12]:
                    flash("Keep End Date in this year, split them 2 different leaves if want to apply for leave in the new year too.", "danger")
                else:
                    db.session.add(entry)
                    db.session.commit()
                    message = f"Hi Admin,\n\nI have applied to request a formal leave for {no_of_leaves} days from Date(s): From: {start_date} To: {end_date} for {reason} reason. Type of leave is {leavetype.upper()}. \n\nCould you please approve the leave, if happy with the leave dates and numner of dates.\n\n{fac.name},\nFaculty. \n\n\n**Please login to EduTrack and goto: \nDashboard -> Leave Management -> Click on 'Approve' or 'Reject' button to take action on this.**"
                    print(message)
                    # mail.send_message("{fac.name} has applied for leave(s).", 
                    #                 sender = email, 
                    #                 recipients=params['gmail-user'],
                    #                 body = message
                    #             )
                    flash("You've successfully applied, Wait for the approval/rejection mail.", "success")
                    return redirect("/faculty_dash")
            else:
                flash(f"Sorry, {no_of_leaves} days are not remaining in {leavetype.upper()} type Leave Balance.", "danger")
        return render_template("apply_leave.html", fac=fac)
    else:
        return redirect("/")

# Take leave page for parents 
@app.route("/take_leave", methods = ["GET", "POST"])
def take_leave():
    if "parent" in session and session['parent'] in par_email:
        p_email = session['parent']
        par = Parents.query.filter_by(p_email=p_email).first()
        facs = Users.query.all()
        fac_emails = []
        for fac in facs:
            fac_emails.append(fac.email)
        if(request.method == 'POST'):
            reason = request.form.get('reason')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            p = start_date.split("-")
            q = end_date.split("-")
            r = datetime.datetime(int(p[0]), int(p[1]), int(p[2]))
            s = datetime.datetime(int(q[0]), int(q[1]), int(q[2]))
            t = int(r.strftime("%d"))
            u = int(s.strftime("%d"))
            count = 0
            if t > u:
                if int(p[1]) in [1, 3, 5, 7, 8, 10, 12]:
                    for i in range(int(p[2]), 32):
                        if datetime.datetime(int(p[0]), int(p[1]), i).strftime("%a") in params['weekdays']:
                            count = count + 1
                elif int(p[1]) in [4, 6, 9, 11]:
                    for i in range(int(p[2]), 31):
                        if datetime.datetime(int(p[0]), int(p[1]), i).strftime("%a") in params['weekdays']:
                            count = count + 1      
                else:
                    if (calendar.isleap(int(p[0]))):
                        for i in range(int(p[2]), 30):
                            if datetime.datetime(int(p[0]), int(p[1]), i).strftime("%a") in params['weekdays']:
                                count = count + 1
                    else:
                        for i in range(int(p[2]), 29):
                            if datetime.datetime(int(p[0]), int(p[1]), i).strftime("%a") in params['weekdays']:
                                count = count + 1

                for i in range(1, u+1):
                    if datetime.datetime(int(p[0]), int(p[1]), i).strftime("%a") in params['weekdays']:
                        count = count + 1
            else:
                for i in range(int(p[2]), u+1):
                    if datetime.datetime(int(p[0]), int(p[1]), i).strftime("%a") in params['weekdays']:
                        count = count + 1
            v = s - r
            no_of_leaves = v.days + 1 - count
            tot_leave = par.leave_bal
            if tot_leave//2 >= no_of_leaves:
                if int(p[1]) == int(q[1]) and t > u:
                    flash("Change End Date, because End date cannot be before start date.", "danger")
                elif int(p[1]) > int(q[1]) and t < u:
                    flash("Change End Date, because End date cannot be before start date.", "danger")
                elif int(p[1]) in [12]:
                    flash("Keep End Date in this year, split them 2 different leaves if want to apply for leave in the new year too.", "danger")
                else:
                    par.leave_bal = tot_leave + no_of_leaves
                    db.session.commit()
                    message = f"Hi Faculty,\n\n{par.s_name} will be on a formal leave of absence for {no_of_leaves} day(s) because of {reason} reason from: {start_date} to: {end_date}.\n\n{par.s_name} will be catching up with the studies missed after the leave(s).\n\nKindly let me know in case of any queries.\n\n{par.p_name}\nParent/LG."
                    print(message)
                    # mail.send_message("{par.p_name} has applied leave(s) for {par.s_name}.", 
                    #                 sender = par.p_email, 
                    #                 recipients = fac_emails,
                    #                 body = message
                    #             )
                    flash("You've successfully applied for leave.", "success")
                    return redirect("/faculty_dash")
            else:
                flash(f"Sorry, {no_of_leaves} days are not remaining in Leave Balance.", "danger")
        return render_template("take_leave.html", par=par)
    else:
        return redirect("/")

# Leaves details page 
@app.route("/leave_mngmt")
def leave_mngmt():
    if "admin" in session and session['admin'] in admin_uname:
        leaves = Leaves.query.all()
        facs = Users.query.all()
        count = 0
        for leave in leaves:
            if leave.display == 1:
                count = count + 1
        return render_template("leave_mngmt.html", count=count, leaves=leaves, facs=facs)
    else:
        return redirect("/")

# Approved leaves details page 
@app.route("/approved_leaves")
def approved_leaves():
    if "admin" in session and session['admin'] in admin_uname:
        leaves = Leaves.query.all()
        facs = Users.query.all()
        count = 0
        for leave in leaves:
            if leave.display == 0:
                count = count + 1
        return render_template("approved_leaves.html", count=count, leaves=leaves, facs=facs)
    else:
        return redirect("/")

# Rejected leaves page 
@app.route("/approve/<int:pk>", methods = ["POST"])
def approve(pk):
    if "admin" in session and session['admin'] in admin_uname:
        leaves = Leaves.query.all()
        facs = Users.query.all()
        if(request.method == 'POST'):
            leave = Leaves.query.filter_by(leave_id=pk).first() 
            leave.display = 0
            email = ""
            for fac in facs:
                if fac.id == leave.id:
                    email = fac.email
                    if leave.leavetype == "sl":
                        fac.sl = fac.sl - leave.no_of_leaves
                    elif leave.leavetype == "cl":
                        fac.cl = fac.cl - leave.no_of_leaves
                    elif leave.leavetype == "el":
                        fac.el = fac.el - leave.no_of_leaves
            db.session.commit()
            date = ''
            if (leave.start_date.day == leave.end_date.day):
                date = f'{leave.end_date.strftime("%B")} {leave.start_date.day}, {leave.start_date.year}'
            elif (leave.start_date.month == leave.end_date.month):
                date = f'{leave.end_date.strftime("%B")} {leave.start_date.day} to {leave.end_date.day}, {leave.start_date.year}'
            else:
                date = f'{leave.start_date.strftime("%B")} {leave.start_date.day} to {leave.end_date.strftime("%B")} {leave.end_date.day}, {leave.start_date.year}'
            message = "The leave you applied for is approved by Admin. Leave details are:\nDate(s): " + date + "\nType of leave: " + leave.leavetype.upper()
            if email != "":
                pass
                # mail.send_message("Your leave is approved by admin.", 
                #                     sender = params['gmail-user'], 
                #                     recipients=[email],
                #                     body = message
                #                 )
            flash("Leave was approved and mail was sent.", "success")
            return redirect("/leave_mngmt")
    else:
        return redirect("/")

# Leave reject page 
@app.route("/reject/<int:pk>", methods = ["POST"])
def reject(pk):
    if "admin" in session and session['admin'] in admin_uname:
        leaves = Leaves.query.all()
        facs = Users.query.all()
        if(request.method == 'POST'):
            leave = Leaves.query.filter_by(leave_id=pk).first()
            email = ""
            for fac in facs:
                if fac.id == leave.id:
                    email = fac.email
            date = ''
            if (leave.start_date.day == leave.end_date.day):
                date = f'{leave.end_date.strftime("%B")} {leave.start_date.day}, {leave.start_date.year}'
            elif (leave.start_date.month == leave.end_date.month):
                date = f'{leave.end_date.strftime("%B")} {leave.start_date.day} to {leave.end_date.day}, {leave.start_date.year}'
            else:
                date = f'{leave.start_date.strftime("%B")} {leave.start_date.day} to {leave.end_date.strftime("%B")} {leave.end_date.day}, {leave.start_date.year}'
            reason = request.form.get('rejectReason')
            message = "The leave you applied for is rejected by Admin. Leave details are:\nDate(s): " + date + "\nType of leave: " + leave.leavetype.upper() + "\nReason for rejection: " + reason
            if email != "":
                pass
                # mail.send_message("Your leave is rejected by admin.", 
                #                     sender = params['gmail-user'], 
                #                     recipients=[email],
                #                     body = message
                #                 )
            db.session.delete(leave)
            db.session.commit()
            flash("Leave was rejected and mail was sent.", "success")
            return redirect("/leave_mngmt")
        # return render_template("leave_mngmt.html", leaves=leaves, facs=facs)
    else:
        return redirect("/")

# Delete leave page 
@app.route("/delete_leave/<int:pk>", methods = ["POST"])
def delete_leave(pk):
    if "admin" in session and session['admin'] in admin_uname:
        leaves = Leaves.query.all()
        facs = Users.query.all()
        if(request.method == 'POST'):
            leave = Leaves.query.filter_by(leave_id=pk).first()
            db.session.delete(leave)
            db.session.commit()
            flash("Leave was successfully deleted.", "success")
            return redirect("/approved_leaves")
    else:
        return redirect("/")

# Notes/Updates pages 
@app.route("/notes/<int:pk>", methods = ["POST"])
def notes(pk):
    if "admin" in session and session['admin'] in admin_uname:
        facs = Users.query.all()
        if(request.method == 'POST'):
            email = ""
            for fac in facs:
                if fac.id == pk:
                    email = fac.email
                    name = fac.name
            note = request.form.get('note')
            message = note
            print(message)
            if email != "":
                pass
                # mail.send_message("Your admin has left a note for you.", 
                #                     sender = params['gmail-user'], 
                #                     recipients=email,
                #                     body = message
                #                 )
            flash(f"Note was sent as a mail to {name}.", "success")
            return redirect("/admin_dash")
    else:
        return redirect("/")

# Notes/Updates pages 
@app.route("/remarks/<int:pk>", methods = ["POST"])
def remarks(pk):
    if "user" in session and session['user'] in fac_uname:
        fac = Users.query.filter_by(username=session['user'])
        pars = Parents.query.all()
        if(request.method == 'POST'):
            email = ""
            for par in pars:
                if par.p_id == pk:
                    email = par.p_email
                    name = par.p_name
            remark = request.form.get('note')
            message = remark
            print(message)
            if email != "":
                pass
                # mail.send_message("Your admin has left a note for you.", 
                #                     sender = fac.email, 
                #                     recipients=email,
                #                     body = message
                #                 )
            flash(f"Remark was sent as a mail to {name}.", "success")
            return redirect("/students")
    else:
        return redirect("/")

# Running app 
app.run(debug=True)