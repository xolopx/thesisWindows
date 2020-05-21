%% Open original image

A = imread("C:\Users\Tom\Desktop\thesisWindows\Report\images\palms_original.jpg");

imshow(A);

%% Resize original

A_fig = openfig("C:\Users\Tom\Desktop\thesisWindows\Report\images\palms_original.fig");
A_resized = truesize(A_fig, [674 843]);

imshow(A_resized);


%% Convert to grayscale

A_grayscale = rgb2gray(A);

imshow(A_grayscale);
%% Threshold to binary

threshold_level = multithresh(A_grayscale);

A_binary = imquantize(A_grayscale,threshold_level);
figure();
imshow(A_binary,[])


%% COmplement image

A_binary_complement = imcomplement(A_binary);

imshow(A_binary_complement, []);
