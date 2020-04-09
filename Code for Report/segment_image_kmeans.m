
RGB = imread("C:\Users\Tom\Desktop\thesisWindows\Report\images\toyCar.jpg");
RGB = imresize(RGB,0.5);

wavelength = 2.^(0:5) * 3;
orientation = 0:45:135;
g = gabor(wavelength,orientation);

I = rgb2gray(im2single(RGB));
gabormag = imgaborfilt(I,g);
montage(gabormag,'Size',[4 6])

for i = 1:length(g)
    sigma = 0.5*g(i).Wavelength;    
    gabormag(:,:,i) = imgaussfilt(gabormag(:,:,i),3*sigma); 
end
montage(gabormag,'Size',[4 6])


nrows = size(RGB,1);
ncols = size(RGB,2);
[X,Y] = meshgrid(1:ncols,1:nrows);

featureSet = cat(3,I,gabormag,X,Y);


L2 = imsegkmeans(featureSet,2,'NormalizeInput',true);
C = labeloverlay(RGB,L2);
figure();
imshow(C)
figure();
imshow(RGB)
%title('Labeled Image with Additional Pixel Information')


