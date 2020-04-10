%%
x = [-1:0.005 :1];
y = normpdf(x,0,0.2);



figure(); plot(x,y); xlim([-1.2 1.2]); ylim([0 2.2]);
%%
mu = 0;
a = 2;
sigma = 0.2;

N = 1;  
%x=linspace(-N, N);
x = -1:0.005:1;
y=x;
[X,Y]=meshgrid(x,y);
%z=(1/sqrt(2*pi).*exp(-(X.^2/2)-(Y.^2/2)));
z = 2.*exp(-((X-mu).^2/2*sigma^2 + (Y-mu).^2/2*sigma^2));



surf(X,Y,z);
shading interp
axis tight

%% 

A = 2;
x0 = 0; y0 = 0; % Mean

sigma_X = 0.2;  % standard deviation
sigma_Y = 0.2;

[X, Y] = meshgrid(-1:.005:1, -1:.005:1);

for theta = 0:pi/100:pi
    a = cos(theta)^2/(2*sigma_X^2) + sin(theta)^2/(2*sigma_Y^2);
    b = -sin(2*theta)/(4*sigma_X^2) + sin(2*theta)/(4*sigma_Y^2);
    c = sin(theta)^2/(2*sigma_X^2) + cos(theta)^2/(2*sigma_Y^2);

    Z = A*exp( - (a*(X-x0).^2 + 2*b*(X-x0).*(Y-y0) + c*(Y-y0).^2));

surf(X,Y,Z);shading interp;view(-36,36)
end