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
from typing import Literal
from struct import unpack_from

def uint_32(byte_array:bytes, start_index:int, byte_order:Literal['little','big']) -> int:
	format = '<' if byte_order == 'little' else '>'
	format += 'I'
	return unpack_from(format, buffer=byte_array, offset=start_index)[0]

def uint_16(byte_array:bytes, start_index:int, byte_order:Literal['little','big']) -> int:
	format = '<' if byte_order == 'little' else '>'
	format += 'H'
	return unpack_from(format, buffer=byte_array, offset=start_index)[0]

def uint_8(byte_array:bytes, start_index:int, byte_order:Literal['little','big']) -> int:
	format = '<' if byte_order == 'little' else '>'
	format += 'B'
	return unpack_from(format, buffer=byte_array, offset=start_index)[0]

def sint_32(byte_array:bytes, start_index:int, byte_order:Literal['little','big']) -> int:
	format = '<' if byte_order == 'little' else '>'
	format += 'i'
	return unpack_from(format, buffer=byte_array, offset=start_index)[0]

def sint_16(byte_array:bytes, start_index:int, byte_order:Literal['little','big']) -> int:
	format = '<' if byte_order == 'little' else '>'
	format += 'h'
	return unpack_from(format, buffer=byte_array, offset=start_index)[0]

def sint_8(byte_array:bytes, start_index:int, byte_order:Literal['little','big']) -> int:
	format = '<' if byte_order == 'little' else '>'
	format += 'b'
	return unpack_from(format, buffer=byte_array, offset=start_index)[0]

def str_b(byte_array:bytes, start_index:int, byte_count:int, encoding:str = 'utf_8') -> str:
	bytes_str = unpack_from(str(byte_count)+'s', buffer=byte_array, offset=start_index)[0]
	# rarely, a zero terminator would penetrate the result (even in the middle of the string)
	# due to a bug in photo software. And in any case, strings are 0-terminated, so we
	# need to remove '\x00' to get rid of binary data in print.
	return bytes_str.decode(encoding=encoding, errors='replace').split('\x00')[0] 