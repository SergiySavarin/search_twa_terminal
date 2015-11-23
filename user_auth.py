#!/usr/bin/env python

import base64
import json

from urllib2 import urlopen, Request, HTTPError
#from search import UserSearch

API_ENDPOINT = 'https://api.twitter.com'
API_VERSION = '1.1'
REQUEST_TOKEN_URL = '%s/oauth2/token' % API_ENDPOINT
REQUEST_RATE_LIMIT = '%s/%s/application/rate_limit_status.json' % \
					(API_ENDPOINT, API_VERSION)
USER_SEARCH_URL = '%s/%s/search/tweets.json?q=paris&result_type=mixed&count=1' % \
					(API_ENDPOINT, API_VERSION)

class Client(object):
	'''For application only authorization'''
	
	def __init__(self, consumer_key, consumer_secret):
		self.consumer_key = consumer_key
		self.consumer_secret = consumer_secret
		self.access_token = ''

	def _get_access_token(self):
		'''Inner method to obtain bearer token'''
		bearer_token = '%s:%s' % (self.consumer_key, self.consumer_secret)
		encoded_bearer_token = base64.b64encode(bearer_token.encode('ascii'))
		request = Request(REQUEST_TOKEN_URL)
		request.add_header('Content-Type',
							'application/x-www-form-urlencoded;charset=UTF-8')
		request.add_header('Authorization',
							'Basic %s' % encoded_bearer_token.decode('utf-8'))

		request_data = 'grant_type=client_credentials'.encode('ascii')
		request.add_data(request_data)
		response = urlopen(request)
		raw_data = response.read().decode('utf-8')
		data = json.loads(raw_data)
		return data['access_token']

	def request(self, url):
		'''Send authennicated request to the Twitter API.'''
		if not self.access_token:
			self.access_token = self._get_access_token()

		request = Request(url)
		request.add_header('Authorization',
							'Bearer %s' % self.access_token)
		try:
			response = urlopen(request)
		except HTTPError as err:
			raise err

		raw_data = response.read().decode('utf-8')
		data = json.loads(raw_data)
		return data

	def rate_limit_status(self, resource=''):
		'''Return a dict of rate limits by resource.'''
		response = self.request(REQUEST_RATE_LIMIT)
		if resource:
			resource_family = resource.split('/')[1]
			return response['resources'][resource_family][resource]
		return response

	def check_rate_limit(self):
		''' Return True if rate limit remainder biger than 1
			else return False.
		'''
		response = self.rate_limit_status()
		rate_status = response['resources']['search']
		rate_remaining = rate_status['/search/tweets']['remaining']
		if rate_remaining == 1:
			return False
		return True


if __name__ == '__main__':
	user = UserSearch()
	consumer_key, consumer_secret = user.get_auth_data()[:2]
	client = Client(consumer_key,consumer_secret)
	status = client.rate_limit_status()
	print (status['resources']['search'],
			status['resources']['search']['/search/tweets']['remaining'])
	# print type(status['resources']['search']['/search/tweets']['remaining'])
	print client.check_rate_limit()
	search_for = client.request(USER_SEARCH_URL)
	for i in search_for['statuses'][0]:
		print i , ' = ', search_for['statuses'][0][i]
