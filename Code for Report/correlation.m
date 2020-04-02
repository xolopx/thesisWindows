im_color = imread("C:\Users\Tom\Desktop\thesisWindows\Report\images\wall.png");
%im1 = imread("C:\Users\Tom\Desktop\thesisWindows\Report\images\horizontal.png");
%im2 = imread("C:\Users\Tom\Desktop\thesisWindows\Report\images\vertical.png");
im = rgb2gray(im_color);

[gv, t] = edge(im, 'sobel', 0.15,'vertical');
[gh, z] = edge(im, 'sobel', 0.15,'horizontal');

gv = uint8(255 * gv);
gh = uint8(255 * gh);
multi = cat(2,im, gv, gh);

imshow(im_color)

%%




%% 
%kernel = fspecial('sobel');
kernelV = [-1 2 -1; -1 2 -1; -1 2 -1];
kernelH = [-1 -1 -1; 2 2 2; -1 -1 -1];

%% Next section
resultV = imfilter(im, kernelV);
resultH = imfilter(im, kernelH);
multi = cat(2, im, resultV, resultH);
%imshow(result,[])
figure();
montage(multi);