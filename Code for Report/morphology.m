%% Open Image

A = imread("C:\Users\Tom\Desktop\thesisWindows\Report\images\castle_original.jpg");
%A = imread("C:\Users\Tom\Desktop\thesisWindows\Report\images\ice_original.jpg");

imshow(A);

%% Convert to Binary
A_grayscale = rgb2gray(A);

threshold_level = multithresh(A_grayscale);
A_binary = imquantize(A_grayscale,threshold_level);
A_binary = imcomplement(A_binary);
figure();
imshow(A_binary,[])
%% Generate Structuring Element
se = strel('square', 9);



%% Dilation

A_dilate = imdilate(A_binary,se);
figure();
imshow(A_dilate, []);


%% Erosion

A_erode = imerode(A_binary, se);
figure();
imshow(A_erode,[]);

%% Opening
A_open = imopen(A_binary, se);
figure();
imshow(A_open,[]);


%% Closing

A_close = imclose(A_binary, se);
figure();
imshow(A_close, []);