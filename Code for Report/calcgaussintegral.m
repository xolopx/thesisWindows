Mean = 0;
Standard_Deviation = .2;
lims = [0.4 0.1];
cp = normcdf(lims, Mean, Standard_Deviation);
Prob = cp(1) - cp(2)
p = @(x,m,s) exp(-((x-m).^2)/(2*s.^2)) / (s*sqrt(2*pi));
c = integral(@(x) p(x, Mean, Standard_Deviation), 0.1, 0.4)