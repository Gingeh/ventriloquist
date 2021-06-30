from pyvirtualcam import PixelFormat, Camera
import numpy as np
from PIL import Image
import alsaaudio
import audioop

name = "popcat"

inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,
                    alsaaudio.PCM_NONBLOCK,
                    channels=1,
                    rate=8000,
                    format=alsaaudio.PCM_FORMAT_S16_LE)

quietimage = np.asarray(Image.open(f"images/{name}/closed.png").convert('RGB'), dtype=np.uint8)
loudimage = np.asarray(Image.open(f"images/{name}/open.png").convert('RGB'), dtype=np.uint8)

if quietimage.shape[:2] != (128, 128) or loudimage.shape[:2] != (128, 128):
    raise ValueError("Images must be 128x128 for some reason")

camera = Camera(128, 128, 20, fmt=PixelFormat.RGB)

avglen = 10
previous = [0, ] * (avglen - 1)
isopen = False
while True:
    l, data = inp.read()

    if isopen:
        threshold = 0.7
    else:
        threshold = 0.95

    if l:
        volume = audioop.max(data, 4) / 2 ** (8*4-1)
        isopen = (sum(previous) + volume) / avglen > 0.8
        if isopen:
            camera.send(loudimage)
        else:
            camera.send(quietimage)
        previous.pop(0)
        previous += [volume, ]
