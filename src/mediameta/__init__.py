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
