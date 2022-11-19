'''
	This file is part of mediameta Python package.

	Copyright 2022 Dandelion Systems <dandelion.systems at gmail.com>

	mediameta was inspired and partially based on:
	1. exiftool (https://github.com/exiftool/exiftool) by Phil Harvey
	2. exif-heic-js (https://github.com/exif-heic-js/exif-heic-js), Copyright (c) 2019 Jim Liu

	mediameta is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	mediameta is distributed in the hope that it will be useful, but
	WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with mediameta. If not, see <http://www.gnu.org/licenses/>.
'''

import os

from mmdandelionsystems.dataroutines import uint_32
from mmdandelionsystems.dataroutines import uint_16
from mmdandelionsystems.dataroutines import uint_8
from mmdandelionsystems.dataroutines import sint_32
from mmdandelionsystems.dataroutines import sint_16
from mmdandelionsystems.dataroutines import sint_8
from mmdandelionsystems.dataroutines import str_b

from mmdandelionsystems.tags import _TiffTags
from mmdandelionsystems.tags import _ExifTags
from mmdandelionsystems.tags import _GPSTags

class UnsupportedMediaFile(Exception):
	pass

class MediaMetadata:
	# _tags follows {'tag_name':[tag_values_list]} format even if there is only 1 value for tag_name
	_tags = {}				

	_file_name = ''
	_file_extension = ''

	_international_encoding = ''

	def __init__(self, file_name:str, encoding:str = 'cp1251'):
		self._file_name = file_name

		_, ext = os.path.splitext(file_name)
		self._file_extension = ext.upper()

		self._international_encoding = encoding
	
	def __getitem__(self, key:str):
		value = []

		if key in self._tags:
			value = self._tags[key]

		match len(value):
			case 0:
				return None
			case 1:
				return value[0]
			case _:
				return value

	def __str__(self):
		as_string = ''
		for (key, value) in self.all():
			if key == 'MakerNote': 								# this tag's value might get long and contain binary data 
				if len(value) > 20: value = value[:20] + '...'	# so we cut it short in print
			as_string += key + '\t' + str(value) + os.linesep
		return as_string

	def all(self):
		for key in self._tags:
			yield (key,self[key])

	def keys(self):
		return list(self._tags.keys())

	def file_name(self):
		return self._file_name

	def file_type(self):
		return self._file_extension

	pass

