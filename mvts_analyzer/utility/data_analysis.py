"""
	This file containts several data analysis methods designed to run on a Dataset Class
	(PCA, clustering, some classification tests)
"""

import logging
import typing

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
import sklearn.cluster
from matplotlib import cm
from sklearn import (decomposition, model_selection, preprocessing)
from sklearn.metrics import classification_report

log = logging.getLogger(__name__)


def plot_subset_columns(dataset, columns, label_column_name = "Classification"):
	"""
	Quick plot of 3d plot of 3 columns of a dataframe
	"""
	fig = plt.figure(figsize = (10,10))
	ax = fig.add_subplot(1, 1, 1, projection='3d') #3d plot #pylint: disable=invalid-name
	ax.set_xlabel(columns[0], fontsize = 15) #set labels
	ax.set_ylabel(columns[1], fontsize = 15)
	ax.set_zlabel(columns[2], fontsize = 15)
	ax.set_title('Columns:' + columns[0] + " "+ columns[1] + " " + columns[2] , fontsize = 20) #set title
	classes = dataset.df[label_column_name].unique() #get all classes
	colors = cm.rainbow(np.linspace(0,1,len(classes))) #get new color for each one #type: ignore #pylint: disable=no-member
	legend = []

	for target, color in zip(classes,colors):
		kept_indices = dataset.df['Classification'] == target #Split on classification type
		ax.scatter(dataset.df.loc[kept_indices, columns[0]], #plot the columns
				dataset.df.loc[kept_indices, columns[1]],
				dataset.df.loc[kept_indices, columns[2]],
				c = color.reshape(1,-1), #Color each type according to different color wheel
				s = 50)
		legend.append(dataset.classes[int(target)])
	ax.legend(legend)
	ax.grid()
	plt.show()



def get_pca(df, components =3, scale=True ):  #pylint: disable=invalid-name
	"""
	Uses PCA to add a "PC1", "PC2", "PC3" column to the passed dataframe and returns it
	Args:
		df (pd.DataFrame): The dataframe to perform PCA on
		components (int, optional): Number of components to return. Defaults to 3.
		scale (bool, optional): Wether to scale the data before PCA. Defaults to True.
	"""
	log.info("Generating 3d PCA plot...")
	df_pca = df.copy()
	if scale: # SCikit learn automatically centers, but does not scale data (MinMaxScaler is used here)
		for col in df_pca: #go over columns, normalize them TODO: what about time? class?
			scaler = preprocessing.MinMaxScaler()
			norm_col = scaler.fit_transform(df_pca[[col]]) #Min-max normalize data (it is centered by scikit-pca)
			df_pca.loc[:, col] = norm_col

	pca = decomposition.PCA(n_components=components)

	df_pca = df_pca.dropna()  #drop NaN for PCA analysis
	princ_components = pca.fit_transform(df_pca) #Apply PCA
	principal_df = pd.DataFrame(data = princ_components, columns = ['PC1', 'PC2', 'PC3'], index=df_pca.index)

	return principal_df

def plot_pca_2d(dataset):
	"""
	Create a 2D PCA plot of the dataset
	"""
	pca_result_df  = get_pca(
		dataset.df[dataset.df.columns.difference(["Date", "Time", "Classification", "DateTime"])], components=2)
	pca_result_df = pd.concat([pca_result_df, dataset.df['Classification']]) #append classification column to PCA plot
	classes = range(int(pca_result_df['Classification'].max()) + 1) #        \
	fig = plt.figure(figsize = (10,10))
	ax = fig.add_subplot(1, 1, 1) #pylint: disable=invalid-name
	ax.set_xlabel('Principal Component 1', fontsize = 15)
	ax.set_ylabel('Principal Component 2', fontsize = 15)
	ax.set_title('2 component PCA', fontsize = 20)
	legend = []

	colors = cm.rainbow(np.linspace(0,1,len(classes))) #get color for each one #type: ignore #pylint: disable=no-member
	for target, color in zip(classes,colors):
		kept_indices = pca_result_df['Classification'] == target #Split on classification type
		ax.scatter(pca_result_df.loc[kept_indices, 'PC1'],
				pca_result_df.loc[kept_indices, 'PC2'],
				c = color.reshape(1,-1), #Color each type according to different color wheel
				s = 50)
		legend.append(dataset.classes(target))

	ax.legend(legend)
	ax.grid()
	plt.show()


