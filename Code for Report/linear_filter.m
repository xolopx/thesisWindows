%% Load in pug
A = imread("C:\Users\Tom\Desktop\thesisWindows\Report\images\pug_original.jpg");
figure;
imshow(A_resized);

%% Open fig and resize
A_fig = openfig("C:\Users\Tom\Desktop\thesisWindows\Report\images\pug.fig");
A_resized = truesize(A_fig, [637 738]);

imshow(A_resized);


%% Add noise to pug 

N = imnoise(A, 'gaussian', 0.02);
figure;
imshow(N);



%% Apply denoising
G = imgaussfilt(N,2);
figure(1);
imshow(G);


B = imboxfilt(A);
figure(2);
imshow(B);

%% Apply Denoising
G_filter = fspecial('gaussian', [7 7])
G_image = imfilter(N, G_filter);
figure(1);
imshow(G_image);

B = imboxfilt(N,7);
figure(2);
imshow(B);

%% Box Blur
B = imboxfilt(A, [17 17]);
figure(2);
imshow(B);

%% Display Resulting Images