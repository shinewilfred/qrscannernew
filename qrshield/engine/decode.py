from __future__ import annotations
import cv2, numpy as np
from .payloads import classify

def decode_image(data: bytes) -> list[tuple[str,str]]:
    image=cv2.imdecode(np.frombuffer(data,np.uint8),cv2.IMREAD_COLOR)
    if image is None: raise ValueError("That file is not a readable image.")
    detector=cv2.QRCodeDetector(); values=[]
    for candidate in (image,cv2.resize(image,None,fx=2,fy=2),cv2.threshold(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY),0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]):
        try:
            ok, decoded, _, _=detector.detectAndDecodeMulti(candidate)
            if ok: values.extend(item for item in decoded if item)
            if not values:
                value,_,_=detector.detectAndDecode(candidate)
                if value: values.append(value)
        except cv2.error: continue
        if values: break
    if not values: raise ValueError("No QR code was found. Try a sharper, well-lit image.")
    return [(value,classify(value)) for value in dict.fromkeys(values)]
