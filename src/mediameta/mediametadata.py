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

# TIFF/EXIF tags
from mediameta.tags import _TiffTags
from mediameta.tags import _ExifTags
from mediameta.tags import _GPSTags

# Interpreters - dictionaries
from mediameta.tags import Orientation
from mediameta.tags import ExposureProgram
from mediameta.tags import MeteringMode
from mediameta.tags import LightSource
from mediameta.tags import Flash
from mediameta.tags import SensingMethod
from mediameta.tags import SceneCaptureType
from mediameta.tags import SceneType
from mediameta.tags import CustomRendered
from mediameta.tags import GainControl
from mediameta.tags import WhiteBalance
from mediameta.tags import Contrast
from mediameta.tags import Saturation
from mediameta.tags import Sharpness
from mediameta.tags import SubjectDistanceRange
from mediameta.tags import FileSource
from mediameta.tags import Components
from mediameta.tags import ResolutionUnit
from mediameta.tags import FocalPlaneResolutionUnit
from mediameta.tags import PhotometricInterpretation
from mediameta.tags import Compression
from mediameta.tags import PlanarConfiguration
from mediameta.tags import YCbCrPositioning
from mediameta.tags import ColorSpace
from mediameta.tags import ExposureMode
from mediameta.tags import Predictor
from mediameta.tags import GPSAltitudeRef
from mediameta.tags import GPSSpeedRef
from mediameta.tags import GPSImgDirectionRef
from mediameta.tags import GPSDestBearingRef

# Interpreters - functions
def str_to_rational(a:str):
	n, d = list(map(int, a.split('/')))
	return int(n/d) if n % d == 0 else n/d

def GPSLatitude(lat):
	coord = list(map(str, map(str_to_rational, lat)))
	return [coord[0] + '\xB0' + coord[1] + '\'' + coord[2] + '"', ]

GPSLongitude = GPSLatitude

def GPSHPositioningError(err):
	return list(map(lambda x:str(str_to_rational(x)) + ' m', err))

def GPSAltitude(alt):
	return list(map(lambda x:str(str_to_rational(x)) + ' m', alt))

def GPSSpeed(s):
	return list(map(lambda x:'{0:.2f}'.format(str_to_rational(x)), s))

def GPSImgDirection(d):
	return list(map(lambda x:'{0:.2f}'.format(str_to_rational(x)) + '\xB0', d))

GPSDestBearing = GPSImgDirection

#https://www.google.com/maps/place/41°04'0.6"N29°01'9.46"E
#https://yandex.com/maps/?ll=float,float&pt=float,float&z=12&l=map
# see https://yandex.com/dev/yandex-apps-launch/maps/doc/concepts/yandexmaps-web.html
def GPS_link(lat:str, lat_ref:str, lng:str, lng_ref:str, service:str='google') -> str:
	match service:
		case 'google':
			return 'https://www.google.com/maps/place/' + lat + lat_ref + lng + lng_ref
		case 'yandex':
			d, ms = lat.split('\xB0')
			m, s = ms.split('\'')
			s, _ = s.split('"')
			latitude = float(d) + float(m)/60 + float(s)/3600
			if lat_ref == 'S': latitude = -latitude
			d, ms = lng.split('\xB0')
			m, s = ms.split('\'')
			s, _ = s.split('"')
			longtitude = float(d) + float(m)/60 + float(s)/3600
			if lng_ref == 'W': longtitude = -longtitude
			coord = str(longtitude) + ',' + str(latitude)
			return 'https://yandex.com/maps/?ll=' + coord + '&pt=' + coord + '&z=17'
		case _:
			raise ValueError

class UnsupportedMediaFile(Exception):
	pass

class MediaMetadata:
	# _tags follows {'tag_name':[tag_values_list]} format even if there is only 1 value for tag_name
	_tags = {}
	_interpreted_tags = {}				

	_nonprintable_tags = []

	_file_name = ''
	_file_extension = ''

	_international_encoding = ''

	def __init__(self, file_name:str, encoding:str = 'utf_8'):
		self._file_name = file_name

		_, ext = os.path.splitext(file_name)
		self._file_extension = ext.upper()

		self._international_encoding = encoding
	
	def __getitem__(self, key:str):
		value = []

		tags = self._interpreted_tags if self._interpreted_tags != {} else self._tags

		if key in tags:
			value = tags[key]

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
			if key not in self._nonprintable_tags:
				as_string += key + '\t' + str(value) + os.linesep
		return as_string

	def all(self):
		for key in self.keys():
			yield (key,self[key])

	def keys(self):
		return list(self._tags.keys())

	def file_name(self):
		return self._file_name

	def file_type(self):
		return self._file_extension

	def interpret(self):
		i_tags = {}
		for key in self.keys():
			values = self._tags[key]
			try:
				interpreter = globals()[key]
				if callable(interpreter):
					i_tags[key] = interpreter(values)
				elif isinstance(interpreter, dict):
					i_tags[key] = list(map(lambda x:interpreter[x],values))
				else:
					i_tags[key] = values
			except:
				i_tags[key] = values

		self._interpreted_tags = i_tags

	def revert_interpretation(self):
		self._interpreted_tags = {}

	pass
