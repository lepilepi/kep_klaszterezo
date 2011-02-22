DATE_MAX = 24*3600

# kepek szamanak ennyi szazalekat meghalado meretu klaszterbol mar lesz thumb
MIN_SIZE_OF_RELEVANT_CLUSTER = 0.12

# SECOND VALUES ARE THE MAX VALUES
EXIF_ATTRIBUTES = [
    ["EXIF Contrast"],
    ["EXIF ExposureProgram"],
    ["EXIF Flash"],
    ["EXIF LightSource"],
    ["EXIF MeteringMode"],
    ["EXIF Saturation"],
    ["EXIF SceneCaptureType"],
    ["EXIF Sharpness"],
    ["EXIF WhiteBalance"],
    ["Image Orientation"],
    ["EXIF ExposureTime",10],
    ["EXIF FNumber",22],
    ["EXIF FocalLengthIn35mmFilm",500]
    #["EXIF ISOSpeedRatings",6400]
]

# max_sum a main.py ben mert kepfuggo
max_mean = 255
max_median = 255
max_rms = 255
max_var = 127.5**2

WEIGHTS = {
    "EXIF Contrast":0.7,
    "EXIF ExposureProgram":0.6,
    "EXIF Flash":1,
    "EXIF LightSource":0.4,
    "EXIF MeteringMode":1.2,
    "EXIF Saturation":1,
    "EXIF SceneCaptureType":0.8,
    "EXIF Sharpness":1.4,
    "EXIF WhiteBalance":2,
    "Image Orientation":0.3,
    "EXIF ExposureTime":2,
    "EXIF FNumber":2,
    "EXIF FocalLengthIn35mmFilm":3,
    #"EXIF ISOSpeedRatings":2,
    "sum2":10,
    "mean":4,
    "median":2,
    "rms":3,
    "var":3
}
