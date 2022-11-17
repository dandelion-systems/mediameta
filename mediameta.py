'''
	This file is part of mediameta Python module.

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
from functools import reduce
import os
import sys
from typing import Literal

class UnsupportedMediaFile(Exception):
	pass

_TiffTags = {
	0x0100: 'ImageWidth',
	0x0101: 'ImageHeight',
	0x0102: 'BitsPerSample',
	0x0103: 'Compression',
	0x0106: 'PhotometricInterpretation',
	0x010E: 'ImageDescription',
	0x010F: 'Make',
	0x0110: 'Model',
	0x0111: 'StripOffsets',
	0x0112: 'Orientation',
	0x0115: 'SamplesPerPixel',
	0x0116: 'RowsPerStrip',
	0x0117: 'StripByteCounts',
	0x011A: 'XResolution',
	0x011B: 'YResolution',
	0x011C: 'PlanarConfiguration',
	0x0128: 'ResolutionUnit',
	0x012D: 'TransferFunction',
	0x0131: 'Software',
	0x0132: 'DateTime',
	0x013B: 'Artist',
	0x013C: 'HostComputer',
	0x013E: 'WhitePoint',
	0x013F: 'PrimaryChromaticities',
	0x0201: 'JPEGInterchangeFormat',
	0x0202: 'JPEGInterchangeFormatLength',
	0x0211: 'YCbCrCoefficients',
	0x0212: 'YCbCrSubSampling',
	0x0213: 'YCbCrPositioning',
	0x0214: 'ReferenceBlackWhite',
	0x8298: 'Copyright',
	0x8769: 'ExifIFDPointer',
	0x8825: 'GPSInfoIFDPointer',
	0xA005: 'InteroperabilityIFDPointer'
}

_ExifTags = {
	0x0001: 'InteroperabilityIndex',
	0x0002: 'InteroperabilityVersion',
	0x1000: 'RelatedImageFileFormat',
	0x1001: 'RelatedImageWidth',
	0x1002: 'RelatedImageLength',
	0x829A: 'ExposureTime',
	0x829D: 'FNumber',
	0x8822: 'ExposureProgram',
	0x8824: 'SpectralSensitivity',
	0x8827: 'ISOSpeedRatings',
	0x8828: 'OECF',
	0x9000: 'ExifVersion',
	0x9003: 'DateTimeOriginal',
	0x9004: 'DateTimeDigitized',
	0x9101: 'ComponentsConfiguration',
	0x9102: 'CompressedBitsPerPixel',
	0x9201: 'ShutterSpeedValue',
	0x9202: 'ApertureValue',
	0x9203: 'BrightnessValue',
	0x9204: 'ExposureBias',
	0x9205: 'MaxApertureValue',
	0x9206: 'SubjectDistance',
	0x9207: 'MeteringMode',
	0x9208: 'LightSource',
	0x9209: 'Flash',
	0x920A: 'FocalLength',
	0x9214: 'SubjectArea',
	0x927C: 'MakerNote',
	0x9286: 'UserComment',
	0x9290: 'SubsecTime',
	0x9291: 'SubsecTimeOriginal',
	0x9292: 'SubsecTimeDigitized',
	0xA000: 'FlashpixVersion',
	0xA001: 'ColorSpace',
	0xA002: 'PixelXDimension',
	0xA003: 'PixelYDimension',
	0xA004: 'RelatedSoundFile',
	0xA005: 'InteroperabilityIFDPointer',
	0xA20B: 'FlashEnergy',
	0xA20C: 'SpatialFrequencyResponse',
	0xA20E: 'FocalPlaneXResolution',
	0xA20F: 'FocalPlaneYResolution',
	0xA210: 'FocalPlaneResolutionUnit',
	0xA214: 'SubjectLocation',
	0xA215: 'ExposureIndex',
	0xA217: 'SensingMethod',
	0xA300: 'FileSource',
	0xA301: 'SceneType',
	0xA302: 'CFAPattern',
	0xA401: 'CustomRendered',
	0xA402: 'ExposureMode',
	0xA403: 'WhiteBalance',
	0xA404: 'DigitalZoomRation',
	0xA405: 'FocalLengthIn35mmFilm',
	0xA406: 'SceneCaptureType',
	0xA407: 'GainControl',
	0xA408: 'Contrast',
	0xA409: 'Saturation',
	0xA40A: 'Sharpness',
	0xA40B: 'DeviceSettingDescription',
	0xA40C: 'SubjectDistanceRange',
	0xA420: 'ImageUniqueID',
	0xA430: 'CameraOwnerName',
	0xA431: 'BodySerialNumber',
	0xA432: 'LensSpecification',
	0xA433: 'LensMake',
	0xA434: 'LensModel',
	0xA435: 'LensSerialNumber',
	0xA500: 'Gamma'
}

_GPSTags = {
	0x0000: 'GPSVersionID',
	0x0001: 'GPSLatitudeRef',
	0x0002: 'GPSLatitude',
	0x0003: 'GPSLongitudeRef',
	0x0004: 'GPSLongitude',
	0x0005: 'GPSAltitudeRef',
	0x0006: 'GPSAltitude',
	0x0007: 'GPSTimeStamp',
	0x0008: 'GPSSatellites',
	0x0009: 'GPSStatus',
	0x000A: 'GPSMeasureMode',
	0x000B: 'GPSDOP',
	0x000C: 'GPSSpeedRef',
	0x000D: 'GPSSpeed',
	0x000E: 'GPSTrackRef',
	0x000F: 'GPSTrack',
	0x0010: 'GPSImgDirectionRef',
	0x0011: 'GPSImgDirection',
	0x0012: 'GPSMapDatum',
	0x0013: 'GPSDestLatitudeRef',
	0x0014: 'GPSDestLatitude',
	0x0015: 'GPSDestLongitudeRef',
	0x0016: 'GPSDestLongitude',
	0x0017: 'GPSDestBearingRef',
	0x0018: 'GPSDestBearing',
	0x0019: 'GPSDestDistanceRef',
	0x001A: 'GPSDestDistance',
	0x001B: 'GPSProcessingMethod',
	0x001C: 'GPSAreaInformation',
	0x001D: 'GPSDateStamp',
	0x001E: 'GPSDifferential',
	0x001F: 'GPSHPositioningError'
}

class MediaMetadata:
	
	_tags = {}				# must follow {'tag_name':[tag_values_list]} format even if there is only 1 value for tag_name

	_file_name = ''
	_file_extension = ''

	_international_encoding = ''

	def __init__(self, file_name:str, encoding:str = 'cp1251'):
		self._file_name = file_name

		_, ext = os.path.splitext(file_name)
		self._file_extension = ext.upper()

		self._international_encoding = encoding

	def __get_binary(self, byte_array:bytes, start_index:int, byte_count:int, byte_order:Literal['little','big'], signed=False):
		integers = [byte_array[start_index + i] for i in range(byte_count)]
		bytes = [integer.to_bytes(1, byte_order, signed=signed) for integer in integers]
		return reduce(lambda a, b: a + b, bytes)

	def _get_uint_32(self, byte_array:bytes, start_index:int, byte_order:Literal['little','big']):
		return int.from_bytes(self.__get_binary(byte_array, start_index, 4, byte_order), byte_order)

	def _get_uint_16(self, byte_array:bytes, start_index:int, byte_order:Literal['little','big']):
		return int.from_bytes(self.__get_binary(byte_array, start_index, 2, byte_order), byte_order)

	def _get_uint_8(self, byte_array:bytes, start_index:int, byte_order:Literal['little','big']):
		return int.from_bytes(self.__get_binary(byte_array, start_index, 1, byte_order), byte_order)

	def _get_sint_32(self, byte_array:bytes, start_index:int, byte_order:Literal['little','big']):
		return int.from_bytes(self.__get_binary(byte_array, start_index, 4, byte_order), byte_order, signed=True)

	def _get_sint_16(self, byte_array:bytes, start_index:int, byte_order:Literal['little','big']):
		return int.from_bytes(self.__get_binary(byte_array, start_index, 2, byte_order), byte_order, signed=True)
	
	def _get_sint_8(self, byte_array:bytes, start_index:int, byte_order:Literal['little','big']):
		return int.from_bytes(self.__get_binary(byte_array, start_index, 1, byte_order), byte_order, signed=True)

	def _get_str(self, byte_array:bytes, start_index:int, byte_count:int):
		bytes_list = []
		integers = [byte_array[start_index + i] for i in range(byte_count)]
		for integer in integers:
			if integer != 0:
				bytes_list.append(integer.to_bytes(1, sys.byteorder, signed=False))
			else:
				break
		bytes = b''.join(bytes_list)
		return bytes.decode(encoding=self._international_encoding, errors='replace')
	
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
		
		(tiff_tags, exif_tags, gps_tags) = self.__interpret_meta_data(raw_meta_data)

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

		# APP1 is mandatory FIRST marker after SOI (EXIF 2.3, p4.5.5, Table 2 - page 6)
		# Search for APP1 marker 0xFFE1 with big endian byte order.
		offset = 2
		f.seek(offset)
		b2 = int.from_bytes(f.read(2), byteorder='big')
		offset += 2
		while b2 != 0xFFE1 and offset < file_size - 2:
			b2 = int.from_bytes(f.read(2), byteorder='big')
			f.seek(offset + b2)
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
		for i in range(metadata_size-4): # '-4' as we are reading by 4-byte values and the last 3 readings would otherwise go out of range
			b4 = data[i:i+4]
			if b4 == b'Exif':
				exif_offset = i
			elif b4 == b'iloc':
				iloc_offset = i

		if exif_offset == -1 or iloc_offset == -1:
			return exif_raw_data

		exif_item_index = self._get_uint_16(byte_array=data, start_index=exif_offset - 4, byte_order='big')

		# Scan through ilocs to find exif item location
		i = iloc_offset + 12
		while i < metadata_size - 16:
			item_index = self._get_uint_16(byte_array=data, start_index=i, byte_order='big')

			if item_index == exif_item_index:
				exif_location = self._get_uint_32(byte_array=data, start_index=i + 8, byte_order='big')
				exif_size = self._get_uint_32(byte_array=data, start_index=i + 12, byte_order='big')
				# Check prefix at exif exifOffset
				f.seek(exif_location)
				prefix_size = 4 + int.from_bytes(f.read(4), byteorder='big')
				f.seek(exif_location + prefix_size)
				exif_raw_data = f.read(exif_size)
				break

			i += 16

		return exif_raw_data

	def __interpret_meta_data(self, exif_data:bytes):
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
		if self._get_uint_16(byte_array=exif_data, start_index=2, byte_order=byte_order) != 0x002A:
			return (tiff_tags, exif_tags, gps_tags)

		ifd1_offset = self._get_uint_32(byte_array=exif_data, start_index=4, byte_order=byte_order)

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

		return (tiff_tags, exif_tags, gps_tags)

	def __read_tag_value(self, data:bytes, offset:int, tag:int, byte_order:str):
		tag_type = self._get_uint_16(byte_array=data, start_index=offset + 2, byte_order=byte_order)
		num_values = self._get_uint_32(byte_array=data, start_index=offset + 4, byte_order=byte_order)
		value_offset = self._get_uint_32(byte_array=data, start_index=offset + 8, byte_order=byte_order)
		values = []

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

				values.append(self._get_str(byte_array=data, start_index=where_to_look, byte_count=num_values-1))

			case 3: # short, 16 bit int
				if num_values <= 2:
					where_to_look = offset + 8
				else:
					where_to_look = value_offset
		
				values = [self._get_uint_16(byte_array=data, start_index=where_to_look + i, byte_order=byte_order) for i in range(num_values)]

			case 4: # 4 - long, 32 bit int
				if num_values == 1:
					where_to_look = offset + 8
				else:
					where_to_look = value_offset
		
				values = [self._get_uint_32(byte_array=data, start_index=where_to_look + i, byte_order=byte_order) for i in range(num_values)]

			case 5: # 5 - rational, two long values, first is numerator, second is denominator
				where_to_look = value_offset
				for i in range(num_values):
					numerator = self._get_uint_32(byte_array=data, start_index=where_to_look + i*8, byte_order=byte_order)
					denominator = self._get_uint_32(byte_array=data, start_index=where_to_look + i*8 + 4, byte_order=byte_order)
					values.append(str(numerator) + '/' + str(denominator))

			case 7: # 7 - undefined, value depending on field
				if num_values <= 4:
					where_to_look = offset + 8
				else:
					where_to_look = value_offset

				values.append(self._get_str(byte_array=data, start_index=where_to_look, byte_count=num_values))
				#values.append(_MediaMetadata__get_binary(self, byte_array=data, start_index=where_to_look, byte_count=num_values, byte_order=byte_order))
			
			case 9: # 9 - slong, 32 bit signed int.
				if num_values == 1:
					where_to_look = offset + 8
				else:
					where_to_look = value_offset
		
				values = [self._get_sint_32(byte_array=data, start_index=where_to_look + i, byte_order=byte_order) for i in range(num_values)]

			case 10: #10 - signed rational, two long values, first is numerator, second is denominator
				where_to_look = value_offset
				for i in range(num_values):
					numerator = self._get_sint_32(byte_array=data, start_index=where_to_look + i*8, byte_order=byte_order)
					denominator = self._get_sint_32(byte_array=data, start_index=where_to_look + i*8 + 4, byte_order=byte_order)
					values.append(str(numerator) + '/' + str(denominator))

		return values

	def __read_tags(self, data:bytes, offset:int, tags_to_search:dict, byte_order:str):
		entries = self._get_uint_16(data, offset, byte_order)
		tags = {}

		for i in range(entries):
			entry_offset = offset + i * 12 + 2 # entry_offset is relevant to TIFF headers (i.e. 0x4949 or 0x4D4D byte order marker has an offset of 0
			tag_marker = self._get_uint_16(byte_array=data, start_index=entry_offset, byte_order=byte_order)
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
			key = self._get_str(tags_list[i][0], 0, len(tags_list[i][0]))
			value = self._get_str(tags_list[i][1], 0, len(tags_list[i][1]))
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
