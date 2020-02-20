from pillow import Image  
import requests
from io import BytesIO

response = requests.get('https://rimh2.domainstatic.com.au/HFFwevfbQlfW3h-kUxPnYTB-zm8=/305x208/filters:format(jpeg):quality(80):no_upscale()/2016036164_1_1_200128_105311-w1600-h1200')
img = pillow..open(BytesIO(response.content))


