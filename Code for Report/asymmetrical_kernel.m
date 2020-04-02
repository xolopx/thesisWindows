A = imread("C:\Users\Tom\Desktop\thesisWindows\Report\images\van.jpg");
A = rgb2gray(A);
%imshow(im)
kernel = ones(16,16)/(16^2);
kern = fspecial('sobel');
kernel = cast(kernel, 'like',kern);
result = imfilter(A, kernel);
imshow(result)