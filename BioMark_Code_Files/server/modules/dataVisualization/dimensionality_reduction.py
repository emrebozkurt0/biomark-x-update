# Load Packages
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from umap import UMAP
import os, json
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly
from matplotlib.pyplot import figure
from mpl_toolkits.mplot3d import Axes3D
sns.set_theme(rc={'figure.figsize':(12,8)})

# custom modules
from modules.logger import logging

class Dimensionality_Reduction:
    """
    A class to perform and visualize dimensionality reduction using PCA, t-SNE, and UMAP 
    in both 2D and 3D scatter plots. The plots can be generated using either Seaborn or Plotly.
    """

    def __init__(self, 
                 data= None, 
                 labels_column:str = "Diagnosis", 
                 dim:str = "2D", 
                 method:str = "pca", 
                 plotter:str = "seaborn",
                 outdir:str = "output"
                ):
        """
        Initialize the Dimensionality_Reduction class with the provided data and parameters.

        Parameters:
        data (pd.DataFrame): The dataset containing features and labels.
        labels_column (str): The column name in the dataset that contains the labels.
        dim (str): The dimensionality of the plot ('2D' or '3D').
        method (str): The dimensionality reduction method to use ('pca', 'tsne', or 'umap').
        plotter (str): The plotting library to use ('seaborn' or 'plotly').
        outdir (str): The directory where output plots will be saved.
        """
        logging.info("List content: %s", str(data))
        self.data = data
        
        # Prepare X matrix with categorical preprocessing
        X_temp = data.drop(labels_column, axis=1)
        
        # Identify categorical and numerical columns
        categorical_columns = X_temp.select_dtypes(include=['object']).columns.tolist()
        numerical_columns = X_temp.select_dtypes(include=[np.number]).columns.tolist()
        
        # Apply One-Hot Encoding to categorical columns if any exist
        self.categorical_encoding_info = {}
        if categorical_columns:
            dummies = pd.get_dummies(
                X_temp[categorical_columns],
                columns=categorical_columns,
                prefix=categorical_columns,
                drop_first=False,
                dummy_na=False
            )

            # Store encoding information for frontend/logging
            for col in categorical_columns:
                generated_cols = [c for c in dummies.columns if c.startswith(f"{col}_")]
                self.categorical_encoding_info[col] = {
                    'generated_columns': list(generated_cols),
                    'encoding_type': 'OneHot'
                }

            X_temp = pd.concat([X_temp.drop(columns=categorical_columns), dummies], axis=1)
            
        self.X = X_temp
        logging.info("self.X: %s", str(self.X))
        self.labels = data[labels_column]
        self.labels_column = labels_column
        self.dim = dim
        self.method = method
        self.plotter = plotter
        self.outdir = outdir
        self.analyses = {
            "2D" : {
                "tsne" : TSNE(n_components=2, random_state=42),
                "pca" : PCA(n_components=2, random_state=42),
                "umap" : UMAP(n_components=2, init='random', random_state=42)
            },
            "3D" : {
                "tsne" : TSNE(n_components=3, random_state=42),
                "pca" : PCA(n_components=3, random_state=42),
                "umap" : UMAP(n_components=3, init='random', random_state=42)
            }
        }
        os.makedirs(outdir, exist_ok=True)

    def plot2Dscatter(self, method:str = None, plotter:str = None):
        """
        Generate a 2D scatter plot using PCA, t-SNE, or UMAP.

        Parameters:
        method (str): The dimensionality reduction method to use ('pca', 'tsne', or 'umap').
        plotter (str): The plotting library to use ('seaborn' or 'plotly').

        This method saves the generated plot as both PNG and PDF files in the output directory.
        """

        if type(method) == type(None):
            method = self.method
        if type(plotter) == type(None):
            plotter = self.plotter

        # perform analysis
        logging.info(f"Performing 2D {method.upper()} Analysis")
        components = self.analyses["2D"][method].fit_transform(self.X)
        if method == "umap":
            components = pd.DataFrame(components, columns = ["umap0","umap1"])
        if method == "tsne":
            components = pd.DataFrame(components, columns = ["tsne0","tsne1"])

        # plot with seaborn
        logging.info(f"Plotting 2D {method.upper()} Plots with {plotter}")

        # Feature selection status for plot title
        feature_status = "AfterFeatureSelection" if "AfterFeatureSelection" in self.outdir else "WithoutFeatureSelection"

        # Treat both 'seaborn' and 'matplotlib' as valid Matplotlib based back-ends
        if plotter in ("seaborn", "matplotlib"):
            plt.figure(figsize=(15, 15))  # Adjust the size as needed
            sns.scatterplot(data=pd.concat([components, self.labels]), 
                            x=f"{method}0", y=f"{method}1", hue=self.labels_column, style=self.labels_column, s = 64)
            
            plt.xlabel(f"{method}0",fontsize=20)
            plt.ylabel(f"{method}1",fontsize=20)
            plt.xticks(fontsize=15)
            plt.yticks(fontsize=15)
            plt.legend(fontsize=15)
            plt.xlim(components[f"{method}0"].min() - 1, components[f"{method}0"].max() + 1)  # Optional: Set x-axis limits
            plt.ylim(components[f"{method}1"].min() - 1, components[f"{method}1"].max() + 1)  # Optional: Set y-axis limits
            plt.tight_layout()
            
            plt.title(f'2D {method.upper()} Plot ({feature_status})', fontsize=20)
            plt.savefig(f'{self.outdir}/2D_{method}_plot.png', dpi=300, bbox_inches='tight')  # Higher resolution for better quality
            print(f'{self.outdir}/2D_{method}_plot.png')  
            plt.savefig(f'{self.outdir}/2D_{method}_plot.pdf', dpi=300, bbox_inches='tight')

        # plot with plotly
        elif plotter == "plotly":
            fig = px.scatter( components, x=f"{method}0", y=f"{method}1", 
                             color=self.labels, labels={'color': self.labels_column})
            fig.update_layout(height=800, width = 900)
            fig.update_traces(marker=dict(size=10))

            fig.write_image(f'{self.outdir}/2D_{method}_plot.png', dpi=300, bbox_inches='tight')
            print(f'{self.outdir}/2D_{method}_plot.png')  # Print the plot path for Node.js integration         
            fig.write_image(f'{self.outdir}/2D_{method}_plot.pdf', dpi=300, bbox_inches='tight')
            #fig.show()
    
    def plot3Dscatter(self, method:str = None, plotter:str = None):
        """
        Generate a 3D scatter plot using PCA, t-SNE, or UMAP.

        Parameters:
        method (str): The dimensionality reduction method to use ('pca', 'tsne', or 'umap').
        plotter (str): The plotting library to use ('seaborn' or 'plotly').

        This method saves the generated plot as both PNG and PDF files in the output directory.
        """

        if type(method) == type(None):
            method = self.method
        if type(plotter) == type(None):
            plotter = self.plotter

        # perform analysis
        logging.info(f"Performing 3D {method.upper()} Analysis")
        components = self.analyses["3D"][method].fit_transform(self.X)

        if method == "umap":
            components = pd.DataFrame(components, columns = ["umap0","umap1", "umap2"])

        logging.info(f"Plotting 3D {method.upper()} Plots with {plotter}")

        # Feature selection status for plot title
        feature_status = "After Feature Selection" if "AfterFeatureSelection" in self.outdir else "Without Feature Selection"
        # plot with seaborn
        # Treat both 'seaborn' and 'matplotlib' as valid Matplotlib based back-ends
        if plotter in ("seaborn", "matplotlib"):
            # Create a 3D scatter plot
            fig = plt.figure(figsize=(15,15))
            ax = plt.axes(projection ="3d")
            
            # Define color palette
            palette = sns.color_palette("husl", len(set(self.labels)))
            color_map = dict(zip(set(self.labels), palette))
            
            # Plotting
            for label in set(self.labels):
                mask = [lbl == label for lbl in self.labels]
                ax.scatter(components.loc[mask, f'{method}0'], 
                           components.loc[mask, f'{method}1'], 
                           components.loc[mask, f'{method}2'], 
                           label=label, 
                           color=color_map[label], 
                           s=128) 
            
            # Get current major tick values for each axis
            x_ticks = ax.get_xticks()
            y_ticks = ax.get_yticks()
            z_ticks = ax.get_zticks()

            # Calculate the distance between major ticks for each axis
            x_major_interval = x_ticks[1] - x_ticks[0]
            y_major_interval = y_ticks[1] - y_ticks[0]
            z_major_interval = z_ticks[1] - z_ticks[0]

            # Set minor ticks as 1/5 of the major interval
            ax.xaxis.set_minor_locator(plt.MultipleLocator(x_major_interval/5))
            ax.yaxis.set_minor_locator(plt.MultipleLocator(y_major_interval/5))
            ax.zaxis.set_minor_locator(plt.MultipleLocator(z_major_interval/5))

            # Adjust axis appearance
            ax.tick_params(which='both', width=0.5)
            ax.tick_params(which='major', length=5)
            ax.tick_params(which='minor', length=2)

            # Set grid
            ax.grid(True, which='major', linestyle='-', alpha=0.2)  # Major grid lines
            ax.grid(True, which='minor', linestyle=':', alpha=0.1)  # Minor grid lines

            # Thin axis grid lines
            for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
                axis._axinfo['grid']['linewidth'] = 0.5
                    
            # Labels and title
            ax.set_xlabel(f'{method}0')
            ax.set_ylabel(f'{method}1')
            ax.set_zlabel(f'{method}2')
            ax.set_title(f'3D {method.upper()} Plot', fontsize=20)
            
            # Legend
            ax.legend(title=self.labels_column, fontsize=16, title_fontsize=18)  # Set legend font size
            
            # Save plot
            ax.set_title(f'3D {method.upper()} Plot ({feature_status})', fontsize=20)
            plt.savefig(f'{self.outdir}/3D_{method}_plot.png', dpi=300, bbox_inches='tight')
            plt.savefig(f'{self.outdir}/3D_{method}_plot.pdf', dpi=300, bbox_inches='tight')
            print(f'{self.outdir}/3D_{method}_plot.png')  # Print the plot path for Node.js integration


        # plot with plotly
        elif plotter == "plotly":
            fig = px.scatter_3d(
                components, x=f"{method}0", y=f"{method}1", z=f"{method}2",
                color=self.labels, labels={'color': self.labels_column}
            )
            fig.update_traces(marker_size=8)
            fig.update_layout(
                height=800, 
                width=900,
                title={'text': f'3D {method.upper()} Plot', 'font': {'size': 20}},  # Set title font size
                legend={'font': {'size': 18}}  # Set legend font size
            )
            fig.write_image(f'{self.outdir}/3D_{method}_plot.png', dpi=300, bbox_inches='tight')
            fig.write_image(f'{self.outdir}/3D_{method}_plot.pdf', dpi=300, bbox_inches='tight')
            print(f'{self.outdir}/3D_{method}_plot.png')  
            #fig.show()
            
    def runPlots(self, runs:list = ["2d_pca", "2d_tsne", "2d_umap"]):
        """
        Execute a series of dimensionality reduction analyses and generate the corresponding plots.

        Parameters:
        runs (list): A list of strings specifying the analyses to run. Each string should be in the 
                     format 'plot_type_method' (e.g., '2d_pca', '3d_tsne').
        
        The method iterates over the specified analyses, performs the dimensionality reduction,
        and generates the respective plots.
        """

        length = 110
        print("="*length)
        print(" Starting Dimensionality Reduction Analysis ")
        print("="*length)
        logging.info(f"RUNNING DIMENSIONALITY REDUCTION ANALYSES: {runs}")
        # Iterate over runs
        for run in runs:
            # Get plot type and method
            plot_type = run.split("_")[0]
            method = run.split("_")[1]

            print("="*length)
            print(f" Starting {plot_type.upper()} {method.upper()} Analysis ")
            print("="*length)

            if plot_type == "2d":
                self.plot2Dscatter(method = method)
            else:
                self.plot3Dscatter(method = method)

        print("="*length)
        print(" Dimensionality Reduction Analysis Completed ")
        print("="*length)
        logging.info(f"COMPLETED DIMENSIONALITY REDUCTION ANALYSES")
