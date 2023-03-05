clc; close all; clear;

depths = [3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,54,60,66,72];
disps = zeros(size(depths));
bf = zeros(size(depths));

for i = 1:size(depths,2)
    depth = depths(i);
    BM = readmatrix("BM_" + string(depth) + ".csv");
    disps(i) = BM(240,50);
    bf(i) = depths(i)*disps(i); 
end

clear BM; clear i; clear depth;

figure;
plot(disps,depths,'LineWidth',2);
grid on;
title('BM Disparity vs Depths');
xlabel('OpenCV BM Disparity (Pixels)');
ylabel('Measured Depth (in.)');

figure;
plot(depths,bf,'LineWidth',2);
grid on;
title('Measured Depths vs bf');
xlabel('Measured Depths (in.)');
ylabel('bf');


data = transpose(cat(1,disps,depths));
writematrix(data,'BM.xlsx');