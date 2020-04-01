A = imread("C:\Users\Tom\Desktop\thesisWindows\Report\images\van.jpg");
A = rgb2gray(A);
%imshow(im)
kernel = ones(16,16)/(16^2);

localMean = convn(A,15);
imshowpair(A,localMean,'montage')