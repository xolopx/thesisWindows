%% Open Image

A = imread("C:\Users\c3175\Desktop\thesisWindows\Report\images\litreview\imageprocessing\linearfiltering\kernels\sunflowers.png");
imshow(A);

%% Convert to Grayscale
G = rgb2gray(A);
imshow(G);

%% Apply Sobel Filters x and y
k_x = [-1,0,1;-2,0,2;-1,0,1]; % Sobel Gx kernel
k_y = k_x'; % gradient Gy
G_x = filter2(k_x,G); % convolve in 2d
G_y = filter2(k_y,G);

figure; imshow(G_x);
figure; imshow(G_y);


%% Combine results of x and y
G = sqrt(G_x.^2 + G_y.^2); % Find magnitude
Gmin = min(min(G)); dx = max(max(G)) - Gmin; % find range
G = floor((G-Gmin)/dx*255); % normalise from 0 to 255
image(G); axis('image')
colormap gray

