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

# TIFF/EXIF tags
from .tags import _TiffTags
from .tags import _ExifTags
from .tags import _GPSTags

from .dataroutines import str_b

# Interpreters - dictionaries
Orientation = {
	1: 'Straight',
	2: 'Flipped horizontally',
	3: 'Flipped horizontally and vertically',
	4: 'Flipped vertically',
	5: 'Flipped vertically and turned 90 degrees clockwise',
	6: 'Turned 90 degress counterclockwise',
	7: 'Flipped vertically and turned 90 degrees counterclockwise',
	8: 'Turned 90 degress clockwise'
}

ExposureProgram = {
	0: 'Not defined',
	1: 'Manual',
	2: 'Normal program',
	3: 'Aperture priority',
	4: 'Shutter priority',
	5: 'Creative program',
	6: 'Action program',
	7: 'Portrait mode',
	8: 'Landscape mode'
}

MeteringMode = {
	0: 'Unknown',
	1: 'Average',
	2: 'CenterWeightedAverage',
	3: 'Spot',
	4: 'MultiSpot',
	5: 'Pattern',
	6: 'Partial',
	255: 'Other'
}

LightSource = {
	0: 'Unknown',
	1: 'Daylight',
	2: 'Fluorescent',
	3: 'Tungsten (incandescent light)',
	4: 'Flash',
	9: 'Fine weather',
	10: 'Cloudy weather',
	11: 'Shade',
	12: 'Daylight fluorescent (D 5700 - 7100K)',
	13: 'Day white fluorescent (N 4600 - 5400K)',
	14: 'Cool white fluorescent (W 3900 - 4500K)',
	15: 'White fluorescent (WW 3200 - 3700K)',
	17: 'Standard light A',
	18: 'Standard light B',
	19: 'Standard light C',
	20: 'D55',
	21: 'D65',
	22: 'D75',
	23: 'D50',
	24: 'ISO studio tungsten',
	255: 'Other'
}

Flash = {
	0x0000: 'Flash did not fire',
	0x0001: 'Flash fired',
	0x0005: 'Strobe return light not detected',
	0x0007: 'Strobe return light detected',
	0x0009: 'Flash fired, compulsory flash mode',
	0x000D: 'Flash fired, compulsory flash mode, return light not detected',
	0x000F: 'Flash fired, compulsory flash mode, return light detected',
	0x0010: 'Flash did not fire, compulsory flash mode',
	0x0018: 'Flash did not fire, auto mode',
	0x0019: 'Flash fired, auto mode',
	0x001D: 'Flash fired, auto mode, return light not detected',
	0x001F: 'Flash fired, auto mode, return light detected',
	0x0020: 'No flash function',
	0x0041: 'Flash fired, red-eye reduction mode',
	0x0045: 'Flash fired, red-eye reduction mode, return light not detected',
	0x0047: 'Flash fired, red-eye reduction mode, return light detected',
	0x0049: 'Flash fired, compulsory flash mode, red-eye reduction mode',
	0x004D: 'Flash fired, compulsory flash mode, red-eye reduction mode, return light not detected',
	0x004F: 'Flash fired, compulsory flash mode, red-eye reduction mode, return light detected',
	0x0059: 'Flash fired, auto mode, red-eye reduction mode',
	0x005D: 'Flash fired, auto mode, return light not detected, red-eye reduction mode',
	0x005F: 'Flash fired, auto mode, return light detected, red-eye reduction mode'
}

SensingMethod = {
	1: 'Not defined',
	2: 'One-chip color area sensor',
	3: 'Two-chip color area sensor',
	4: 'Three-chip color area sensor',
	5: 'Color sequential area sensor',
	7: 'Trilinear sensor',
	8: 'Color sequential linear sensor'
}

SceneCaptureType = {
	0: 'Standard',
	1: 'Landscape',
	2: 'Portrait',
	3: 'Night scene'
}

SceneType = {
	1: 'Directly photographed'
}

CustomRendered = {
	0: 'Normal process',
	1: 'Custom process'
}

WhiteBalance = {
	0: 'Auto white balance',
	1: 'Manual white balance'
}

GainControl = {
	0: 'None',
	1: 'Low gain up',
	2: 'High gain up',
	3: 'Low gain down',
	4: 'High gain down'
}

Contrast = {
	0: 'Normal',
	1: 'Soft',
	2: 'Hard'
}

Saturation = {
	0: 'Normal',
	1: 'Low saturation',
	2: 'High saturation'
}

Sharpness = {
	0: 'Normal',
	1: 'Soft',
	2: 'Hard'
}

