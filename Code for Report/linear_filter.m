A = imread("C:\Users\Tom\Desktop\thesisWindows\Report\images\dogPug.jpg");
%imshow(im)
kernel = ones(5,5)/25;
display(kernel)

localMean = imboxfilt(A,15);
imshowpair(A,localMean,'montage')