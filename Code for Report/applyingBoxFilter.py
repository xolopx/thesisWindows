# Applying box filter to image
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv

# Open image and store in an array
im = Image.open(r"C:\Users\Tom\Desktop\thesisWindows\Report\images\dogPug.jpg")
im = np.array(im)

# Apply filter

# Show image
# fig = plt.figure()
plt.imshow(im)
print("Done")
# Save image