SubjectDistanceRange = {
	0: 'Unknown',
	1: 'Macro',
	2: 'Close view',
	3: 'Distant view'
}

FileSource = {
	3: 'DSC'
}

Components = {
	0: '',
	1: 'Y',
	2: 'Cb',
	3: 'Cr',
	4: 'R',
	5: 'G',
	6: 'B'
}

ResolutionUnit = {
	1: '',
	2: 'in',
	3: 'cm'
}
FocalPlaneResolutionUnit = ResolutionUnit

PhotometricInterpretation = {
	0: 'White is zero',
	1: 'Black is zero',
	2: 'RGB',
	3: 'Palette color',
	4: 'Transparency Mask',
	5: 'Seperated (CMYK)',
	6: 'YCbCr',
	8: 'CIE L*a*b*',
	9: 'ICC L*a*b*',
	10: 'ITU L*a*b*',
	32844: 'Pixar LogL',
	32845: 'Pixar LogLuv',
	32803: 'CFA (Color Filter Array)',
	34892: 'LinearRaw',
	51177: 'Depth'
}

Compression = {
	1: 'No compression',
	2: 'CCITT Group 3 1-Dimensional Modified Huffman run-length encoding',
	3: 'CCITT Group 3 fax encoding',
	4: 'CCITT Group 4 fax encoding',
	5: 'LZW',
	6: 'JPEG (old-style)',
	7: 'JPEG',
	8: 'Deflate (Adobe)',
	9: 'JBIG on black and white',
	10: 'JBIG on color',
	32773: 'PackBits compression',
	34892: 'Lossy JPEG'
}

PlanarConfiguration = {
	1: 'Chunky',
	2: 'Planar'
}

YCbCrPositioning = {
	1: 'Centered',
	2: 'Cosited'
}

ColorSpace = {
	0x0001: 'sRGB',
	0xFFFF: 'Uncalibrated'
}

ExposureMode = {
	0: 'Auto exposure',
	1: 'Manual exposure',
	2: 'Auto bracket'
}

Predictor = {
	1: 'No prediction scheme used before coding',
	2: 'Horizontal differencing',
	3: 'Floating point horizontal differencing'
}

GPSAltitudeRef = {
	0: 'Above sea level',
	1: 'Below sea level'
}

GPSSpeedRef = {
	'K': 'km/h',
	'M': 'miles/h',
	'N': 'knots'
}

GPSImgDirectionRef = {
	'T': 'True',
	'M': 'Magnetic'
}

GPSDestBearingRef = GPSImgDirectionRef

# Interpreters - functions
def str_to_rational(a:str) -> (int | float):
	n, d = list(map(int, a.split('/')))
	return int(n/d) if n % d == 0 else n/d

def format_rational(x:int | float, num_digits:int = 2) -> str:
	return str(x) if isinstance(x, int) else str(round(x, num_digits))

def ExifVersion(v):
	vbytes = v[0]
	major = str_b(vbytes[0:2],0,2)
	if major[0] == '0': major = major[1:2]
	minor = str_b(vbytes[2:4],0,2)
	if minor[1] == '0': minor = minor[0:1]
	return [major + '.' + minor, ]

FlashpixVersion = ExifVersion
InteroperabilityVersion = ExifVersion

def ExposureTime(t):
	return [t[0] + ' sec', ]

def ShutterSpeedValue(v):
	return [format_rational(str_to_rational(v[0])) + ' Ev', ]

ApertureValue = ShutterSpeedValue
ExposureBiasValue = ShutterSpeedValue
MaxApertureValue = ShutterSpeedValue

def BrightnessValue(a):
	n, d = list(map(int, a[0].split('/')))
	if n == 0xFFFFFFFF:
		return 'Unknown'
	bv = str(int(n/d)) if n % d == 0 else str(round(n/d,2))
	return bv + ' Ev'

def FocalLength(f):
	return [str(str_to_rational(f[0])) + ' mm', ]

def FocalLengthIn35mmFilm(f):
	return ['Unknown' if f[0] == 0 else str(f[0]) + ' mm', ]

def LensSpecification(s):
	min_focal_length = 'f min = ' + format_rational(str_to_rational(s[0])) + ' mm'
	max_focal_length = 'f max = ' + format_rational(str_to_rational(s[1])) + ' mm'
	try:
		min_fn_min_lngth = 'f/' + format_rational(str_to_rational(s[2]))
	except ZeroDivisionError:
		min_fn_min_lngth = 'F number unknown'
	try:
		min_fn_max_lngth = 'f/' + format_rational(str_to_rational(s[3]))
	except ZeroDivisionError:
		min_fn_max_lngth = 'F number unknown'
	#return [min_focal_length, max_focal_length, min_fn_min_lngth, min_fn_max_lngth]
	return [min_focal_length + ' (' + min_fn_min_lngth + '), ' + max_focal_length + ' (' + min_fn_max_lngth + ')', ]

