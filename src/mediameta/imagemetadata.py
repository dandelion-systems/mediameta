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

from .dataroutines import uint_32
from .dataroutines import uint_16
from .dataroutines import sint_32
from .dataroutines import str_b

from .tags import _TiffTags
from .tags import _ExifTags
from .tags import _GPSTags

from .mediametadata import UnsupportedMediaFile
from .mediametadata import MediaMetadata

class ImageMetadata(MediaMetadata):

	def __init__(self, file_name:str, encoding:str = 'utf_8'):
		super().__init__(file_name, encoding)

		self._nonprintable_tags += [
			'XMLPacket', 'MakerNote', 'UserComment', 
			'ImageResources', 'ImageDescription',
			'IPTCNAA', 'StripByteCounts', 'StripOffsets',
			'InterColorProfile', 'JPEGTables', 'OECF',
			'SpatialFrequencyResponse', 'CFAPattern',
			'DeviceSettingDescription', 'ExifIFDPointer',
			'GPSInfoIFDPointer', 'InteroperabilityIFDPointer'
		]

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
		
		(tiff_tags, exif_tags, gps_tags, inter_tags) = self.__parse_meta_data(raw_meta_data)

		self._tags = tiff_tags | exif_tags | gps_tags | inter_tags

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
		b2 = int.from_bytes(f.read(2), 'big')     # b2 - two bytes
		
		if b2 != 0xFFD8:
			#print('Bad SOI marker in ' + file_name +'. Not a valid JPEG.')
			return exif_raw_data

		# APP1 EXIF (0xFFE1, big endian) is mandatory FIRST marker after SOI, 
		# see (EXIF 2.3, p4.5.5, Table 2 - page 6). But we search for it to 
		# jump over APP0 JFIF (0xFFE0) marker in case it is present.
		offset = 2
		f.seek(offset)
		b2 = int.from_bytes(f.read(2), 'big')
		offset += 2
		while b2 != 0xFFE1 and offset < file_size - 2:							# FIXME: the first occurence of 0xFFE1 must be EXIF
			b2 = int.from_bytes(f.read(2), 'big')						# so we stop at it for now. But APP1 XMP (also 0xFFE1) 
			f.seek(offset + b2)													# and ICC (0xFFE2) can follow. Would be nice to add them.
			offset += 2 + b2
			b2 = int.from_bytes(f.read(2), 'big')

		if b2 == 0xFFE1:                                                        # Found TIFF/EXIF data.
			exif_data_length = int.from_bytes(f.read(2), 'big') - 2   # The length value includes the length of itself, 2 bytes
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

		ftype_size = int.from_bytes(f.read(4), 'big')         # size of ftype box
		f.seek(ftype_size)
		metadata_size = int.from_bytes(f.read(4), 'big')      # size of metadata box

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

		exif_item_index = uint_16(data, exif_offset - 4, 'big')

		# Scan through ilocs to find exif item location
		i = iloc_offset + 12
		while i < metadata_size - 16:
			item_index = uint_16(data, i, 'big')

			if item_index == exif_item_index:
				exif_location = uint_32(data, i + 8, 'big')
				exif_size = uint_32(data, i + 12, 'big')
				# FIXME: Check EXIF prefix at exif_location
				f.seek(exif_location)
				prefix_size = 4 + int.from_bytes(f.read(4), 'big')
				f.seek(exif_location + prefix_size)
				exif_raw_data = f.read(exif_size)
				break

			i += 16

		return exif_raw_data

	def __parse_meta_data(self, exif_data:bytes):
		tiff_tags = {}
		exif_tags = {}
		gps_tags  = {}
		inter_tags = {}

		# Validity check 1: the first two bytes contain little/big endian marker
		if exif_data[0] == 0x49 and exif_data[1] == 0x49:   # I I - Intel
			byte_order = 'little'
		elif exif_data[0] == 0x4D and exif_data[1] == 0x4D: # M M - Motorola
			byte_order = 'big'
		else:
			return (tiff_tags, exif_tags, gps_tags)

		# Validity check 2: the third and fourth bytes contain a 0x002A magic number
		if uint_16(exif_data, 2, byte_order) != 0x002A:
			return (tiff_tags, exif_tags, gps_tags)

		ifd1_offset = uint_32(exif_data, 4, byte_order)

		# Validity check 3: the first IFD must be reachable
		if ifd1_offset < 8 or ifd1_offset >= len(exif_data):
			return (tiff_tags, exif_tags, gps_tags)

		tiff_tags = self.__read_tags(exif_data, ifd1_offset, _TiffTags | _ExifTags, byte_order)

		if 'ExifIFDPointer' in tiff_tags:
			exif_offset = tiff_tags['ExifIFDPointer'][0]
			exif_tags = self.__read_tags(exif_data, exif_offset, _TiffTags | _ExifTags, byte_order)

		gps_offset = -1
		if 'GPSInfoIFDPointer' in tiff_tags:
			gps_offset = tiff_tags['GPSInfoIFDPointer'][0]
		elif 'GPSInfoIFDPointer' in exif_tags:
			gps_offset = exif_tags['GPSInfoIFDPointer'][0]
		if gps_offset != -1:
			gps_tags = self.__read_tags(exif_data, gps_offset, _GPSTags, byte_order)

		inter_offset = -1
		if 'InteroperabilityIFDPointer' in tiff_tags:
			inter_offset = tiff_tags['InteroperabilityIFDPointer'][0]
		elif 'InteroperabilityIFDPointer' in exif_tags:
			inter_offset = exif_tags['InteroperabilityIFDPointer'][0]
		if inter_offset != -1:
			inter_tags = self.__read_tags(exif_data, inter_offset, _TiffTags | _ExifTags, byte_order)

		return (tiff_tags, exif_tags, gps_tags, inter_tags)

	def __read_tag_value(self, data:bytes, offset:int, tag:str, byte_order:str):
		tag_type = uint_16(data, offset + 2, byte_order)
		num_values = uint_32(data, offset + 4, byte_order)
		value_offset = uint_32(data, offset + 8, byte_order)
		values = []
		encoding = self._international_encoding

		# Processing for secial cases
		if tag in ['XPTitle', 'XPComment', 'XPAuthor', 'XPKeywords', 'XPSubject']: # windows tags all in utf_16
			if num_values <= 2:
				where_to_look = offset + 8
			else:
				where_to_look = value_offset
			# FIXME: byte_order for utf_16 can be different from the system where this code is run
			values.append(str_b(data, where_to_look, num_values, 'utf_16'))
			tag_type = -1
		elif tag == 'XMLPacket': # XMP data might often be stored as bytes, not ascii
			tag_type = 2

		# Orderly processing
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

				values.append(str_b(data, where_to_look, num_values, encoding))

			case 3: # short, 16 bit int
				if num_values <= 2:
					where_to_look = offset + 8
				else:
					where_to_look = value_offset
		
				values = [uint_16(data, where_to_look + i, byte_order) for i in range(num_values)]

			case 4: # 4 - long, 32 bit int
				if num_values == 1:
					where_to_look = offset + 8
				else:
					where_to_look = value_offset
		
				values = [uint_32(data, where_to_look + i, byte_order) for i in range(num_values)]

			case 5: # 5 - rational, two long values, first is numerator, second is denominator
				where_to_look = value_offset
				for i in range(num_values):
					numerator = uint_32(data, where_to_look + i*8, byte_order)
					denominator = uint_32(data, where_to_look + i*8 + 4, byte_order)
					values.append(str(numerator) + '/' + str(denominator))

			case 7: # 7 - undefined, value depending on field
				if num_values <= 4:
					where_to_look = offset + 8
				else:
					where_to_look = value_offset

				#values.append(str_b(data, where_to_look, num_values, encoding))
				values.append(data[where_to_look:where_to_look+num_values])
				if tag not in self._nonprintable_tags + ['ExifVersion', 'FlashpixVersion', 'InteroperabilityVersion']:
					self._nonprintable_tags.append(tag)
				
			case 9: # 9 - slong, 32 bit signed int.
				if num_values == 1:
					where_to_look = offset + 8
				else:
					where_to_look = value_offset
		
				values = [sint_32(data, where_to_look + i, byte_order) for i in range(num_values)]

			case 10: #10 - signed rational, two long values, first is numerator, second is denominator
				where_to_look = value_offset
				for i in range(num_values):
					numerator = sint_32(data, where_to_look + i*8, byte_order)
					denominator = sint_32(data, where_to_look + i*8 + 4, byte_order)
					values.append(str(numerator) + '/' + str(denominator))

			case _:
				pass

		return values

	def __read_tags(self, data:bytes, offset:int, tags_to_search:dict, byte_order:str):
		entries = uint_16(data, offset, byte_order)
		tags = {}

		for i in range(entries):
			entry_offset = offset + i * 12 + 2 # entry_offset is relevant to TIFF headers (i.e. 0x4949 or 0x4D4D byte order marker has an offset of 0
			tag_marker = uint_16(data, entry_offset, byte_order)
			if tag_marker in tags_to_search:
				key = tags_to_search[tag_marker]
			else:
				key = 'Tag 0x{0:04X} ({1:05})'.format(tag_marker, tag_marker)
			tags[key] = self.__read_tag_value(data, entry_offset, key, byte_order)
		
		return tags

	pass
