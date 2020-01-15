# Backend Engineering Challenge -Solution

This is a solution for the backend engineering challenge. It was made using python 3.7

How to use :

	python movAverage.py --input_file <inputfile.json> --window_size <window_size (minutes)>

Example:

	python movAverage.py --input_file movAverage.json --window_size 120

	
#### Notes

Here I've tried to explore an efficient solution for calculating the moving average with a constant time rate. The naive solution would simply be that for each sample of the output file (each exact minute), we would go back N seconds (being N the size of the moving window) and calculate the average of the durations that were found. However this is not very efficient given that we create a new data structure that saves the samples inside the window and calculate the average of its elements (summing the elements and dividing by the total number of elements takes linear time). This is specially problematic if the data points have a much bigger frequency than the sampling rate, and even worst, if the window is also very large. This is because we would store already screened data points and calculate the mean from scratch.

To overcome this a sort of dynamic programming approach can be applied, where the previous processed points are not processed for later samplings if they are still inside the window. The average is just updated when the point "enters" or "leaves" the window. This update to the moving average is done iteratively since the mean of a sequence can be described as an aritmetic series.

Maybe this scenario does not apply in practice. The naive solution would work just fine for sparse datasets (as the one shown in the problem example). But if many translations are occuring all over the world within 1 minute time, this would not be so time or space efficient.



The program accepts non-integer window sizes as input. This is if we want to be able to have windows whose length are smaller than 1 min or intermediate values

The writing to a json file is not the most efficient since I'm saving all the output points in a variable and save at the end. I'm sure there is a better way :) 
