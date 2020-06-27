import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import NotFittedError

from ..wdtypes import *

warnings.filterwarnings("ignore")
pd.options.mode.chained_assignment = None

__all__ = ["LabelEncoder"]


class LabelEncoder(object):
    """
    Class to Label Encode the categorical features

    Parameters
    ----------
    columns_to_encode: List, Optional
        List of strings containing the names of the columns to encode

    Attributes
    ----------
    encoding_dict; Dict
        Dictionary containing the encoding mappings in the format, e.g.
        {'colname1': {'cat1': 0, 'cat2': 1, ...}, 'colname2': {'cat1': 0, 'cat2': 1, ...}, ...}
    inverse_encoding_dict; Dict
        Dictionary containing the insverse encoding mappings in the format, e.g.
        {'colname1': {0: 'cat1', 1: 'cat2', ...}, 'colname2': {0: 'cat1', 1: 'cat2', ...}, ...}

    Example
    ----------
    >>> df = pd.DataFrame({'col1': [1,2,3], 'col2': ['me', 'you', 'him']})
    >>> columns_to_encode = ['col2']
    >>> encoder = LabelEncoder(columns_to_encode)
    >>> encoder.fit_transform(df)
       col1  col2
    0     1     0
    1     2     1
    2     3     2
    >>> encoder.encoding_dict
    {'col2': {'me': 0, 'you': 1, 'him': 2, 'unseen': 3}}

    Note that LabelEncoder automatically adds a new category and label for
    unseen new categories
    """

    def __init__(self, columns_to_encode: Optional[List[str]] = None):
        super(LabelEncoder, self).__init__()

        self.columns_to_encode = columns_to_encode

    def fit(self, df: pd.DataFrame):

        df_inp = df.copy()

        if self.columns_to_encode is None:
            self.columns_to_encode = list(
                df_inp.select_dtypes(include=["object"]).columns
            )
        else:
            # sanity check to make sure all categorical columns are in an adequate
            # format
            for col in self.columns_to_encode:
                df_inp[col] = df_inp[col].astype("O")

        unique_column_vals = dict()
        for c in self.columns_to_encode:
            unique_column_vals[c] = df_inp[c].unique()

        self.encoding_dict = dict()
        for k, v in unique_column_vals.items():
            self.encoding_dict[k] = {o: i for i, o in enumerate(unique_column_vals[k])}
            self.encoding_dict[k]["unseen"] = len(self.encoding_dict[k])

        self.inverse_encoding_dict = dict()
        for c in self.encoding_dict:
            self.inverse_encoding_dict[c] = {
                v: k for k, v in self.encoding_dict[c].items()
            }

        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:

        try:
            self.encoding_dict
        except AttributeError:
            raise NotFittedError(
                "This LabelEncoder instance is not fitted yet. "
                "Call 'fit' with appropriate arguments before using this LabelEncoder."
            )

        df_inp = df.copy()
        # sanity check to make sure all categorical columns are in an adequate
        # format
        for col in self.columns_to_encode:  # type: ignore
            df_inp[col] = df_inp[col].astype("O")

        for k, v in self.encoding_dict.items():
            original_values = [f for f in v.keys() if f != "unseen"]
            df_inp[k] = np.where(df_inp[k].isin(original_values), df_inp[k], "unseen")
            df_inp[k] = df_inp[k].apply(lambda x: v[x])

        return df_inp

    def inverse_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        for k, v in self.inverse_encoding_dict.items():
            df[k] = df[k].apply(lambda x: v[x])

        return df

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fit(df).transform(df)
