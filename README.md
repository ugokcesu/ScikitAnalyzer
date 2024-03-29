# Scikit Analyzer
A python program with a pyqt interface for loading and analyzing datasets available in <b>scikit-learn.datasets</b>.
Check out <a href="https://youtu.be/nH0ePeOrICI"> this youtube video</a> for a short demo

<b> Features</b>
<ul> 
  <li>Run info statistics</li>
  <li>Compute multiple histograms colored by categories</li>
  <li>Compute <b>Histogram Dispersion</b> as a way of understanding how linearly separable your target values are for each 
  <li>Create cross plots and 2D histograms</li>
  <li>Easily run ML algorithms with varying parameters and features to find optimal parameters and features with highest      impact </li>
</ul>
  
  

# Screenshots
<img src="Screen Shot 1.png"> </img>
<img src="ML gridsearch.png"> </img>
<img src="xplot screenshot.png"> </img>


# Running the Code / Installation Notes 

See requirements.txt for a full list of modules and corresponding versions. 
Mainly, the datasets are gathered from <b>scikit-learn.datasetsa</b>, <b>PyQt5</b> for the graphical interface and <b>matplotlib</b> for plotting the histograms, 
<b>pandas</b> for storing datasets.
<p>
Entry point is in <b>main_window.py</b>

