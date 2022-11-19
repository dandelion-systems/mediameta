# Metadata extractor from image and video files

Version 0.1 (initial release)

`mediameta` provides `ImageMetadata` and `VideoMetadata` classes which facilitate extracting metadata information from media files. `mediameta` was written and will be maintained without thrid-party image manupulation libraries or modules as they might be licensed. `mediameta` is distributed under GNU General Public License.
Copyright 2022 Dandelion Systems <dandelion.systems at gmail.com>

`mediameta` was inspired and partially based on:
1. [exiftool](https://github.com/exiftool/exiftool) by Phil Harvey
2. [exif-heic-js](https://github.com/exif-heic-js/exif-heic-js), copyright (c) 2019 Jim Liu

Currently `ImageMetadata` class supports

* JPEG
* HEIC
* TIFF

file formats. Depending on the content of the metadata fields available in a file it extracts **TIFF** headers, **EXIF** data and **GPS** data.

> Please note that the current implementation loads entire TIFF files into memory for processing and is therefore not recommended for use with TIFF files as they might get very big. JPEG and HEIC files are handled optimally by loading only the metadata into memory.

`VideoMetadata` class only supports Apple QuickTime MOV files in this release. It extracts all metadata it finds in the moov/meta atom of the file.

## Usage summary

The usage of both classes is straigthforward. Just instaciate them supplying the name of the media file. In case the constructor cannot understand what the file is, it throws an `UnsupportedMediaFile` exception. For example

	import mediameta as mm
	import os

	# Iterate through files in a given directory
	for f in os.scandir('./img'):
		# Skip subdirectories and links
		if not f.is_file(follow_symlinks=False):
			continue

		# Try and load the metadata
		try:
			meta_data = mm.ImageMetadata(f.path)
		except mm.UnsupportedMediaFile:
			print(f.path + ' - format is not supported.')
			continue

		# If success show it
		print('Metadata in ' + f.path)
		print(meta_data)

`mediameta` module declares image metadata keys in three dictionaries

* _TiffTags
* _ExifTags
* _GPSTags

> Note: some keys defined by the latest revisions of the EXIF standard and the keys defined by invidiual equipment and software vendors are not declared. However, such keys will be read and stored as `Tag 0xXXXX (DDDDD)`. XXXX and DDDDD stand for hexadecimal and decimal values of the unknown tag respectively.

If you wish to obtain individual key values from a file's metadata, you should use the literals from these dictionaries as keys to index the object of `ImageMetadata`. For instance, the `print()` calls in the example above could look like this:

		print('Metadata in ' + f.path)
		print('Picture taken on ' + meta_data['DateTimeOriginal'])
		print('at the location with GPS coordinates')
		print(meta_data['GPSLatitude'] + meta_data['GPSLatitudeRef'])
		print(meta_data['GPSLongitude'] + meta_data['GPSLongitudeRef'])

A dictionary with metadata keys for `VideoMetadata` is not included as these keys are stored in the MOV files by their literal names. Apple defines a set of such literals in its [developer documentation](https://developer.apple.com/library/archive/documentation/QuickTime/QTFF/Metadata/Metadata.html#//apple_ref/doc/uid/TP40000939-CH1-SW43). You are encouraged to use the keys listed in [Tables 3-6 and 3-7 of Apple developer documentation](https://developer.apple.com/library/archive/documentation/QuickTime/QTFF/Metadata/Metadata.html#//apple_ref/doc/uid/TP40000939-CH1-SW43) to try and retrieve metadata from Quicktime MOV files but the result is not guaranteed. It all depends on the author of the video file. Alternatively, you can iterate through `keys()` or `all()` to get all the metadata we could collect from a MOV file and then decide which ones you need. For instance, the videos taken with iPhones are likely to have at least these metadata keys:

* com.apple.quicktime.make
* com.apple.quicktime.model
* com.apple.quicktime.software
* com.apple.quicktime.creationdate
* com.apple.quicktime.location.ISO6709

## Data model

Both `ImageMetadata` and `VideoMetadata` are subclasses of `MediaMetadata` which is a dummy class providing declarations of common fields, binary data manipulation methods, and metadata access methods. The latter is documented below. You should never need to instaciate the top level class.

`__init__(file_name:str, encoding:str = 'cp1251')` - the constructor, this is where all metadata is scanned in `ImageMetadata` and `VideoMetadata`. It requires just the name of the file containing media. `encoding` is optional and used to decode string values from byte sequences in the metadata. The deafult decodes Latin and Cyrillic (Russian) characters without a problem. `encoding` should be one of Python supported [Standard encodings](https://docs.python.org/3/library/codecs.html#standard-encodings). In case decoding fails the offending symbols in a string will be replaced with � (U+FFFD).

`__getitem__(key:str)` - retrieves the metadata value for a specific `key` allowing the objects of `MediaMetadata` and its descendants to be indexed with `[]`. If the `key` is not present in the file's headers an empty list is returned. If the `key` is present and a single value is stored under it, this value is returned. If the `key` holds mulptiple values like, for instance, in the case of GPS coordinates, they are returned as a list.

> Note: Rational type values are returned as '_numerator_/_denominator_' strings. For example, in the case of `ExposureTime` tag you will see something like `'1/3003'` as its value. This is done to preserve the original metadata and to avoid division by zero as might happen, for instance, in `LensSpecification` tag recording an unknown F number in `0/0` notation.

`__str__()` - casts the object to `str` type returning a string of tab separated metadata key/value pairs found in the media file each followed by a line separator. The format of values follows the logic documented for `__getitem__()`. Useful to import the data into a spreadsheet. Or if you are creaing a command line tool, the output can be fed to `awk` for further processing.

`all()` - a generator yielding tuples of `(key, value)` found in the media file. The format of values follows the logic documented for `__getitem__()`.

`keys()` - returns a `list` of all keys found in the media file.

`file_name()` and `file_extension()` - return the file name that was supplied to the class constructor and the capitalised extesion respectively. The extesion can be used in further releases/forks to manipulate the metadata which implies knowing the original file type.