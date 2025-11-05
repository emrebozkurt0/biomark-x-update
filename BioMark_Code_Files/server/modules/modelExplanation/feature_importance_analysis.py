# Load general packages
import pandas as pd
import numpy as np
import os
from tqdm.notebook import tqdm

# Load sklearn packages
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn import set_config

# Load visualization packages
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

# Load Custom Modules
from modules.utils import save_json, load_json, getparams
from modules.logger import logging


def plot_feature_importance(feature_importance_dict, outdir, num_top_features=20):
    """
    Plots and saves feature importance graphs for multiple models.

    Parameters:
        feature_importance_dict (dict): A dictionary where keys are model names and values are dicts
                                        containing 'feature_names' and 'feature_importances'.
        outdir (str): The directory to save the output plots.
        num_top_features (int): The number of top features to display in the plot.
    """
    print("plot_feature_importance function.....\n")
    for model_name, importances_data in feature_importance_dict.items():
        feature_names = importances_data['feature_names']
        feature_importances = importances_data['feature_importances']

        # Create a pandas Series for easy sorting and plotting
        feature_importance_series = pd.Series(feature_importances, index=feature_names).sort_values(ascending=False)
        
        # Select top N features
        top_n_features = feature_importance_series.head(num_top_features)
        
        # Plotting
        plt.figure(figsize=(8, 0.4 * num_top_features)) # Adjusted figure size for better readability
        sns.barplot(x=top_n_features.values, y=top_n_features.index, hue=top_n_features.index, palette="viridis", legend=False)
        
        plt.xlabel('Feature Importance', fontsize=12)
        plt.ylabel('Features', fontsize=12)
        plt.title(f'{model_name} - Top {num_top_features} Feature Importances', fontsize=14)
        plt.tight_layout() # Adjust layout

        # Create directories if they don't exist
        png_dir = os.path.join(outdir, 'feature_importance', 'png')
        pdf_dir = os.path.join(outdir, 'feature_importance', 'pdf')
        os.makedirs(png_dir, exist_ok=True)
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Save plots
        plot_path_png = os.path.join(png_dir, f'{model_name}_feature_importance.png')
        plot_path_pdf = os.path.join(pdf_dir, f'{model_name}_feature_importance.pdf')
        
        plt.savefig(plot_path_png, bbox_inches='tight')
        plt.savefig(plot_path_pdf, bbox_inches='tight')
        plt.close() # Close the plot to free memory
        
        print(f"Feature importance plot saved to: {plot_path_png}")
        # Also print the bare path so the Node server can capture it directly
        print(plot_path_png)

        # Save importance as CSV
        try:
            csv_dir = os.path.join(outdir, 'feature_importance')
            os.makedirs(csv_dir, exist_ok=True)
            pd.DataFrame({'Feature': feature_names, 'Importance': feature_importances}) \
              .sort_values('Importance', ascending=False) \
              .to_csv(os.path.join(csv_dir, f'{model_name}_feature_importance.csv'), index=False, sep=';', encoding='utf-8-sig')
        except Exception:
            pass


