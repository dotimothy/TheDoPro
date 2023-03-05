clc; close all; clear;

depths = [12,15,18,21,24,27,30,33,36,39,42,45,48,54,60,66,72];
disps = zeros(size(depths));
bf = zeros(size(depths));

for i = 1:size(depths,2)
    depth = depths(i);
    SGBM = readmatrix("SGBM_" + string(depth) + ".csv");
    disps(i) = SGBM(255,239);
    bf(i) = depths(i)*disps(i); 
end

clear SGBM; clear i; clear depth;

figure;
plot(disps,depths,'LineWidth',2);
grid on;
title('SGBM Disparity vs Depths');
xlabel('OpenCV SGBM Disparity (Pixels)');
ylabel('Measured Depth (in.)');

figure;
plot(depths,bf,'LineWidth',2);
grid on;
title('Measured Depths vs bf');
xlabel('Measured Depths (in.)');
ylabel('bf');


data = transpose(cat(1,disps,depths));
writematrix(data,'SGBM.xlsx');