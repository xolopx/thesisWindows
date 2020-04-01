import sys
import cv2 as cv
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Original Image
src = cv.imread(r"C:\Users\Tom\Desktop\thesisWindows\Report\images\dogPug.jpg",cv.IMREAD_COLOR)
src = np.array(src)
plt.figure(1)
plt.imshow(src)

# Filter original image
kernel = np.ones((3,3), dtype = np.float32)
kernel /= 9
print(kernel)
result = cv.filter2D(src, -1, kernel)
plt.figure(2)
plt.imshow(result)
plt.show()