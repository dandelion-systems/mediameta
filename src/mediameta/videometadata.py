'''
	This file is part of mediameta Python package.

	Copyright 2022 Dandelion Systems <dandelion.systems at gmail.com>

	mediameta was inspired and partially based on:
	1. exiftool (https://github.com/exiftool/exiftool) by Phil Harvey
	2. exif-heic-js (https://github.com/exif-heic-js/exif-heic-js), Copyright (c) 2019 Jim Liu

	mediameta is free software; you can redistribute it and/or modify
	it under the terms of the MIT License.

	mediameta is distributed in the hope that it will be useful, but
	WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
	See the MIT License for more details.

	SPDX-License-Identifier: MIT
'''

import os

from .dataroutines import str_b

from .mediametadata import UnsupportedMediaFile
from .mediametadata import MediaMetadata

class VideoMetadata(MediaMetadata):

	def __init__(self, file_name:str, encoding:str = 'utf_8'):
		super().__init__(file_name, encoding)

		match self._file_extension:
			case '.MOV':
				tags_list = self.__find_meta_mov(file_name)
			case _: # UPNEXT: mp4
				raise UnsupportedMediaFile
		
		if tags_list is None:
			raise UnsupportedMediaFile

		for i in range(len(tags_list)):
			key = str_b(tags_list[i][0], 0, len(tags_list[i][0]), encoding)
			value = str_b(tags_list[i][1], 0, len(tags_list[i][1]), encoding)
			self._tags[key] = [value]

	def __find_meta_mov(self, file_name:str):
		# Sanity check
		file_size = os.path.getsize(file_name)
		if file_size < 8:
			return None

		f = open(file_name, 'rb')

		# Read the top level atoms.
		# We assume to find the 'moov' atom among them.
		offset = 0
		moov_atom_offset = -1
		moov_atom_size = -1

		qt_atoms = {}
		qt_atom_index = 0

		while offset < file_size:
			f.seek(offset)
			atom_size = int.from_bytes(f.read(4), 'big')
			atom_name = f.read(4)

			if atom_size == 0:
				atom_size = file_size - offset
			elif atom_size == 1:
				atom_size = int.from_bytes(f.read(8), 'big')

			qt_atoms[qt_atom_index] = [atom_name, atom_size, offset]

			if atom_name == b'moov':
				moov_atom_offset = offset
				moov_atom_size = atom_size
				#break - if we do not wish to read all atom names at the current level

			qt_atom_index += 1
			offset += atom_size

		if moov_atom_offset == -1:
			return None

		# Now dive into the 'moov' atom looking for 'meta' subatom.
		offset = moov_atom_offset + 4 + 4       # 4 bytes - size, 4 bytes = 'moov', then the first subatom of 'moov' atom starts
		meta_atom_offset = -1
		meta_atom_size = -1
		qt_moov_atoms = {}
		qt_atom_index = 0

		while offset < moov_atom_offset + moov_atom_size:
			f.seek(offset)
			atom_size = int.from_bytes(f.read(4), 'big')
			atom_name = f.read(4)

			if atom_size == 0:
				atom_size = file_size - offset
			elif atom_size == 1:
				atom_size = int.from_bytes(f.read(8), 'big')

			qt_moov_atoms[qt_atom_index] = [atom_name, atom_size, offset]

			if atom_name == b'meta':
				meta_atom_offset = offset
				meta_atom_size = atom_size
				#break - if we do not wish to read all atom names at the current level

			qt_atom_index += 1
			offset += atom_size

		if meta_atom_offset == -1:
			return None

		# 'meta' atom found. We need to read its 'keys' and 'ilst' subatoms
		# to get the metadata. Hopefully it will contain the date and time information.
		offset = meta_atom_offset + 4 + 4       # 4 bytes - size, 4 bytes = 'meta', then the first subatom of 'meta' atom starts

		qt_meta_atoms = {}
		qt_atom_index = 0

		while offset < meta_atom_offset + meta_atom_size:
			f.seek(offset)
			atom_size = int.from_bytes(f.read(4), 'big')
			atom_name = f.read(4)

			if atom_size == 0:
				atom_size = file_size - offset
			elif atom_size == 1:
				atom_size = int.from_bytes(f.read(8), 'big')

			qt_meta_atoms[atom_name] = [atom_size, offset]

			qt_atom_index += 1
			offset += atom_size

		# 'keys' and 'ilst' subatoms found. Read them. 
		if b'keys' in qt_meta_atoms and b'ilst' in qt_meta_atoms:
			qt_meta_keys = {0:[b'',b'']}

			keys_offset = qt_meta_atoms[b'keys'][1] + 4 + 4 + 4  # Skip size, type and 4 zero bytes of 'keys' atom 
			ilst_offset = qt_meta_atoms[b'ilst'][1] + 4 + 4      # Skip size, type of 'ilst' atom
			
			f.seek(keys_offset)
			entry_count = int.from_bytes(f.read(4), 'big')
			keys_offset += 4

			for i in range(entry_count):
				# each entry in 'keys' has the following format: 
				# key_size:unit32, namespace:unit32, key_name:array of bytes with sizeof(key_name) = key_size - 8
				f.seek(keys_offset)
				key_size = int.from_bytes(f.read(4), 'big')
				f.seek(keys_offset + 4 + 4)
				key_name = f.read(key_size - 8)
				keys_offset += 4 + 4 + key_size - 8

				# each entry in 'ilst' has the following format: 
				# record_size:uint32, key_index:unit32, record_size1:unit32, 'data' (or other 4-byte literals), type:unit32, locale:unit32, key_value:array of bytes with sizeof(key_value) = record_size1 - 16
				# record_size1 = record_size - 8, so record_size is superfluous
				f.seek(ilst_offset + 4) # skip record_size as superfluous
				j = int.from_bytes(f.read(4), 'big') - 1
				value_size = int.from_bytes(f.read(4), 'big') - 4 - 4 - 4 - 4
				f.seek(ilst_offset + 4 + 4 + 4 + 4 + 4 + 4)
				key_value = f.read(value_size)
				ilst_offset += 4 + 4 + 4 + 4 + 4 + 4 + value_size

				# Values in 'ilst' do not necessarily go in the order of 'keys'.
				# So we intiate a record here and its key name/value pair gets filled out asyncroniously.
				if i not in qt_meta_keys:
					qt_meta_keys[i] = [b'',b'']
				if j not in qt_meta_keys:
					qt_meta_keys[j] = [b'',b'']

				qt_meta_keys[i][0] = key_name
				qt_meta_keys[j][1] = key_value
		else:
			return None

		return qt_meta_keys

	pass
