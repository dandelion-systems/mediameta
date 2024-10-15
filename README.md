# Metadata extractor from image and video files

`mediameta` provides `ImageMetadata` and `VideoMetadata` classes which facilitate extracting metadata information from media files. `mediameta` was written and will be maintained without thrid-party image manupulation libraries or modules as they might be licensed. As of release 0.2.0 `mediameta` is distributed under MIT License, the previous releases were provided under GNU General Public License version 3.

Install it from PyPi with 

	pip install mediameta

If you run Python in a managed environment, you should have created a venv prior to attempting the installation. If the venv is in ~/venv, the installtion command would look like

	~/venv/bin/pip install mediameta
	
See https://github.com/dandelion-systems/mediautilities for usage samples.

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

> Note: some keys defined by the latest revisions of the EXIF standard, especially the ones used by some equipment and software vendors are not declared. However, such keys will be read and stored as `Tag 0xXXXX (DDDDD)`. XXXX and DDDDD stand for hexadecimal and decimal values of the unknown tag respectively.

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

`__init__(file_name:str, encoding:str = 'utf_8')` - the constructor, this is where all metadata is scanned in `ImageMetadata` and `VideoMetadata`. It requires just the name of the file containing media. `encoding` is optional and used to decode string values from byte sequences in the metadata. `encoding` should be one of Python supported [Standard encodings](https://docs.python.org/3/library/codecs.html#standard-encodings). In case decoding fails the offending symbols in a string will be replaced with � (U+FFFD).

`__getitem__(key:str)` - retrieves the metadata value for a specific `key` allowing the objects of `MediaMetadata` and its descendants to be indexed with `[]`. If the `key` is not present in the file's headers a None value is returned. If the `key` is present and a single value is stored under it, this value is returned. If the `key` holds mulptiple values like, for instance, in the case of GPS coordinates, they are returned as a list. If the object was interpreted (see `interpret()` below), the interpreted values are returned.

> Note: For tags that have not been interpreted, rational type values are returned as '_numerator_/_denominator_' strings. For example, in the case of `ExposureTime` tag you will see something like `'1/3003'` as its value. This is done to preserve the original metadata and to avoid division by zero as might happen, for instance, in `LensSpecification` tag recording an unknown F number in `0/0` notation.

`__str__()` - casts the object to `str` type returning a string of tab separated metadata key/value pairs found in the media file each followed by a line separator. The format of values follows the logic documented for `__getitem__()`. Useful to import the data into a spreadsheet. Or if you are creaing a command line tool, the output can be fed to `awk` or `grep` for further processing.

> Note: there are non-printable tags which will not show in the output. The tags of UNDEFINED type (== 7) are such as well as some others that typically contain binary data. For instance, MakerNote and UserComment. Tags with typically long outputs will not show either though they might be perfectly printable like XMLPacket and StripOffsets. If you wish to access these, use `[]` to get them directly from the class instance.

`all()` - a generator yielding tuples of `(key, value)` found in the media file. The format of values follows the logic documented for `__getitem__()`.

`keys()` - returns a `list` of all keys found in the media file.

`file_name()` and `file_extension()` - return the file name that was supplied to the class constructor and the capitalised extesion respectively. The extesion can be used in further releases/forks to manipulate the metadata which implies knowing the original file type.

`interpret()` - calling this function would attempt at converting the tag's values to their human-readable form. This function attemps to locate a dictionary or a function with exactly the same name as the tag. If a dictionary is found, it tries to map the values of the tag to the ones in the dictionary. If a function is found, the tag's value is passed to it and the result is then stored as an interpreted value.

The interpreters (dictionaries and functions) defined in the package are documented below. Should you wish to overrride them, or write an interpreter for another tag, just define it in your code and register with `assign_interpreter()` prior to calling `interpret()`.

Even if an interpreter for a tag is not available, `interpret()` will attempt to convert rational values to their decimal form, e.g. 1/4 will be converted to 0.25.

`revert_interpretation()` - reverts the tags back to their original values as they were obtained from the media file.

`assign_interpreter(tag: str, interpreter)` - assigns an interpreter for `tag`. `interpreter` must be a dictionary or a function. A dictionary must define a mapping between the tag's values and their human-readable form. Al least, this is the primary goal of interpreters. An interpreter function does the same but with whatever logic the developer thinks is right. It must accept a list of values as an input (even if there is only one value) and return a list as well.

Use it even if there is a default interpreter for a tag. The assignment will override it.

`drop_interpreter(tag: str)` - reverts assignment by `assign_interpreter()`

## Interpreters reference

### Dictionaries

 1..10 | 11..20 | 21..30
---|---|---
Orientation | ExposureProgram | MeteringMode
LightSource | Flash | SensingMethod
SceneCaptureType | SceneType | CustomRendered
GainControl | WhiteBalance | Contrast
Saturation | Sharpness | SubjectDistanceRange
FileSource | Components | ResolutionUnit
FocalPlaneResolutionUnit | PhotometricInterpretation | Compression
PlanarConfiguration | YCbCrPositioning | ColorSpace
ExposureMode | Predictor | GPSAltitudeRef
GPSSpeedRef | GPSImgDirectionRef | GPSDestBearingRef

### Functions

Intepreter Function | Action
--- | ---
ExifVersion | Returns a version string, e.g. _2.3_
FlashpixVersion | Returns a version string
InteroperabilityVersion | Returns a version string
ExposureTime | Returns a rational in seconds
ShutterSpeedValue | Returns an APEX value, e.g. _2.0 Ev_
ApertureValue | Returns an APEX value
ExposureBiasValue | Returns an APEX value
MaxApertureValue | Returns an APEX value
BrightnessValue | Returns an APEX value or _Unknown_ if 0xFFFFFFFF is found
FocalLength | Returns a focal length in mm, e.g. _4 mm_
FocalLengthIn35mmFilm | Returns a focal length in mm
LensSpecification | Returns a string with min and max focal length and min Fnumber for both, e.g. _f min = 18 (f/1.8), f max = 24 (f/1.8)_
FNumber | Converts a rational value of FNumber to a string 'f/__' with a decimal value following the slash
GPSLatitude | Converts GPS latitude to dd°mm'ss"N format, e.g. _41°4'0.6"_
GPSLongitude | Same as GPSLatitude but for the longtitude
GPSHPositioningError | Converts the error to string in meters, e.g. _24 m_
GPSAltitude | Converts the altitude to string in meters, e.g. _156 m_
GPSSpeed | Returns the speed as formatted string with float value
GPSImgDirection | Returns the direction as formatted string with float value and degrees sign at the end ('°', '\xB0')
GPSDestBearing | Same as GPSImgDirection but for the bearing
GPSVersionID | 

## Function reference

There are a few useful functions that come predefined with the package, should you wish to use them in your code.

`str_to_rational(a:str)` - converts a '_numerator_/_denominator_' string to `float` or `int` if the the numbers are exact multiples

`format_rational(x:int | float, num_digits:int = 2)` - returns a string containing an integer value or a floating point value rounded to `num_digits` decimal points.

`GPS_link(lat:str, lat_ref:str, lng:str, lng_ref:str, service:str='google')` - returns the maps link for the supplied coordinates. The coordinates must be obtained after calling `interpret()`. Supported providers are Google, Yandex, OpenStreetMaps and Microsoft Bing. Samples follow:

	google_maps = GPS_link('41°4'0.6"', 'N', '29°1\'9.46"', 'E')
	yandex_maps = GPS_link('41°4'0.6"', 'N', '29°1\'9.46"', 'E', 'yandex')
	openst_maps = GPS_link('41°4'0.6"', 'N', '29°1\'9.46"', 'E', 'osm')
	msbing_maps = GPS_link('41°4'0.6"', 'N', '29°1\'9.46"', 'E', 'bing') 

Link | Sample result
--- | ---
google_maps | https://www.google.com/maps/place/41.066833,29.019294
yandex_maps | https://yandex.com/maps/?ll=29.019294,41.066833&pt=29.019294,41.066833&z=17&l=map
openst_maps | https://www.openstreetmap.org/?mlat=41.066833&mlon=29.019294#map=17/41.066833/29.019294
msbing_maps | https://www.bing.com/maps?cp=41.066833~long&lvl=17&sp=point.41.066833_29.019294_Photo%20GPS%20location
