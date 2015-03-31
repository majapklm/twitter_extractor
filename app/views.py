from flask import url_for,render_template,flash,redirect,session,url_for,request,abort,g
from flask.ext.login import login_user,logout_user,current_user,login_required,user_logged_in
from app import app,lm
from .forms import *
from models import *
from email import confirm_email,encode,decode
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
import json
from urllib import urlopen
from twitter import tweets
@lm.user_loader
def load_user(id):
    c=sqlite3.connect('test.db')
    c=c.execute('SELECT * from users where id=(?)',[id])
    userrow=c.fetchone()
    if userrow!=None:
    	  return User(userrow[1],userrow[2],userrow[3],userrow[4])
@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=['GET','POST'])
def index():
	git=None
        if request.form.get('submit'):
		try:
    			git=json.loads(urlopen("https://api.github.com/username/"+request.form.get('git')+"/repos").read())
		except:
			None
	else :
		try:
			git=tweets(request.form.get('twittername'))
		except:
			None
	return render_template("index.html",title='Home',datas=git)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
	return redirect("/index")
    form = LoginForm()
    if form.validate_on_submit():
    	username=form.username.data
	password=form.password.data
	remember=bool(form.rememberme.data)
	c=sqlite3.connect('test.db')
	passcheck=False
	pa=c.execute("SELECT password,email,confirm from users where username=(?)",[username])
	for x in pa:
               	passcheck=check_password_hash(x[0],password)
               	email=x[1]
               	password=x[0]
               	confirm=x[2]
	if not passcheck:
		pa=c.execute("SELECT password,username,confirm from users where email=(?)",[username])
		for x in pa:
			passcheck=check_password_hash(x[0],password)
			email=username
			username=x[1]
			password=x[0]
			confirm=x[2]
	ruser=None
	if passcheck:
		ruser=User(username,password,email,confirm)
	if ruser is None:
		return render_template('login.html',title='sign in error',form=form,error='incorrect username or password')
	login_user(ruser,remember)
	return redirect(request.args.get('next') or '/index')
    return render_template('login.html', 
                           title='Sign In',
                           form=form)
    return render_template('login.html',title='sign in',form=form)
@app.route('/register',methods=['GET','POST'])
def register():
	form=SignupForm()
	if form.validate_on_submit():
		user=User(form.username.data,form.email.data,generate_password_hash(form.password.data),False)
		try:
			user.add()
			try:
				confirm_email(form.email.data,"confirm")
			except:None
			flash('User successfully registered check your email and click the link to confirm your email')
			return redirect('/login')
		except:
			return render_template('register.html',form=form,title='register',error='user already exist')
	return render_template('register.html',form=form,title='register')
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')
@app.route('/confirm/<url>',methods=['GET','POST'])
def confirm(url):
   try:
	email=decode(url,300)
	j=sqlite3.connect('test.db')
	j.execute('UPDATE users SET confirm=1 WHERE email=(?)',[email])
	j.commit()
	flash('User successfully confirmed Email')
        return redirect('/login')
   except:
	return redirect('/register')
@app.route('/resetpassword',methods=['GET','POST'])
@app.route('/resetpassword/',methods=['GET','POST'])
def resetpass():
	return render_template('/forgotpassword.html',error='invalid reset try',title="ForgotPassword")
@app.route('/resetpassword/<url>',methods=['GET','POST'])
def reset(url):
    form=SignupForm()
    try:
	if request.form.get('reset'):
		if form.password.data==form.rptpassword.data:
			password=generate_password_hash(form.password.data)
			email=request.form.get('idid')
			k=sqlite3.connect('test.db')
			k.execute('UPDATE users SET password=(?) WHERE email=(?)',[password,email])
			k.commit()
			flash("password updated successfully")
			return redirect('/login')
	if decode(url,300):
		return render_template("resetpassword.html",email=decode(url,300),form=form)
	else:return render_template('/forgotpassword.html',error='invalid reset try',title="ForgotPassword")
    except:
	return render_template('/forgotpassword.html',error='invalid reset try',title="ForgotPassword")
@app.route('/forgotpassword',methods=['GET','POST'])
def forgot():
	if request.form.get('submit'):
		confirm_email(request.form.get('email'),'resetpassword')
	return render_template('/forgotpassword.html',error='',title="ForgotPassword")
@app.errorhandler(404)
@app.errorhandler(500)
def page_not_found(error):
	flash('This page does not exist redirected to home')
	return redirect('/index')