class ImageMetadata(MediaMetadata):

	def __init__(self, file_name:str, encoding:str = 'cp1251'):
		super().__init__(file_name, encoding)

		match self._file_extension:
			case '.JPG' | '.JPEG':
				raw_meta_data = self.__find_meta_jpeg(file_name)
			case '.HEIC':
				raw_meta_data = self.__find_meta_heic(file_name)
			case '.TIF' | '.TIFF':
				raw_meta_data = self.__find_meta_tiff(file_name)
			case _:
				raise UnsupportedMediaFile
		
		if raw_meta_data is None:
			raise UnsupportedMediaFile
		
		(tiff_tags, exif_tags, gps_tags) = self.__parse_meta_data(raw_meta_data)

		self._tags = tiff_tags | exif_tags | gps_tags

	def __find_meta_jpeg(self, file_name:str):
		exif_raw_data = None
		exif_data_length = 0

		# Sanity check
		file_size = os.path.getsize(file_name)
		if file_size < 20:
			return exif_raw_data

		f = open(file_name, 'rb')

		# Check the SOI (Start Of Image) marker.
		# Must always be 0xFFD8, big endian byte order.
		b2 = int.from_bytes(f.read(2), byteorder='big')     # b2 - two bytes
		
		if b2 != 0xFFD8:
			#print('Bad SOI marker in ' + file_name +'. Not a valid JPEG.')
			return exif_raw_data

		# APP1 EXIF (0xFFE, big endian) is mandatory FIRST marker after SOI, 
		# see (EXIF 2.3, p4.5.5, Table 2 - page 6). But we search for it to 
		# jump over APP0 JFIF (0xFFE0) marker in case it is present.
		offset = 2
		f.seek(offset)
		b2 = int.from_bytes(f.read(2), byteorder='big')
		offset += 2
		while b2 != 0xFFE1 and offset < file_size - 2:							# FIXME: the first occurence of 0xFFE1 must be EXIF
			b2 = int.from_bytes(f.read(2), byteorder='big')						# so we stop at it for now. But APP1 XMP (also 0xFFE1) 
			f.seek(offset + b2)													# and ICC (0xFFE2) can follow. Would be nice to add them.
			offset += 2 + b2
			b2 = int.from_bytes(f.read(2), byteorder='big')

		if b2 == 0xFFE1:                                                        # Found TIFF/EXIF data.
			exif_data_length = int.from_bytes(f.read(2), byteorder='big') - 2   # The length value includes the length of itself, 2 bytes
			f.seek(offset + 2 + 4 + 2)                                          # Skip to the start of TIFF header: APP1 length - 2 bytes, 'Exif' - 4 bytes, 0x0000 filler - 2 bytes
			exif_raw_data = f.read(exif_data_length)                            # Read TIFF, EXIF and GPS tags as raw bytes and stop processing
			
		return exif_raw_data

	def __find_meta_tiff(self, file_name:str):
		# Sanity check
		file_size = os.path.getsize(file_name)
		if file_size < 20:
			return None
		
		f = open(file_name, 'rb')

		# Read the whole file as TIFF tags
		# Seems there is no way to determine the size of the meta data in advance
		return f.read(file_size)

	def __find_meta_heic(self, file_name:str):
		exif_raw_data = None
		exif_size = 0

		# Sanity check
		file_size = os.path.getsize(file_name)
		if file_size < 20: # Must check this later
			return exif_raw_data

		f = open(file_name, 'rb')

		ftype_size = int.from_bytes(f.read(4), byteorder='big')         # size of ftype box
		f.seek(ftype_size)
		metadata_size = int.from_bytes(f.read(4), byteorder='big')      # size of metadata box

		# Scan through metadata until we find (a) Exif, (b) iloc
		data = f.read(metadata_size)
		exif_offset = -1
		iloc_offset = -1
		for i in range(metadata_size-4): 								# '-4' as we are reading by 4-byte values and 
			b4 = data[i:i+4]											# the last 3 readings would otherwise go out of range
			if b4 == b'Exif':
				exif_offset = i
			elif b4 == b'iloc':
				iloc_offset = i

		if exif_offset == -1 or iloc_offset == -1:
			return exif_raw_data

		exif_item_index = uint_16(byte_array=data, start_index=exif_offset - 4, byte_order='big')

		# Scan through ilocs to find exif item location
		i = iloc_offset + 12
		while i < metadata_size - 16:
			item_index = uint_16(byte_array=data, start_index=i, byte_order='big')

			if item_index == exif_item_index:
				exif_location = uint_32(byte_array=data, start_index=i + 8, byte_order='big')
				exif_size = uint_32(byte_array=data, start_index=i + 12, byte_order='big')
				# FIXME: Check EXIF prefix at exif_location
				f.seek(exif_location)
				prefix_size = 4 + int.from_bytes(f.read(4), byteorder='big')
				f.seek(exif_location + prefix_size)
				exif_raw_data = f.read(exif_size)
				break

			i += 16

		return exif_raw_data

	def __parse_meta_data(self, exif_data:bytes):
		tiff_tags = {}
		exif_tags = {}
		gps_tags  = {}

		# Validity check 1: the first two bytes contain little/big endian marker
		if exif_data[0] == 0x49 and exif_data[1] == 0x49:   # I I - Intel
			byte_order = 'little'
		elif exif_data[0] == 0x4D and exif_data[1] == 0x4D: # M M - Motorola
			byte_order = 'big'
		else:
			return (tiff_tags, exif_tags, gps_tags)

		# Valdity check 2: the third and fourth bytes contain a 0x002A magic number
		if uint_16(byte_array=exif_data, start_index=2, byte_order=byte_order) != 0x002A:
			return (tiff_tags, exif_tags, gps_tags)

		ifd1_offset = uint_32(byte_array=exif_data, start_index=4, byte_order=byte_order)

		# Valdity check 3: the first IFD must be reachable
		if ifd1_offset < 8 or ifd1_offset >= len(exif_data):
			return (tiff_tags, exif_tags, gps_tags)

		tiff_tags = self.__read_tags(data=exif_data, offset=ifd1_offset, tags_to_search=_TiffTags | _ExifTags, byte_order=byte_order)

		if 'ExifIFDPointer' in tiff_tags:
			exif_offset = tiff_tags['ExifIFDPointer'][0]
			exif_tags = self.__read_tags(data=exif_data, offset=exif_offset, tags_to_search=_TiffTags | _ExifTags, byte_order=byte_order)

		if 'GPSInfoIFDPointer' in tiff_tags:
			gps_offset = tiff_tags['GPSInfoIFDPointer'][0]
			gps_tags = self.__read_tags(data=exif_data, offset=gps_offset, tags_to_search=_GPSTags, byte_order=byte_order)

		# FIXME: Interoperability tags are not parsed.
		return (tiff_tags, exif_tags, gps_tags)

	def __read_tag_value(self, data:bytes, offset:int, tag:int, byte_order:str):
		tag_type = uint_16(byte_array=data, start_index=offset + 2, byte_order=byte_order)
		num_values = uint_32(byte_array=data, start_index=offset + 4, byte_order=byte_order)
		value_offset = uint_32(byte_array=data, start_index=offset + 8, byte_order=byte_order)
		values = []
		encoding = self._international_encoding

		match tag_type:
			case 1: # 1 - byte, 8-bit unsigned int
				if num_values <= 4:
					where_to_look = offset + 8
				else:
					where_to_look = value_offset
					
				values = [data[where_to_look + i] for i in range(num_values)]

			case 2: # ascii, 8-bit byte
				if num_values <= 4:
					where_to_look = offset + 8
				else:
					where_to_look = value_offset

				values.append(str_b(byte_array=data, start_index=where_to_look, byte_count=num_values-1, encoding=encoding))

			case 3: # short, 16 bit int
				if num_values <= 2:
					where_to_look = offset + 8
				else:
					where_to_look = value_offset
		
				values = [uint_16(byte_array=data, start_index=where_to_look + i, byte_order=byte_order) for i in range(num_values)]

			case 4: # 4 - long, 32 bit int
				if num_values == 1:
					where_to_look = offset + 8
				else:
					where_to_look = value_offset
		
				values = [uint_32(byte_array=data, start_index=where_to_look + i, byte_order=byte_order) for i in range(num_values)]

			case 5: # 5 - rational, two long values, first is numerator, second is denominator
				where_to_look = value_offset
				for i in range(num_values):
					numerator = uint_32(byte_array=data, start_index=where_to_look + i*8, byte_order=byte_order)
					denominator = uint_32(byte_array=data, start_index=where_to_look + i*8 + 4, byte_order=byte_order)
					values.append(str(numerator) + '/' + str(denominator))

			case 7: # 7 - undefined, value depending on field
				if num_values <= 4:
					where_to_look = offset + 8
				else:
					where_to_look = value_offset

				values.append(str_b(byte_array=data, start_index=where_to_look, byte_count=num_values, encoding=encoding))
				
			case 9: # 9 - slong, 32 bit signed int.
				if num_values == 1:
					where_to_look = offset + 8
				else:
					where_to_look = value_offset
		
				values = [sint_32(byte_array=data, start_index=where_to_look + i, byte_order=byte_order) for i in range(num_values)]

			case 10: #10 - signed rational, two long values, first is numerator, second is denominator
				where_to_look = value_offset
				for i in range(num_values):
					numerator = sint_32(byte_array=data, start_index=where_to_look + i*8, byte_order=byte_order)
					denominator = sint_32(byte_array=data, start_index=where_to_look + i*8 + 4, byte_order=byte_order)
					values.append(str(numerator) + '/' + str(denominator))

		return values

	def __read_tags(self, data:bytes, offset:int, tags_to_search:dict, byte_order:str):
		entries = uint_16(data, offset, byte_order)
		tags = {}

		for i in range(entries):
			entry_offset = offset + i * 12 + 2 # entry_offset is relevant to TIFF headers (i.e. 0x4949 or 0x4D4D byte order marker has an offset of 0
			tag_marker = uint_16(byte_array=data, start_index=entry_offset, byte_order=byte_order)
			if tag_marker in tags_to_search:
				key = tags_to_search[tag_marker]
			else:
				key = 'Tag 0x{0:04X} ({1:05})'.format(tag_marker, tag_marker)
			tags[key] = self.__read_tag_value(data=data, offset=entry_offset, tag=tag_marker, byte_order=byte_order)
		
		return tags

	pass

