import os
import pickle
from io import StringIO

import pandas as pd
from SPARQLWrapper import SPARQLWrapper, CSV
from vantage6.client import serialization
from vantage6.tools import docker_wrapper
from vantage6.tools.data_format import DataFormat
from vantage6.tools.dispatch_rpc import dispact_rpc
from vantage6.tools.util import info

SPARQL_RETURN_FORMAT = CSV


def sparql_wrapper(module: str):
    """
    Wrapper for a vantage6 algorithm module that will query a SPARQL endpoint stored in the DATABASE_URI environment
    variable. It will then pass the result as a pandas DataFrame to a method implemented in `module`.

    In the vantage6 infrastructure information is passed to algorithm containers through the use of environment
    variables.

    Required environment variables:

    - `INPUT_FILE`: Path to the file containing the input arguments as a python dict.
    - `DATABASE_URI`: URI to a SPARQL endpoint
    - `TOKEN_FILE`: Path to a file containing a vantage6 authentication token
    - `OUTPUT_FILE`: Path where algorithm output should be stored

    The file indicated by the `INPUT_FILE` environment variable requires the field `query` in order to use this wrapper.
    The value should be a SPARQL `SELECT` query string.

    Example
    ======
    Given the following input parameters:
    ```
    {'method': 'column_names',
     'query':
     '''
     PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
    SELECT ?person ?name ?email
    WHERE {
    ?person foaf:name ?name .
    ?person foaf:mbox ?email .
    }
    '''
     }

    The wrapper will provide the `column_names` algorithm with a pandas dataframe with the columns `person`, `name`,
    `email`.

    :param module: the name of a package that contains vantage6 algorithms
    :return:
    """
    info(f"wrapper for {module}")

    # read input from the mounted inputfile.
    input_file = os.environ["INPUT_FILE"]
    info(f"Reading input file {input_file}")

    # TODO: _load_data handles input deserialization. It should be a public function
    input_data = docker_wrapper._load_data(input_file)

    query = input_data['query']

    # all containers receive a token, however this is usually only
    # used by the master method. But can be used by regular containers also
    # for example to find out the node_id.
    token_file = os.environ["TOKEN_FILE"]
    info(f"Reading token file '{token_file}'")
    with open(token_file) as fp:
        token = fp.read().strip()

    endpoint = os.environ["DATABASE_URI"]

    endpoint = _fix_endpoint(endpoint)

    info(f"Using '{endpoint}' as triplestore endpoint")

    data = query_triplestore(endpoint, query)

    # make the actual call to the method/function
    info("Dispatching ...")
    output = dispact_rpc(data, input_data, module, token)

    # write output from the method to mounted output file. Which will be
    # transfered back to the server by the node-instance.
    output_file = os.environ["OUTPUT_FILE"]
    info(f"Writing output to {output_file}")
    with open(output_file, 'wb') as fp:
        if 'output_format' in input_data:
            output_format = input_data['output_format']

            # Indicate output format
            fp.write(output_format.encode() + b'.')

            # Write actual data
            output_format = DataFormat(output_format.lower())
            serialized = serialization.serialize(output, output_format)
            fp.write(serialized)
        else:
            # No output format specified, use legacy method
            fp.write(pickle.dumps(output))


def _fix_endpoint(endpoint: str) -> str:
    """
    Remove all text before "http".
    Workaround because the endpoint is automatically prefixed with the data folder. However this does not make sense for
    a sparql endpoint.

    :param endpoint:
    :return:
    """
    idx = endpoint.find('http')
    return endpoint[idx:]


def query_triplestore(endpoint: str, query: str):
    sparql = SPARQLWrapper(endpoint, returnFormat=SPARQL_RETURN_FORMAT)
    sparql.setQuery(query)

    result = sparql.query().convert().decode()

    return pd.read_csv(StringIO(result))
