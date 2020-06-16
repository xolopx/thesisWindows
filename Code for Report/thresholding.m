%% open image

A = imread("C:\Users\Tom\Desktop\thesisWindows\Report\images\litreview\imageprocessing\thresholding\horses.jpg");

imshow(A);

%% Convert to grayscale

G = rgb2gray(A);
imshow(G);

%% Threshold image

T = im2bw(G, 0.67);
imshow(T, [])