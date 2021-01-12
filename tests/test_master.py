from unittest.mock import MagicMock

import pandas as pd
import pytest
from v6_test_py import master

ID = 1
TRIES = 1
MOCK_TASK = {'id': ID}
IDENTIFIER_KEYS = ['GBAGeboorteJaar', 'GBAGeboorteMaand', 'GBAGeboorteDag', 'GBAGeslacht', 'GBAPostcode',
                   'GBAHuisnummer', 'GBAToev']
KEY_VALUES = [1987, 10, 30, 1, '1098ln', 11, 'b']
COLUMN1 = 'column1'
COLUMN2 = 'column2'

DATASET = 'tests/resources/joined_data.csv'

# Arbitrary features
FEATURES = ['height', 'weight', 'bmi', 'Age', 'n_smokingcat4', 'WOZ', 'N_ALCOHOL_CAT',
            'ZVWKOPHOOGFACTOR_2010', 'ZVWKHUISARTS_2010', 'ZVWKFARMACIE_2010', 'ZVWKZIEKENHUIS_2010',
            'ZVWKPARAMEDISCH_2010', 'ZVWKZIEKENVERVOER_2010',
            'ZVWKBUITENLAND_2010', 'ZVWKOVERIG_2010', 'ZVWKEERSTELIJNSPSYCHO_2010', 'ZVWKGGZ_2010',
            'ZVWKHULPMIDDEL_2010', 'ZVWKOPHOOGFACTOR_2011', 'ZVWKHUISARTS_2011']
TARGET = 'N_CVD'


def test_column_names_returns_column_set():
    client = create_base_mock_client()
    client.get_results.return_value = [[COLUMN1], [COLUMN2]]

    result = master.column_names(client, None, tries=TRIES)

    target = {COLUMN1, COLUMN2}

    assert target == result


def test_column_names_master_node_excluded_from_task():
    my_organization_id = 1
    organization_ids = [1, 2, 3]
    client = create_base_mock_client()
    client.get_organizations_in_my_collaboration.return_value = [{'id': i} for i in organization_ids]

    master.column_names(client, None, tries=TRIES, exclude_orgs=[my_organization_id])
    client.create_new_task.assert_called_once_with(input_={'method': 'column_names'}, organization_ids=[2, 3])


def test_column_names_raise_exception_when_task_timeout():
    client = create_base_mock_client()
    client.get_task.return_value = {'complete': False}

    with pytest.raises(Exception):
        master.column_names(client, None, tries=TRIES)


def create_basic_data_client(*node_data):
    client = create_base_mock_client()

    client.get_results.return_value = node_data
    return client


def create_base_mock_client():
    client = MagicMock()
    client.create_new_task.return_value = MOCK_TASK
    client.get_task.return_value = {'complete': True}
    client.get_results.return_value = [COLUMN1, COLUMN2]

    return client()


def load_dataset(path=DATASET):
    return pd.read_csv(path)
