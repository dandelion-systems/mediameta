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
from typing import Literal
from struct import unpack_from

def uint_32(byte_array:bytes, start_index:int, byte_order:Literal['little','big']):
	format = '<' if byte_order == 'little' else '>'
	format += 'I'
	return unpack_from(format, buffer=byte_array, offset=start_index)[0]

def uint_16(byte_array:bytes, start_index:int, byte_order:Literal['little','big']):
	format = '<' if byte_order == 'little' else '>'
	format += 'H'
	return unpack_from(format, buffer=byte_array, offset=start_index)[0]

def uint_8(byte_array:bytes, start_index:int, byte_order:Literal['little','big']):
	format = '<' if byte_order == 'little' else '>'
	format += 'B'
	return unpack_from(format, buffer=byte_array, offset=start_index)[0]

def sint_32(byte_array:bytes, start_index:int, byte_order:Literal['little','big']):
	format = '<' if byte_order == 'little' else '>'
	format += 'i'
	return unpack_from(format, buffer=byte_array, offset=start_index)[0]

def sint_16(byte_array:bytes, start_index:int, byte_order:Literal['little','big']):
	format = '<' if byte_order == 'little' else '>'
	format += 'h'
	return unpack_from(format, buffer=byte_array, offset=start_index)[0]

def sint_8(byte_array:bytes, start_index:int, byte_order:Literal['little','big']):
	format = '<' if byte_order == 'little' else '>'
	format += 'b'
	return unpack_from(format, buffer=byte_array, offset=start_index)[0]

def str_b(byte_array:bytes, start_index:int, byte_count:int, encoding:str):
	bytes_str = unpack_from(str(byte_count)+'s', buffer=byte_array, offset=start_index)[0]
	# rarely, a zero terminator would penetrate the result (even in the middle of the string)
	# due to a bug in photo software. And in any case, strings are 0-terminated, so we
	# need to remove '\x00' to get rid of binary data in print.
	return bytes_str.decode(encoding=encoding, errors='replace').split('\x00')[0] 