def plot_pca_3d(
		dataframe : pd.DataFrame,
		plot_only_classes : typing.Optional[typing.List[str]] = None,
		dt_column = "DateTime",
		lbl_column = None,
		figurenr : int = 5,
		figsize : tuple = (15, 10)):
	"""Plots a 3D PCA splot for the provided dataframe (all columns included).
	Colors each dot according to its column

	Args:
		dataframe (pd.DataFrame): The dataframe with all data
		plot_only_classes (Typing.List[str] optional): Wether to only plot certain columns (classes), provide a
			list of string. Defaults to [].
	"""
	if plot_only_classes is None:
		plot_only_classes = []

	#Perform PCA on all passed data (except datetime/class label):
	pca_result_df = get_pca(dataframe[dataframe.columns.difference([dt_column, lbl_column])], components=3)

	classes = ["All"]
	if lbl_column:
		pca_result_df = pd.concat([pca_result_df, dataframe[lbl_column]]) #append label column to PCA plot
		classes = dataframe[lbl_column].unique()

	fig = plt.figure(figurenr)
	ax = fig.add_subplot(1, 1, 1, projection='3d') #pylint: disable=invalid-name

	fig.set_size_inches(figsize[0], figsize[1])

	ax.set_xlabel('Principal Component 1', fontsize = 15)
	ax.set_ylabel('Principal Component 2', fontsize = 15)
	ax.set_zlabel('Principal Component 3', fontsize = 15)
	ax.set_title('3 Component PCA', fontsize = 20)

	log.debug(f"Classes: {classes}")

	colors = cm.rainbow(np.linspace(0,1,len(classes))) #get color for each one #type: ignore #pylint: disable=no-member
	legend = []
	# colors = ['r', 'g', 'b']
	for target, color in zip(classes,colors):
		log.debug(f"Now processing class {target}")
		# if target == 6: #Skip jetting as this process applies to
		#     continue
		if len(plot_only_classes) > 0 and target not in plot_only_classes: #If plot
			continue

		if lbl_column is None: #If all should be added:
			kept_indices = dataframe.index
		else:
			kept_indices = dataframe[lbl_column] == target #Split on classification type
			legend.append(target)

		if len(pca_result_df.loc[kept_indices]) <= 0:
			# print("None")
			log.warning(f"No entries for class {target}")
			continue

		ax.scatter(pca_result_df.loc[kept_indices, 'PC1'],
				pca_result_df.loc[kept_indices, 'PC2'],
				pca_result_df.loc[kept_indices, 'PC3'],
				c = color.reshape(1,-1), #Color each type according to different color wheel
				s = 50)
	ax.legend(legend)
	ax.grid()
	fig.show()

def plot_df_scatter_class(
		df, #pylint: disable=invalid-name
		ax,	#pylint: disable=invalid-name
		color_column="Classification",
		legend_label_prefix = "",
		class_name_dict = None,
		plot_kwargs = None
	):
	"""
	Plot a dataframe with a classification column, color each class differently
	Args:
		df (pd.DataFrame): The dataframe to plot
		ax (matplotlib.axes.Axes): The ax to plot on
		color_column (str, optional): The column to use for coloring. Defaults to "Classification".
		legend_label_prefix (str, optional): Prefix to add to each class label in the legend. Defaults to "".
		class_name_dict (dict, optional): Dictionary to translate class labels to other labels. Defaults to {-1 : None}.
	"""
	if plot_kwargs is None:
		plot_kwargs = {}
	if class_name_dict is None:
		class_name_dict = {-1 : None}
	dims = len(df.columns) - 1 #Columns count - classification column (determines color)
	data_cols = df.columns[ df.columns != color_column]

	if len(data_cols) > 4:
		log.fatal(f"Trying to generate a plot with dims={dims} (excluding color_column), this is impossible, exiting...")
		raise ValueError(f"Trying to generate a plot with dims={dims} (excluding color_column), "
			"this is impossible, exiting...")

	# classes = range(int(df[color_column].max()) + 1)
	classes = df[color_column].unique() #get all unique classes

	colormap = cm.rainbow(np.linspace(0,1,len(classes))) #get colors #type: ignore #pylint: disable=no-member

	class_color_dict = {}

	for i, _ in enumerate(classes):
		class_color_dict[i] = colormap[i] #create color mapping of form {"class": [r,g,b,a], etc}
	colors = pd.Series(df.loc[:, color_column]).map(class_color_dict) #create color array for each entry

	if dims == 2:
		df.plot.scatter(x=data_cols[0], y=data_cols[1], c=colors, ax=ax, **plot_kwargs)
	elif dims == 3:
		for cur_class in classes:
			cur_class_df = df[df[color_column] == cur_class] #Select only
			cur_label = legend_label_prefix + str(cur_class)
			if cur_label in class_name_dict.keys(): #if label-translation
				cur_label = class_name_dict[cur_label] #type: ignore
			ax.scatter(
				cur_class_df[data_cols[0]].to_numpy(),
	      		cur_class_df[data_cols[1]].to_numpy(),
				cur_class_df[data_cols[2]].to_numpy(),
				**plot_kwargs,
				label=cur_label
			)
			ax.legend()

		ax.set_xlabel(data_cols[0], fontsize = 10) #set labels
		ax.set_ylabel(data_cols[1], fontsize = 10)
		ax.set_zlabel(data_cols[2], fontsize = 10)
	else:
		print("Dims = 1, cant plot")


	ax.grid()
	# plt.show()



