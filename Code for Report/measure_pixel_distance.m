%% 100
imtool('C:\Users\Tom\Desktop\measuring_scene_one.png')

%% 70
imtool('Desktop/bound_70.png')

%% 40
imtool('Desktop/bound_40.png')

%% Show figures

fig1 = imread('C:\Users\Tom\Desktop\thesisWindows\Report\images\design\detection\bounding\centroid_test.png');
fig2 = imread('C:\Users\Tom\Desktop\thesisWindows\Report\images\design\detection\bounding\centroid_test_2.png');


figure();
imshow(fig1);
figure();
imshow(fig2);