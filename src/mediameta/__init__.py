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

from mediameta.tags import _TiffTags
from mediameta.tags import _ExifTags
from mediameta.tags import _GPSTags

from mediameta.mediametadata import UnsupportedMediaFile
from mediameta.mediametadata import MediaMetadata
from mediameta.mediametadata import str_to_rational
from mediameta.mediametadata import GPS_link

from mediameta.imagemetadata import ImageMetadata

from mediameta.videometadata import VideoMetadata

__version__ = '0.0.1'
