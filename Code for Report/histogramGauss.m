A = [3 2; -2 1];
R1 = normrnd(0,0.323,1000, 1);
R2 = normrnd(1,0.6,1000, 1);
R3 = normrnd(2,0.55,1000, 1);

R = cat(1,R1,R2,R3);
size(R)
%q = [1 0; 2 3; 4 5]
m = [-1:.0015:3.5];
m = m(1:end-1);
size(R)
figure();x = histogram(R);
figure(); p = gscatter(R,m);
%%
text1 = '\pi_1';
text2 = '\pi_2';
text3 = '\pi_3';



woah = 0.248;
m = [-1:.01:3.5];
y1 = normpdf(m,0,0.323);
y2 = normpdf(m,1,0.2);
y3 = normpdf(m,2,0.5);
y1 =  woah*y1;
y2 =  woah*y2;
y3 =  woah*y3;
figure(); hold on;
axis([-1 3.5 0 0.55])
text(0, 0.325,text1,'HorizontalAlignment','right','FontSize',14);
text(1,0.5,text2,'HorizontalAlignment','right','FontSize',14);
text(2,0.2,text3,'HorizontalAlignment','right','FontSize',14);
plot(m,y1,'LineWidth',2);
plot(m,y2,'LineWidth',2);
plot(m,y3,'LineWidth',2);


%% Plot super

y = y1 + y2 + y3;
plot(m,y,'LineWidth',2);