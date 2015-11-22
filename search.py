#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import oauth2
import os
import sys

from datetime import date, timedelta
from cription import CryptObject

class UserSearch(object):
	''' Class realize user login by terminal,
		validation login data, search tweets by word
		or phrase, colect tweets data during last 7 days
		and sort by included parameters.
	'''
	def __init__(self):
		''' Define file with consuner authorization data
			and file with application users credentials.
		'''
		self.auth_data_file = 'tk.txt'
		self.credentials_file = 'credentials.txt'

	def _date_range(self):
		''' Forming list of dates for search by date.
			Only for class inner using.
		'''
		date_range = []
		for i in range(7):
			date_range.append((date.today() - 
				timedelta(i)).strftime('%Y-%m-%d'))
		date_range.reverse()
		return date_range

	def terminal_interaction(self, action):
		method = getattr(os, 'system')
		return method(action)
	
	def get_auth_data(self):
		'''Get twitter authorization data from file'''
		auth_data = []
		for i in open(self.auth_data_file, 'r'):
			token.append(i.rstrip())
		return auth_data

	def login(self):
		''' Login function. Realize login to application
			using terminal and validation user credentials
			using file with credentials and CryptObject.
		'''
		inpt = raw_input('If your`re registered user enter `Sign In` or press Enter\n \
 					\relse enter `Registration` to registrate new User.\n \
 					\r>')
		if inpt.lower() == 'sign in' or inpt == '':
			while True:
				name = raw_input('Enter your name: ')
				passwd = raw_input('Enter your password: ')
				credentials = CryptObject()
				cred_data = [x for x in open(self.credentials_file, 'r')		#add valid credential
					if credentials.decrypt_user_credentials(name, 				#validation credentials
															passwd, x[:-1])]	#func return True if valid
				if len(cred_data) == 1:
					print 'Successfuly logined'
					user_folder_name = cred_data[0][:10]
					show = self.terminal_interaction
					if os.listdir(user_folder_name) == []:
						print 'Your working directory is empty'
					else:
						show('ls %s' % user_folder_name)
					break
				print 'Your login or password is wrong try one more time!'
		else:
			self.registration()

	def registration(self):
		''' Registration function. Realize reginstration to
			application and adding user credentials to 
			credentials.txt. Creat user working folder.
		'''
		print 'Registration Form'
		name = raw_input('Enter your name: ')
		while True:
			passwd1 = raw_input('Enter your password: ')
			passwd2 = raw_input('Enter your password: ')
			if passwd1 == passwd2:
				break
			print 'Incorrect password'
		credentials = CryptObject()
		data = credentials.encrypt_user_credentials(name, passwd1)
		user_folder_name = data[:10]								#use first ten symbols for user's folder name for saving wprking files
		create = self.terminal_interaction
		create('mkdir %s' % user_folder_name)						#create working folder
		with open(self.credentials_file, 'a') as cred_data:
			cred_data.write(data + '\n')
		cred_data.close()


	# def get_request(date, method='GET'):
	# 	consumer = oauth2.Consumer(key=get_auth_data()[0], 
	# 							secret=get_auth_data()[1])
	# 	client = oauth2.Client(consumer)
	# 	resp, content = client.request(
	# 					(search_tweets_url(get_phrase()) + date), method)
	# 	return content

	def search_tweets_url(self, phrase):
		''' Function return search url with input phrase
			and without date for using to request tweets data.

			phrase:
				Word or phrase whick user enter for search
		'''
		api_endpoint = 'https://api.twitter.com'
		api_version = '1.1'
		search = 'search/tweets.json'
		query = '?q=' + phrase
		result_type = '&result_type=mixed'
		count = '&count=50'
		date = '&until='
		search_url = '%s/%s/%s' + query + result_type + count + date % \
					(api_endpoint, api_version, search)
		return search_url

	def get_phrase(self):
		phrase = raw_input('Enter your word or phrase for search: ')
		return phrase

	def colect_user_data(self, tweets_data, users_data):
		''' Function colect user data from tweet.

			tweets_data:
				Raw tweets data by date in dict.

			users_data:
				User's tweet data in dict.

			output:
				Colected data about tweet and his owner.
		'''
		for user in tweets_data:
			user_data = []
			user_profile_data = user['user']
			user_data.append(user['id_str'].encode('utf-8'))
			user_data.append(user['text'].encode('utf-8'))
			user_data.append(user_profile_data['location'].encode('utf-8'))
			user_data.append(user_profile_data['lang'].encode('utf-8'))
			try:
				user_data.append(user_profile_data['time_zone'].encode('utf-8'))
			except:
				user_data.append(user_profile_data['time_zone'])
			if user_data not in users_data:
				users_data.append(user_data)
		return users_data

	def colect_users_data_for_last_7_days(self):
		users_data = []
		for date in _date_range():
			content = json.loads(get_request(date))
			tweets_data = content['statuses']
			users_data = colect_user_data(tweets_data, users_data)
		return users_data

	# def show_data():
	# 	data = colect_users_data_for_last_7_days()
	# 	for line in data:
	# 		print line

	def sort_data(self, sort_by=1):
		''' Function sort colecred data by
			language, location or time zone.

			sort_by:
				1 : location
				2 : language
				3 : time zone

			output:
				Sorted data with three most
				popular staff which was used
				like filter.
		'''		
		data = colect_users_data_for_last_7_days()
		list_for_sort = [x[sort_by + 1] for x in data]
		sorted_dict = {}
		for phrase in list_for_sort:
			if phrase in sorted_dict:
				sorted_dict[phrase] += 1
			else:
				sorted_dict[phrase] = 1
		values = [sorted_dict[x] for x in sorted_dict]
		values = sorted(values, reverse=True)
		values = values[0:3]
		sorted_list = [(x, y) for x in values				#make list with values of most popular staff
								for y in sorted_dict
									if sorted_dict[y] == x]
		return sorted_list

	def write_data_to_file(self, file_name):
		data = colect_users_data_for_last_7_days()
		data_file = open('%s/%s' % (user_folder_name, file_name), 'w')
		for line in data:
			data_file.write(line)
		data_file.close()
		print 'Your data saved to %s' % file_name

if __name__ == '__main__':
	user = UserSearch()
	user.login()
	# print sort_data(3)
	# show_data()
	# print colect_users_data_for_last_7_days(), len(colect_users_data_for_last_7_days())
