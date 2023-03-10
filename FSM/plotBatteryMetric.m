clc; close all; clear;

data = readtable("18650-Powered_RPI_4_-_Sheet1.csv");

f = figure;
plot(data.TimeElapsed_Minutes_,data.BatteryVoltage_Volts_,'LineWidth',2);
title('Battery Life Expectancy');
set(gca,"FontSize",14);
xlabel('Time [Minutes]');
ylabel('Battery Voltage [Volts]');
hold on;
axis([0 90 3 4.2]);
yline(3.2,'LineWidth',2,'Color',[1 0 0]);
xline(77,'--','LineWidth',2,'Color', [0 0.5 0]);
legend('Battery Voltage','Cut-off Voltage (V = 3.2 V)','Cut-off Time (T = 77 mins)');
grid on;
saveas(f,'batteryMetric.jpg');

