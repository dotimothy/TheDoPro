clc; close all; clear;

data = readtable("18650-Powered_RPI_4_-_Sheet1.csv");

f = figure;
plot(data.TimeElapsed_Minutes_,data.BatteryVoltage_Volts_,'LineWidth',2);
title('Battery Life Expectancy');
set(gca,"FontSize",12);
xlabel('Time (Minutes)');
ylabel('Battery Voltage (V)');
hold on;
axis([0 90 3 4.2]);
yline(3.2,'LineWidth',2,'Color',[1 0 0]);
legend('Battery Voltage','Threshold');
grid on;
saveas(f,'batteryMetric.jpg');

