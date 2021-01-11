import pandas as pd
from vantage6.tools.util import info


def RPC_column_names(data: pd.DataFrame, *args, **kwargs):
    """Column names

    List the names of the table columns
    """
    info("Retrieving column names")

    # what you return here is sent to the central server. So make sure
    # no privacy sensitive data is shared
    return data.columns.to_list()


def RPC_correlation_matrix(data: pd.DataFrame, *args, **kwargs):
    """
    Produce a correlation matrix of the local features

    :param data:
    :param args:
    :param kwargs:
    :return:
    """
    return data.corr()


def RPC_count(data: pd.DataFrame, *args, **kwargs):
    """
    Count the number of rows in the result.

    :param data:
    :param args:
    :param kwargs:
    :return:
    """
    return len(data.index)
