#!/usr/bin/env python

import os
import socket
import sys

from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import Required

from cription import CryptObject
from search import UserSearch


class MyForm(Form):
	name = StringField('Login', validators=[Required()])
	password = PasswordField('Password', validators=[Required()])
	submit = SubmitField('Submit')

class MySearch(Form):
	search = StringField('', validators=[Required()])
	submit = SubmitField('Twitter Search')

class MyRegistration(Form):
	name = StringField('Login', validators=[Required()])
	password1 = PasswordField('Password', validators=[Required()])
	password2 = PasswordField('Repeat Password', validators=[Required()])
	submit = SubmitField('Submit')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Shomething hard to guess'
bootstrap = Bootstrap(app)
user = UserSearch()
credentials = CryptObject()

@app.route('/', methods=['GET', 'POST'])
def index():
	form = MyForm()
	if form.validate_on_submit():
		form.name.data = str(form.name.data)
		form.password.data = str(form.password.data)
		session['name'] = form.name.data
		cred_data = [x[:-1] for x in open(user.credentials_file, 'r')			#add valid credential
					if credentials.decrypt_user_credentials(form.name.data, 	#validation credentials
											form.password.data, x[:-1])]		#func return True if valid
		if len(cred_data) == 1:
			if user.user_folder_name == '':
				user.user_folder_name = cred_data[0][:10]						#use first ten symbols for user's folder name for saving wprking files
			return redirect(url_for('user_page', name=session.get('name')))
		else:
			flash('Wrong login name or password.')
		form.name.data = ''
		form.password.data = ''
		return redirect(url_for('index'))
	return render_template('index.html', form=form, name=session.get('name'))

@app.route('/user/<name>', methods=['GET', 'POST'])
def user_page(name):
	form = MySearch()
	if form.validate_on_submit():
		phrase = str(form.search.data)
		data = user.colect_users_data_for_last_7_days(phrase)
		# form.search.data = ''
		if data:
			return render_template('search_result.html', form=form,
							phrase=phrase, name=session['name'], data=data)
		return redirect(url_for('user_page', name=session.get('name')))
	# session['name'] = form.name.data
	try:
		dir_list = os.listdir(user.user_folder_name)
	except:
		return redirect(url_for('index'))
	return render_template('user1.html', form=form,
							name=session['name'], dir_list=dir_list)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
	form = MyRegistration()
	if form.validate_on_submit():
		if form.password1.data != form.password2.data:
			flash('Wrong password input.')
		data = credentials.encrypt_user_credentials(form.name.data,
													form.password1.data)
		user.user_folder_name = data[:10]								#use first ten symbols for user's folder name for saving wprking files
		create = user.terminal_interaction
		create('mkdir %s' % user.user_folder_name)						#create working folder
		with open(user.credentials_file, 'a') as cred_data:
			cred_data.write(data + '\n')
		cred_data.close()
		form.name.data = ''
		form.password1.data = ''
		form.password2.data = ''
		return redirect(url_for('index'))
	return render_template('registration.html', form=form)

@app.route('/user/<name>/<us_file>', methods=['GET', 'POST'])
def user_file(name, us_file):
	data = open('%s/%s' % (user.user_folder_name, us_file))
	# print user.user_folder_name, type(user.user_folder_name)
	# print us_file, type(us_file)
	line = [x for x in data]
	# print line
	return app.send_static_file('%s/%s' % (user.user_folder_name, us_file))
	return render_template('file.html', data=line)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

if __name__ == '__main__':
	host = str(socket.gethostbyname(socket.getfqdn()))
	print ' * Server started on host: %s, port: 5000' % host
	app.run(host=host, debug=True)
	bootstrap
