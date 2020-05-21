%% Load image and make grayscale

A = imread("C:\Users\Tom\Desktop\thesisWindows\Report\images\emu_original.jpg");
imshow(A);

A_gray = rgb2gray(A);
figure();
imshow(A_gray);

%% Add salt and pepper noise

A_noise = imnoise(A_gray, 'salt & pepper');
figure();
imshow(A_noise);


%% Filter - Gaussian

G = fspecial('gaussian', [17 17]);
A_gauss = imfilter(A_noise, G);
figure();
imshow(A_gauss);



%% Filter - Median
A_median = medfilt2(A_noise, [5 5]);
figure();
imshow(A_median);




