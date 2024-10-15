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

	SPDX-License-Identifier: GPL-3.0-or-later
'''

from .tags import _TiffTags
from .tags import _ExifTags
from .tags import _GPSTags

from .mediametadata import UnsupportedMediaFile
from .mediametadata import MediaMetadata
from .mediametadata import str_to_rational
from .mediametadata import format_rational
from .mediametadata import GPS_link

from .imagemetadata import ImageMetadata

from .videometadata import VideoMetadata

__version__ = '0.2.0'
