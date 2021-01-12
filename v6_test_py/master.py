""" methods.py

This file contains all algorithm pieces that are executed on the nodes.
It is important to note that the master method is also triggered on a
node just the same as any other method.

When a return statement is reached the result is send to the central
server after encryption.
"""
import time
from itertools import chain

from vantage6.client import ContainerClient
from vantage6.tools.util import info

NUM_TRIES = 40
TOKEN_FILE = 'TOKEN_FILE'
RANDOM_SEED = 5
MIN_RECORDS = 100


def _dispatch_tasks(client: ContainerClient, data, method, *args, exclude_orgs=(), **kwargs):
    """
    Generic master algorithm
    """
    tries = kwargs.get('tries', NUM_TRIES)

    # Get all organizations (ids) that are within the collaboration
    # FlaskIO knows the collaboration to which the container belongs
    # as this is encoded in the JWT (Bearer token)
    organizations = client.get_organizations_in_my_collaboration()

    info(f'Organizations in my collaboration: {organizations}')

    ids = map(lambda x: x['id'], organizations)
    ids = filter(lambda x: x not in exclude_orgs, ids)
    ids = list(ids)

    info(f'Dispatching task to organizations with ids {ids}.\n{exclude_orgs} will be excluded.')

    # The input for the algorithm is the same for all organizations
    # in this case
    info("Defining input parameters")
    input_ = {
        "method": method,
    }

    # create a new task for all organizations in the collaboration.
    info("Dispatching node-tasks")
    task = client.create_new_task(
        input_=input_,
        organization_ids=list(ids)
    )

    return _get_results(client, tries, task)


def _get_results(client, tries, task):
    """
    Check up to n times if a task has completed, return the results if possible. Otherwise, raise an exception.
    """
    # Wait for node to return results. Instead of polling it is also
    # possible to subscribe to a websocket channel to get status
    # updates
    info("Waiting for results")
    task_id = task.get("id")
    for r in range(tries):
        task = client.get_task(task_id)
        if task.get('complete'):
            break

        info("Waiting for results")
        time.sleep(1)
    # Raise Exception if task has still not completed
    if not task.get('complete'):
        raise Exception(f'Task timeout for master function column names\ntask id: {task_id}')
    info("Obtaining results")
    results = client.get_results(task_id=task.get("id"))
    return results


def column_names(client: ContainerClient, data, *args, exclude_orgs=(), **kwargs):
    """Master algoritm.

    Ask all nodes for their column names and combines them in one set.
    """

    info(f'Calling column names tasks on all organizations within collaboration except {exclude_orgs}')
    results = _dispatch_tasks(client, data, *args, method='column_names', exclude_orgs=exclude_orgs, **kwargs)

    # Create generator that lists all columns and turn it into a set to remove duplicates
    column_set = set(chain.from_iterable(results))

    info("master algorithm complete")

    # return all the messages from the nodes
    return column_set
