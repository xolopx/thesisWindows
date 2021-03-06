%%
rng('default') % For reproducibility
X = [randn(100,2)*0.75+ones(100,2);
    randn(100,2)*0.5-ones(100,2);
    randn(100,2)*0.75];

[idx,C] = kmeans(X,3);

figure
gscatter(X(:,1),X(:,2),idx,'bgm')
hold on
plot(C(:,1),C(:,2),'kx')
legend('Cluster 1','Cluster 2','Cluster 3','Cluster Centroid')

%%
load fisheriris;
X = meas(:,1:2);
[n,p] = size(X);
%%
plot(X(:,1),X(:,2),'.','MarkerSize',15);
title('Fisher''s Iris Data Set');
xlabel('Sepal length (cm)');
ylabel('Sepal width (cm)');
rng(3);                                 % Set the seed   
k = 3;                                  % Number of GMM components
options = statset('MaxIter',1000);      % Number of iterations

Sigma = {'diagonal','full'};            % Options for covariance matrix type
nSigma = numel(Sigma);                  % Get number of elements in array.                

SharedCovariance = {true,false};        % Indicator for identical or nonidentical covariance matrices
SCtext = {'true','false'};              % Set params for shared cov.
nSC = numel(SharedCovariance);          % Get num elements

d = 500;                                                    % Grid length
x1 = linspace(min(X(:,1))-2, max(X(:,1))+2, d);             % Data: Linearly Spaced
x2 = linspace(min(X(:,2))-2, max(X(:,2))+2, d);             % Data: Linearly Spaced
[x1grid,x2grid] = meshgrid(x1,x2);                          % Smoosh them together 
X0 = [x1grid(:) x2grid(:)];                                 % 

threshold = sqrt(chi2inv(0.99,2));
count = 1;

gmfit = fitgmdist(X,k,'CovarianceType',Sigma{2}, ...
            'SharedCovariance',SharedCovariance{2},'Options',options);  % Fitted GMM
        
clusterX = cluster(gmfit,X);                                            % Cluster index 
mahalDist = mahal(gmfit,X0);                                            % Distance from each grid point to each GMM component
% Draw ellipsoids over each GMM component and show clustering result.
h1 = gscatter(X(:,1),X(:,2),clusterX);
hold on
hold on
for m = 1:k
    idx = mahalDist(:,m)<=threshold;
    Color = h1(m).Color*0.75 - 0.5*(h1(m).Color - 1);
    h2 = plot(X0(idx,1),X0(idx,2),'.','Color',Color,'MarkerSize',1);
    uistack(h2,'bottom');
end  
plot(gmfit.mu(:,1),gmfit.mu(:,2),'kx','LineWidth',2,'MarkerSize',10)
%title(sprintf('Sigma is %s\nSharedCovariance = %s',Sigma{i},SCtext{j}),'FontSize',8)
legend(h1,{'1','2','3'})
hold off
count = count + 1;

%%
for i = 1:nSigma
    for j = 1:nSC
        gmfit = fitgmdist(X,k,'CovarianceType',Sigma{i}, ...
            'SharedCovariance',SharedCovariance{j},'Options',options); % Fitted GMM
        clusterX = cluster(gmfit,X); % Cluster index 
        mahalDist = mahal(gmfit,X0); % Distance from each grid point to each GMM component
        % Draw ellipsoids over each GMM component and show clustering result.
        subplot(2,2,count);
        h1 = gscatter(X(:,1),X(:,2),clusterX);
        hold on
            for m = 1:k
                idx = mahalDist(:,m)<=threshold;
                Color = h1(m).Color*0.75 - 0.5*(h1(m).Color - 1);
                h2 = plot(X0(idx,1),X0(idx,2),'.','Color',Color,'MarkerSize',1);
                uistack(h2,'bottom');
            end    
        plot(gmfit.mu(:,1),gmfit.mu(:,2),'kx','LineWidth',2,'MarkerSize',10)
        title(sprintf('Sigma is %s\nSharedCovariance = %s',Sigma{i},SCtext{j}),'FontSize',8)
        legend(h1,{'1','2','3'})
        hold off
        count = count + 1;
    end
end

