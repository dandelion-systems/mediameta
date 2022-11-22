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

_TiffTags = {
	0x0100: 'ImageWidth',
	0x0101: 'ImageHeight',
	0x0102: 'BitsPerSample',
	0x0103: 'Compression',
	0x0106: 'PhotometricInterpretation',
	0x010E: 'ImageDescription',
	0x010F: 'Make',
	0x0110: 'Model',
	0x0111: 'StripOffsets',
	0x0112: 'Orientation',
	0x0115: 'SamplesPerPixel',
	0x0116: 'RowsPerStrip',
	0x0117: 'StripByteCounts',
	0x011A: 'XResolution',
	0x011B: 'YResolution',
	0x011C: 'PlanarConfiguration',
	0x0128: 'ResolutionUnit',
	0x012D: 'TransferFunction',
	0x0131: 'Software',
	0x0132: 'DateTime',
	0x013B: 'Artist',
	0x013C: 'HostComputer',
	0x013D: 'Predictor',
	0x013E: 'WhitePoint',
	0x013F: 'PrimaryChromaticities',
	0x0152: 'ExtraSamples',
	0x015B: 'JPEGTables',
	0x0201: 'JPEGInterchangeFormat',
	0x0202: 'JPEGInterchangeFormatLength',
	0x0211: 'YCbCrCoefficients',
	0x0212: 'YCbCrSubSampling',
	0x0213: 'YCbCrPositioning',
	0x0214: 'ReferenceBlackWhite',
	0x02BC: 'XMLPacket',
	0x8298: 'Copyright',
	0x83BB: 'IPTCNAA',
	0x8649: 'ImageResources',
	0x8773: 'InterColorProfile',
	0x00FE: 'NewSubfileType',

	0x8769: 'ExifIFDPointer',
	0x8825: 'GPSInfoIFDPointer',
	0xA005: 'InteroperabilityIFDPointer'
}

_ExifTags = {
	0x0001: 'InteroperabilityIndex',
	0x0002: 'InteroperabilityVersion',
	0x1000: 'RelatedImageFileFormat',
	0x1001: 'RelatedImageWidth',
	0x1002: 'RelatedImageLength',

	0x829A: 'ExposureTime',
	0x829D: 'FNumber',
	0x8822: 'ExposureProgram',
	0x8824: 'SpectralSensitivity',
	0x8827: 'ISOSpeedRatings',
	0x8828: 'OECF',
	0x8829: 'Interlace',
	0x882A: 'TimeZoneOffset',
	0x882B: 'SelfTimerMode',
	0x8830: 'SensitivityType',
	0x8831: 'StandardOutputSensitivity',
	0x8832: 'RecommendedExposureIndex',
	0x9000: 'ExifVersion',
	0x9003: 'DateTimeOriginal',
	0x9004: 'DateTimeDigitized',
	0x9010: 'OffsetTime',
	0x9011: 'OffsetTimeOriginal',
	0x9012: 'OffsetTimeDigitized',
	0x9101: 'ComponentsConfiguration',
	0x9102: 'CompressedBitsPerPixel',
	0x9201: 'ShutterSpeedValue',
	0x9202: 'ApertureValue',
	0x9203: 'BrightnessValue',
	0x9204: 'ExposureBias',
	0x9205: 'MaxApertureValue',
	0x9206: 'SubjectDistance',
	0x9207: 'MeteringMode',
	0x9208: 'LightSource',
	0x9209: 'Flash',
	0x920A: 'FocalLength',
	0x9214: 'SubjectArea',
	0x927C: 'MakerNote',
	0x9286: 'UserComment',
	0x9290: 'SubsecTime',
	0x9291: 'SubsecTimeOriginal',
	0x9292: 'SubsecTimeDigitized',

	0x9C9B: 'XPTitle',
	0x9C9C: 'XPComment',
	0x9C9D: 'XPAuthor',
	0x9C9E: 'XPKeywords',
	0x9C9F: 'XPSubject',

	0xA000: 'FlashpixVersion',
	0xA001: 'ColorSpace',
	0xA002: 'PixelXDimension',
	0xA003: 'PixelYDimension',
	0xA004: 'RelatedSoundFile',
	0xA005: 'InteroperabilityIFDPointer',
	0xA20B: 'FlashEnergy',
	0xA20C: 'SpatialFrequencyResponse',
	0xA20E: 'FocalPlaneXResolution',
	0xA20F: 'FocalPlaneYResolution',
	0xA210: 'FocalPlaneResolutionUnit',
	0xA214: 'SubjectLocation',
	0xA215: 'ExposureIndex',
	0xA217: 'SensingMethod',
	0xA300: 'FileSource',
	0xA301: 'SceneType',
	0xA302: 'CFAPattern',
	0xA401: 'CustomRendered',
	0xA402: 'ExposureMode',
	0xA403: 'WhiteBalance',
	0xA404: 'DigitalZoomRatio',
	0xA405: 'FocalLengthIn35mmFilm',
	0xA406: 'SceneCaptureType',
	0xA407: 'GainControl',
	0xA408: 'Contrast',
	0xA409: 'Saturation',
	0xA40A: 'Sharpness',
	0xA40B: 'DeviceSettingDescription',
	0xA40C: 'SubjectDistanceRange',
	0xA420: 'ImageUniqueID',
	0xA430: 'CameraOwnerName',
	0xA431: 'BodySerialNumber',
	0xA432: 'LensSpecification',
	0xA433: 'LensMake',
	0xA434: 'LensModel',
	0xA435: 'LensSerialNumber',
	0xA500: 'Gamma'
}

_GPSTags = {
	0x0000: 'GPSVersionID',
	0x0001: 'GPSLatitudeRef',
	0x0002: 'GPSLatitude',
	0x0003: 'GPSLongitudeRef',
	0x0004: 'GPSLongitude',
	0x0005: 'GPSAltitudeRef',
	0x0006: 'GPSAltitude',
	0x0007: 'GPSTimeStamp',
	0x0008: 'GPSSatellites',
	0x0009: 'GPSStatus',
	0x000A: 'GPSMeasureMode',
	0x000B: 'GPSDOP',
	0x000C: 'GPSSpeedRef',
	0x000D: 'GPSSpeed',
	0x000E: 'GPSTrackRef',
	0x000F: 'GPSTrack',
	0x0010: 'GPSImgDirectionRef',
	0x0011: 'GPSImgDirection',
	0x0012: 'GPSMapDatum',
	0x0013: 'GPSDestLatitudeRef',
	0x0014: 'GPSDestLatitude',
	0x0015: 'GPSDestLongitudeRef',
	0x0016: 'GPSDestLongitude',
	0x0017: 'GPSDestBearingRef',
	0x0018: 'GPSDestBearing',
	0x0019: 'GPSDestDistanceRef',
	0x001A: 'GPSDestDistance',
	0x001B: 'GPSProcessingMethod',
	0x001C: 'GPSAreaInformation',
	0x001D: 'GPSDateStamp',
	0x001E: 'GPSDifferential',
	0x001F: 'GPSHPositioningError'
}


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