class VideoMetadata(MediaMetadata):

	def __init__(self, file_name:str, encoding:str = 'cp1251'):
		super().__init__(file_name, encoding)

		match self._file_extension:
			case '.MOV':
				tags_list = self.__find_meta_mov(file_name)
			case _:
				raise UnsupportedMediaFile
		
		if tags_list is None:
			raise UnsupportedMediaFile

		for i in range(len(tags_list)):
			key = str_b(tags_list[i][0], 0, len(tags_list[i][0], encoding=encoding))
			value = str_b(tags_list[i][1], 0, len(tags_list[i][1], encoding=encoding))
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
			atom_size = int.from_bytes(f.read(4), byteorder='big')
			atom_name = f.read(4)

			if atom_size == 0:
				atom_size = file_size - offset
			elif atom_size == 1:
				atom_size = int.from_bytes(f.read(8), byteorder='big')

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
			atom_size = int.from_bytes(f.read(4), byteorder='big')
			atom_name = f.read(4)

			if atom_size == 0:
				atom_size = file_size - offset
			elif atom_size == 1:
				atom_size = int.from_bytes(f.read(8), byteorder='big')

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
			atom_size = int.from_bytes(f.read(4), byteorder='big')
			atom_name = f.read(4)

			if atom_size == 0:
				atom_size = file_size - offset
			elif atom_size == 1:
				atom_size = int.from_bytes(f.read(8), byteorder='big')

			qt_meta_atoms[atom_name] = [atom_size, offset]

			qt_atom_index += 1
			offset += atom_size

		# 'keys' and 'ilst' subatoms found. Read them. 
		if b'keys' in qt_meta_atoms and b'ilst' in qt_meta_atoms:
			qt_meta_keys = {0:[b'',b'']}

			keys_offset = qt_meta_atoms[b'keys'][1] + 4 + 4 + 4  # Skip size, type and 4 zero bytes of 'keys' atom 
			ilst_offset = qt_meta_atoms[b'ilst'][1] + 4 + 4      # Skip size, type of 'ilst' atom
			
			f.seek(keys_offset)
			entry_count = int.from_bytes(f.read(4), byteorder='big')
			keys_offset += 4

			for i in range(entry_count):
				# each entry in 'keys' has the following format: 
				# key_size:unit32, namespace:unit32, key_name:array of bytes with sizeof(key_name) = key_size - 8
				f.seek(keys_offset)
				key_size = int.from_bytes(f.read(4), byteorder='big')
				f.seek(keys_offset + 4 + 4)
				key_name = f.read(key_size - 8)
				keys_offset += 4 + 4 + key_size - 8

				# each entry in 'ilst' has the following format: 
				# record_size:uint32, key_index:unit32, record_size1:unit32, 'data' (or other 4-byte literals), type:unit32, locale:unit32, key_value:array of bytes with sizeof(key_value) = record_size1 - 16
				# record_size1 = record_size - 8, so record_size is superfluous
				f.seek(ilst_offset + 4) # skip record_size as superfluous
				j = int.from_bytes(f.read(4), byteorder='big') - 1
				value_size = int.from_bytes(f.read(4), byteorder='big') - 4 - 4 - 4 - 4
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