class FeatureImportance_Analysis:

    """
    A class for analyzing feature importance using various classification models.

    This class provides methods to compute and visualize feature importance scores 
    from trained classifiers such as XGBoost and Random Forest. It supports model 
    fine-tuning through cross-validation and allows for plotting of the top features.

    Attributes:
        X (pd.DataFrame): The feature matrix containing input data for the model.
        y (pd.Series): The target variable corresponding to the feature matrix.
        feature_map_reverse (dict): A mapping from encoded feature names to their original names.
        feature_type (str): A string representing the type of features (e.g., 'gene', 'protein').
        top_features_to_plot (int): The number of top features to visualize in the plots.
        model_finetune (bool): Flag indicating whether to perform model fine-tuning.
        fine_tune_cv_nfolds (int): The number of folds for cross-validation during fine-tuning.
        scoring (str): The metric to optimize during model training and evaluation.
        outdir (str): The output directory for saving plots and results.
        X_train (pd.DataFrame): The training feature matrix after train-test split.
        X_test (pd.DataFrame): The testing feature matrix after train-test split.
        y_train (pd.Series): The training target variable after train-test split.
        y_test (pd.Series): The testing target variable after train-test split.

    Methods:
        PermutationFeatureImportance:
            Fits a RandomForest classifier and computes permutation feature importance 
            on the test dataset. If model fine-tuning is enabled, performs cross-validation 
            to find the optimal hyperparameters before fitting the model. Otherwise, fits 
            the default RandomForest model. The method calculates permutation feature importances, 
            visualizes the results with box plots, and saves the plots as PNG and PDF files.
            Returns a dictionary mapping feature names to their importance scores, sorted 
            in descending order.

    Parameters:
        X (pd.DataFrame, optional): The input feature data. Defaults to None.
        y (pd.Series, optional): The target labels corresponding to the input data. Defaults to None.
        test_size (float, optional): The proportion of the dataset to include in the test split. Defaults to 0.2.
        feature_map_reverse (dict, optional): A mapping for reversing encoded feature names. Defaults to None.
        feature_type (str, optional): A description of the feature type for reporting purposes. Defaults to None.
        top_features_to_plot (int, optional): Number of top features to visualize. Defaults to 20.
        model_finetune (bool, optional): Enable model fine-tuning. Defaults to False.
        fine_tune_cv_nfolds (int, optional): Number of cross-validation folds for fine-tuning. Defaults to 5.
        scoring (str, optional): Scoring metric for model evaluation. Defaults to "f1".
        outdir (str, optional): Directory to save output plots and results. Defaults to "output".

    Example:
        >>> feature_analysis = FeatureImportance_Analysis(X=data_features, y=data_labels)
        >>> feature_analysis.RandomForestFeatureImportance()
    """

    def __init__(self, 
                 X=None,
                 y=None, 
                 test_size:float = 0.2, 
                 feature_map_reverse:dict = None, 
                 feature_type:str = None, 
                 top_features_to_plot:int = 20, 
                 model_finetune:bool = False, 
                 fine_tune_cv_nfolds:int = 5,
                 scoring:str = "f1",
                 outdir:str = "output",
                 trained_models_info:dict = None,
                 preprocessor: object = None,
                 X_test: pd.DataFrame = None,
                 y_test: pd.Series = None
                ):
        """
        Initializes the FeatureImportance_Analysis class with the given parameters.

        Parameters:
            X (pd.DataFrame, optional): The input feature data. Defaults to None.
            y (pd.Series, optional): The target labels corresponding to the input data. Defaults to None.
            test_size (float, optional): The proportion of the dataset to include in the test split. Defaults to 0.2.
            feature_map_reverse (dict, optional): A mapping for reversing encoded feature names. Defaults to None.
            feature_type (str, optional): A description of the feature type for reporting purposes. Defaults to None.
            top_features_to_plot (int, optional): Number of top features to visualize. Defaults to 20.
            model_finetune (bool, optional): Enable model fine-tuning. Defaults to False.
            fine_tune_cv_nfolds (int, optional): Number of cross-validation folds for fine-tuning. Defaults to 5.
            scoring (str, optional): Scoring metric for model evaluation. Defaults to "f1".
            outdir (str, optional): Directory to save output plots and results. Defaults to "output".

        Initializes the training and testing sets based on the provided input data.
        """

        self.X = X
        self.y = y
        self.feature_map_reverse = feature_map_reverse
        self.feature_type = feature_type
        self.top_features_to_plot = top_features_to_plot
        self.model_finetune = model_finetune 
        self.fine_tune_cv_nfolds = fine_tune_cv_nfolds
        self.scoring = scoring
        self.outdir = outdir
        self.trained_models_info = trained_models_info
        self.preprocessor = preprocessor

        # Use provided test set if available to ensure alignment with model evaluation
        if X_test is not None and y_test is not None:
            self.X_test = X_test
            self.y_test = y_test
        else:
            # create train/test split (fallback)
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, stratify=self.y, test_size=test_size, random_state=42, shuffle= True)

    def _strip_transformer_prefix(self, column_name):
        """
        Normalize transformed feature names coming from ColumnTransformer with
        pandas output. It strips any pipeline/step prefixes like
        "num_pipeline__Feature_12" -> "Feature_12" so that reverse mapping to
        original column names works correctly.
        """
        if isinstance(column_name, str) and "__" in column_name:
            return column_name.split("__")[-1]
        return column_name
 
    def PermutationFeatureImportance(self):
        """
        Fits a RandomForest classifier and computes permutation feature importance on the test dataset.
    
        If model fine-tuning is enabled, performs cross-validation to find the optimal hyperparameters 
        before fitting the model. Otherwise, fits the default RandomForest model. The method calculates 
        permutation feature importances, visualizes the results with box plots, and saves the plots as 
        PNG and PDF files.
    
        Returns:
            dict: A dictionary mapping feature names to their importance scores, sorted in descending order.
        """


        logging.info("Fitting model for Permutation Feature Importance")

        # Model-Agnostic path: use pre-trained model
        if self.trained_models_info:
            model_key = list(self.trained_models_info.keys())[0]
            logging.info(f"Using pre-trained model for Permutation Feature Importance: {model_key}")
            fitted_model = self.trained_models_info[model_key]['model']
        else:
            raise ValueError("Permutation Feature Importance analysis requires a pre-trained classification model, but none was provided.")
        
        if self.preprocessor is None:
            raise ValueError("Permutation Feature Importance analysis in V2 pipeline requires a 'preprocessor' object, but none was provided.")

        # Transform test data using preprocessor
        X_test_processed = self.preprocessor.transform(self.X_test)
        logging.info(f"Computing Permutation Feature Importance for {model_key} using processed data")

        # calculate permutation importance for test data 
        logging.info("Running Permutation Importance Algorithm")
        # Use numpy array to avoid sklearn's feature-name validation mismatch
        result_test = permutation_importance(
            fitted_model, X_test_processed, self.y_test, n_repeats=20, random_state=42, n_jobs=8
        )
        
        sorted_importances_idx_test = result_test.importances_mean.argsort()
        # Determine processed feature names aligned to permutation_importance output
        try:
            processed_feature_names = list(X_test_processed.columns)
        except AttributeError:
            try:
                processed_feature_names = list(self.preprocessor.get_feature_names_out())
            except Exception:
                processed_feature_names = [f"Feature_{i}" for i in range(result_test.importances.shape[0])]

        # Build dataframe using processed feature names to ensure shapes match
        importances_test = pd.DataFrame(
            result_test.importances[sorted_importances_idx_test].T,
            columns=np.asarray(processed_feature_names)[sorted_importances_idx_test],
        )
        # Reverse map to original names when available (strip pipeline prefixes first)
        importances_test.columns = [
            self.feature_map_reverse.get(self._strip_transformer_prefix(col), col)
            for col in importances_test.columns
        ]

        feat_importances_permutation = importances_test.sum(axis=0).sort_values(ascending=False)
        important_features_by_permutation = feat_importances_permutation.head(self.top_features_to_plot).index
        
        # Plot the Feature Importance values of the top differentiating features
        logging.info("Plotting Feature Importances")
        plt.figure(figsize=(4, 8))
        importances_test[important_features_by_permutation[::-1]].plot.box(vert=False, whis=10)
        plt.title(f'Permutation Feature Importance of Top Differentiating {self.feature_type}s',
                 fontsize=20, loc='center', pad=20)
        plt.axvline(x=0, color="k", linestyle="--")
        plt.xlabel("Decrease in accuracy score",fontsize=20)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        
        # save
        logging.info("Saving Plots")
        plt.savefig(f'{self.outdir}/feature_importance/png/permutation_features_plot.png', bbox_inches='tight')
        plt.savefig(f'{self.outdir}/feature_importance/pdf/permutation_features_plot.pdf', bbox_inches='tight')
        print(f'{self.outdir}/feature_importance/png/permutation_features_plot.png')
        #plt.show()

        # Save top features and raw matrix to CSVs
        try:
            csv_dir = os.path.join(self.outdir, 'feature_importance')
            os.makedirs(csv_dir, exist_ok=True)
            # Summary (aggregated)
            summary_df = feat_importances_permutation.reset_index()
            summary_df.columns = ["Feature", "Importance"]
            summary_df.to_csv(os.path.join(csv_dir, 'permutation_feature_importance_summary.csv'), index=False, sep=';', encoding='utf-8-sig')
            # Full per-repeat matrix
            importances_test.to_csv(os.path.join(csv_dir, 'permutation_feature_importance_matrix.csv'), index=False, sep=';', encoding='utf-8-sig')
        except Exception:
            pass

        top_features = {feat_importances_permutation.index[i]:feat_importances_permutation[i] \
                    for i in range(len(feat_importances_permutation))}

        return top_features