def FNumber(f):
	return ['f/' + format_rational(str_to_rational(f[0])), ]

def GPSLatitude(lat):
	coord = list(map(lambda x:format_rational(str_to_rational(x)), lat))
	return [coord[0] + '\xB0' + coord[1] + '\'' + coord[2] + '"', ]

GPSLongitude = GPSLatitude

def GPSHPositioningError(err):
	return list(map(lambda x:format_rational(str_to_rational(x)) + ' m', err))

def GPSAltitude(alt):
	return list(map(lambda x:format_rational(str_to_rational(x)) + ' m', alt))

def GPSSpeed(s):
	return list(map(lambda x:format_rational(str_to_rational(x)), s))

def GPSImgDirection(d):
	return list(map(lambda x:format_rational(str_to_rational(x)) + '\xB0', d))

GPSDestBearing = GPSImgDirection

def GPSVersionID(id):
	return [str(id[0]) + '.' + str(id[1]) + '.' + str(id[2]) + '.' + str(id[3]), ]

def GPS_link(lat:str, lat_ref:str, lng:str, lng_ref:str, service:str='google') -> str:
	'''
		GPS Maps links - returns an url to a maps service with a pin at the specified location

		lat and lng are latitude and longitude respectively in the form 41°04'0.6"

		lat_ref and lng_ref are references for lat and lng, either 'N'/'S' or 'E'/'W' respectively
		
		service is one of 'google', 'yandex', 'osm' or 'bing'

		Sample results:
		https://www.google.com/maps/place/41.066833,29.019294
		https://yandex.com/maps/?ll=29.019294,41.066833&pt=29.019294,41.066833&z=17&l=map
		https://www.openstreetmap.org/?mlat=41.066833&mlon=29.019294#map=17/41.066833/29.019294
		https://www.bing.com/maps?cp=41.066833~long&lvl=17&sp=point.41.066833_29.019294_Photo%20GPS%20location
	'''
	url = ''

	d, ms = lat.split('\xB0')
	m, s = ms.split('\'')
	s, _ = s.split('"')
	latitude = float(d) + float(m)/60 + float(s)/3600
	if lat_ref == 'S': latitude = -latitude

	d, ms = lng.split('\xB0')
	m, s = ms.split('\'')
	s, _ = s.split('"')
	longitude = float(d) + float(m)/60 + float(s)/3600
	if lng_ref == 'W': longitude = -longitude

	match service:
		case 'google':
			url = f'https://www.google.com/maps/place/{latitude},{longitude}'
		case 'yandex':
			url = f'https://yandex.com/maps/?ll={longitude},{latitude}&pt={longitude},{latitude}&z=17&l=map'
		case 'osm':
			url = f'https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}#map=17/{latitude}/{longitude}'
		case 'bing':
			url = f'https://www.bing.com/maps?cp={latitude}~{longitude}&lvl=17&sp=point.{latitude}_{longitude}_Photo%20GPS%20location'
		case _:
			raise ValueError

	return url

class UnsupportedMediaFile(Exception):
	pass

class MediaMetadata:
	# _tags follows {'tag_name':[tag_values_list]} format even if there is only 1 value for tag_name
	_tags = {}
	_interpreted_tags = {}
	_interpreters = {}

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

	def assign_interpreter(self, tag: str, interpreter):
		self._interpreters[tag] = interpreter

	def drop_interpreter(self, tag:str):
		if tag in self._interpreters:
			del self._interpreters[tag]

	def interpret(self):
		i_tags = {}
		for key in self.keys():
			values = self._tags[key]
			try: 			# try to use an interpreter
				interpreter = self._interpreters[key] if key in self._interpreters else globals()[key]
				if callable(interpreter):
					i_tags[key] = interpreter(values)
				elif isinstance(interpreter, dict):
					i_tags[key] = list(map(lambda x:interpreter[x],values))
				else:
					i_tags[key] = values 
			except: 		# no or faulty interpreter
				try:		# so, try to convert a rational value to decimal form
					i_tags[key] = list(map(lambda x:r if isinstance((r:=str_to_rational(x)), int) else round(r, 2), values))
				except:		# no joy, leave the value as is
					i_tags[key] = values

		self._interpreted_tags = i_tags

	def revert_interpretation(self):
		self._interpreted_tags = {}

	pass