def k_cluster(df, n_clusters = 4): #pylint: disable=invalid-name
	"""Cluster using k-means"""
	df = df[df.columns.difference(["Date", "Time", "DateTime", "Classification"])]
	df = df.dropna() #remove nan values
	model = sklearn.cluster.KMeans(n_clusters=n_clusters).fit(df) #Train using the trainset (split[0]), without labels
	results = pd.Series(model.predict(df), name="Cluster", index=df.index) #Nearest clusters
	df['Cluster'] = results
	return df




def k_means_classification(dataset, label_column_name= "Classification", n_clusters=100, n_splits = 5):
	"""
	Do k-means clustering, then determine the label of that cluster using majority vote. We can then use this
	to classify new data points by finding the nearest cluster and using the majority vote label of that cluster.
	"""
	#Simple k-means classification using majority-vote for each cluster center, contains a test as well
	df_norm = dataset.get_df_norm()
	train_df = df_norm[df_norm.columns.difference(["Date", "Time"])] #Train on all (normalized) data except
		# date, time and label
	train_df = train_df.dropna() #remove nan values
	print("Number of detected classification labels in database: "
    	+  str(len(dataset.df[label_column_name].unique())) + "  (" + str(dataset.df[label_column_name].unique()) + ")")
	splits = model_selection.KFold(n_splits = n_splits, shuffle=False) #TODO: shuffle manually to equal-shared?
	labels_actual = np.array([])
	labels_predicted = np.array([])
	splits = splits.split(train_df) #get splits for training dataframe

	# for n_test in range(n_splits): #perform classification and evaluate for every split
	for n_test, split_indexes in enumerate(splits):
		print(" Doing K-fold test "+ str(n_test+1) + " out of "+  str(n_splits))
		# split_indexes = next(splits) #get split indexes
		split = train_df.iloc[split_indexes[0]], train_df.iloc[split_indexes[1]] #get train and testsplit

		train_split = split[0][split[0].columns.difference([label_column_name])] #get current trainsplit
		test_split = split[1][split[1].columns.difference([label_column_name])] #get current testsplit

		model = sklearn.cluster.KMeans(n_clusters=n_clusters).fit(train_split) #Train using the trainset (split[0]),
		results = pd.Series(model.predict(train_split), name="Cluster") #create a result series with the nearest cluster
		#create df that has class label+cluster for each entry, index should first be reset or join will fail:
		df_label_and_cluster = pd.concat([split[0][label_column_name].reset_index(drop=True), results], axis=1)
		cluster_label = ["UNKNOWN" for i in range(len(results.unique()))]
		#create dataframe with each center and the (majority voted) label for that center:
		df_center_labels = pd.DataFrame(columns=["Center", "Label Mode"])

		for cur_cluster in results.unique(): #Go over each mean (cluster), do majority vote to get labels per cluster
			cluster_df = df_label_and_cluster[df_label_and_cluster["Cluster"] == cur_cluster] #get all
			cluster_label = cluster_df[label_column_name].mode() #do majority vote for cluster
			cluster_row = pd.DataFrame([[cur_cluster, cluster_label.iloc[0]]], columns=["Center", "Label Mode"])
			df_center_labels = df_center_labels.append(cluster_row) #append row #type: ignore

		#----------------------Testing-----------------------
		#Get current predictions/labels in numpy array
		cur_pred = pd.DataFrame(model.predict(test_split), columns=["Center"])
		cur_pred = cur_pred.merge(df_center_labels, on=["Center"], how='left')["Label Mode"] #join to get majority-vote
		cur_pred_np = np.array(cur_pred, dtype=int)

		cur_act = split[1][label_column_name].reset_index(drop=True)
		cur_act_np = np.array(cur_act, dtype=int)

		#append to total list of actual/predictions
		labels_actual = np.append(labels_actual, cur_act_np) #create list with all actual labels
		labels_predicted = np.append(labels_predicted, cur_pred_np) #create list with all predicted labels


	labels_actual = [ dataset.classes[int(labels_actual[i])] for i in range(len(labels_actual))] #translate to int+class
	labels_predicted = [ dataset.classes[int(labels_predicted[i])] for i in range(len(labels_predicted))]

	print(classification_report(labels_actual, labels_predicted))
