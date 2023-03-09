clc; close all; clear;

depths = [12,15,18,21,24,27,30,33,36,39,42,45,48,54,60,66,72];
disps = zeros(size(depths));
bf = zeros(size(depths));

for i = 1:size(depths,2)
    depth = depths(i);
    SGBM = readmatrix("Scan_256/SGBM_" + string(depth) + ".csv");
    disps(i) = SGBM(245,90);
    bf(i) = depths(i)*disps(i); 
end

clear SGBM; clear i; clear depth;

f = figure;
plot(disps,depths,'LineWidth',2);
grid on; 
set(gca,"FontSize",18);
t = title('Disparity to Depth');
t.FontSize = 24;
xlabel("Disparity x_L' - x_R' [Pixels]");
ylabel('Depth [inches]');
saveas(f,'dispvsdepth.png');

% figure;
% plot(depths,bf,'LineWidth',2);
% grid on;
% title('Measured Depths vs bf');
% xlabel('Measured Depths (in.)');
% ylabel('bf');


data = transpose(cat(1,disps,depths));
writematrix(data,'SGBM.xlsx');