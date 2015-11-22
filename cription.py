#!/usr/bin/env python

import hashlib
import os
import random
import struct

from Crypto.Cipher import AES

class CryptObject(object):
	'''Class for encrypting and decripting files.
		
		chunk_size:
			Sets the size of the chunk whick the function
			uses to read and encrypt the file. Chunk size
			must be devisible by 16.
	'''

	def __init__(self):
		self.mode = AES.MODE_CBC # ecription and dicription mode
		self.chunk_size = 64*1024

	def _credential_preparer(self, user_name, user_pass):
		'''	Frunction prepare user credentials
			for encrypting/decripting.
		'''
		if len(user_name) % 16 != 0 or len(user_pass) % 16 != 0:
			user_name += ' ' * (16 - len(user_name) % 16)
			user_pass += ' ' * (16 - len(user_pass) % 16)
		return user_name, user_pass


	def encrypt_user_credentials(self, user_name, user_pass):
		''' Function encrypt user credentials by
			using AES (CBC mode) with given key. In our
			case key for user name encryption is user
			password and for user password is user name.

			user_name:
				User name as string

			user_pass:
				User password as string
		'''
		user_name, user_pass = self._credential_preparer(user_name, user_pass)

		key_for_pass = hashlib.sha256(user_name).digest()
		key_for_name = hashlib.sha256(user_pass).digest()

		iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
		encryptor_for_name = AES.new(key_for_name, self.mode, iv)
		encryptor_for_pass = AES.new(key_for_pass, self.mode, iv)

		#adding symbols ':' to divide phrase
		#during decription

		return (encryptor_for_name.encrypt(user_name) + '1234' + iv +
			'1234' + encryptor_for_pass.encrypt(user_pass)).encode('hex')

	def decrypt_user_credentials(self, user_name, user_pass,
									user_credentials, restore=False):
		''' Function decrypt user credentials by
			using AES (CBC mode) with given key. In our
			case key for user name encryption is user
			password and for user password is user name.

			user_name:
				User name as string

			user_pass:
				User password as string
			
			user_credentials:
				Encrypted user credentials

			Output:
				True or False for user validation
		'''
		user_name, user_pass = self._credential_preparer(user_name, user_pass)

		credentials = user_credentials.decode('hex')
		credentials = credentials.split('1234')

		key_for_pass = hashlib.sha256(user_name).digest()
		key_for_name = hashlib.sha256(user_pass).digest()

		iv = credentials[1]
		decryptor_for_name = AES.new(key_for_name, self.mode, iv)
		decryptor_for_pass = AES.new(key_for_pass, self.mode, iv)

		if restore:
			return (decryptor_for_name.decrypt(credentials[0]),
					decryptor_for_pass.decrypt(credentials[2]))

		if decryptor_for_name.decrypt(credentials[0]) != user_name or \
			decryptor_for_pass.decrypt(credentials[2]) != user_pass:
			return False
		return True

	def encrypt_file(self, key, input_filename, output_filename=None):
		''' Function for encrypting file with key(user pass)
			by file name or path.

			key:
				The encryption key - a string must be 
				either 16, 24, 32 bytes long. Longer keys
				more secure. In out case key is user pass.

			input_filename:
				Name or path of the input file.

			output_filename:
				if None, '<input_filename>.enc' will be used.
		'''
		if not output_filename:
			output_filename = input_filename.split('.')[0] + '.enc'

		iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
		encryptor = AES.new(key, self.mode, iv)
		filesize = os.path.getsize(input_filename)

		with open(input_filename, 'r') as inpfile:
			with open(output_filename, 'w') as outfile:
				outfile.write(struct.pack('<Q', filesize))
				outfile.write(iv)

				while True:
					chunk = inpfile.read(self.chunk_size)
					if len(chunk) == 0:
						break
					elif len(chunk) % 16 != 0:
						chunk += ' ' * (16 - len(chunk) % 16)

					outfile.write(encryptor.encrypt(chunk))

	def decrypt_file(self, key, input_filename, output_filename=None):
		''' Function decript input file usig AES (CBC mode) with
			the give key. Parameters are simular to encrypt_file
			function. One exception is output file name.

			output_filename:
				If name None, than '<input_filename>.dec'
		'''
		if not output_filename:
			output_filename = input_filename.split('.')[0] + '.dec'

		with open(input_filename, 'r') as inpfile:
			original_size = struct.unpack('<Q',
							inpfile.read(struct.calcsize('Q')))[0]
			iv = inpfile.read(16)
			decryptor = AES.new(key, self.mode, iv)
			with open(output_filename, 'w') as outfile:
				while  True:
					chunk = inpfile.read(self.chunk_size)
					if len(chunk) == 0:
						break
					outfile.write(decryptor.decrypt(chunk))

				outfile.truncate(original_size)

if __name__ == '__main__':
	passwd = 'trololo'
	key = hashlib.sha256(passwd).digest()
	
	# hex_key = key.encode('hex')
	dec = CryptObject()
	foo = dec.encrypt_user_credentials('victor', passwd)
	print foo
	print dec.decrypt_user_credentials('victor', passwd, foo)
	# dec.encrypt_file(key, 'set_test4.py')
	# dec.decrypt_file(key, 'set_test4.enc')
	print 'Done'