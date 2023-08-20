<!-- # MVTS-Analyzer -->
<p align="center">
	<!-- <img src="https://github.com/Woutah/MVTS-analyzer/main/mvts_analyzer/res/app_banner.png" width="1200" /> -->
	<!-- <img src="https://raw.githubusercontent.com/Woutah/MVTS-analyzer/first-release/mvts_analyzer/res/app_banner.png" width="1200" /> -->
	<img src="./mvts_analyzer/res/app_banner.png"/>
</p>

MVTS-Analyzer is an open-source Python app for plotting, analyzing and annotating multivariate time series. The app was mainly implemented using [PySide6](https://pypi.org/project/PySide6/), [Pandas](https://pypi.org/project/pandas/) and [Matplotlib](https://pypi.org/project/matplotlib/) and makes it easy to quickly load, display and manipulate multivariate time-series data from a .CSV, .XLSX or pandas-dataframe-pickle file.

# Table of contents- [Table of contents](#table-of-contents)
- [Features](#features)


# Features
<p align="center">
	<img src="./mvts_analyzer/example/images/app_selection_example.png"/>
</p>

Using MVTS-Analyzer, we can quickly load and plot multivariate time-series data from a .csv, .xlsx or pandas-dataframe-pickle file. The app also allows us to easily manipulate the data by adding, removing or renaming columns, as well as adding, removing or renaming rows. 




<p align="center">
<img src="./mvts_analyzer/example/images/app_settings_example.png" width="500"/>
</p>

We can open multiple views and plot the same data in different ways using line- and scatter-plots. Point-selection is shared between views, so we can plot different sensors against each other, and select point in one view to highlight them in the other views. This is useful for example to quickly identify outliers in the data - or to select certain patterns in the data.
<p align="center">
<img src="./mvts_analyzer/example/images/multi_view_selection_example.gif" width="1200"/>
</p>
