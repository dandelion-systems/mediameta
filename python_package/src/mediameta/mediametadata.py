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

class UnsupportedMediaFile(Exception):
	pass

class MediaMetadata:
	# _tags follows {'tag_name':[tag_values_list]} format even if there is only 1 value for tag_name
	_tags = {}				

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
			if key not in self._nonprintable_tags:
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
