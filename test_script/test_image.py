import cv2
import numpy as np
#1.2
#85

image=cv2.imread("segmented.png")
new_image = np.zeros(image.shape, image.dtype)

alpha = 1.0 # Simple contrast control
beta = 0    # Simple brightness control

# Initialize values
print(' Basic Linear Transforms ')
print('-------------------------')
try:
    alpha = float(input('* Enter the alpha value [1.0-3.0]: '))
    beta = int(input('* Enter the beta value [0-100]: '))
except ValueError:
    print('Error, not a number')
# Do the operation new_image(i,j) = alpha*image(i,j) + beta
# Instead of these 'for' loops we could have used simply:
# new_image = cv.convertScaleAbs(image, alpha=alpha, beta=beta)
# but we wanted to show you how to access the pixels :)

alpha_arr = np.full((image.shape), alpha, dtype= 'uint8')
new_image = cv2.multiply(image, alpha_arr)
beta_arr = np.full((image.shape), beta, dtype= 'uint8')
new_image = cv2.subtract(new_image,beta_arr)
# for y in range(image.shape[0]):
#     for x in range(image.shape[1]):
#         for c in range(image.shape[2]):
#             new_image[y,x,c] = np.clip(alpha*image[y,x,c] - beta, 0, 255)

cv2.imshow('Original Image', image)
cv2.imshow('New Image', new_image)
print(new_image)
cv2.waitKey()
