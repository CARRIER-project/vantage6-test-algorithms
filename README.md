# Vantage6 test algorithms

This repo contains a couple of simple algorithms implemented in python that run on the Vantage6 infrastructure.
The algorithms are available as docker image: `harbor2.vantage6.ai/testing/v6-test-py`

## Examples

### Combined column names
The `column_names` master algorithm collects all column names from the nodes in the collaboration and combines them 
in one big set.

```python
import vantage6.client as vtgclient
HOST = 'http://your.vantage.server' # Replace with your vantage6 server URI
PORT = 5000
IMAGE = 'harbor2.vantage6.ai/testing/v6-test-py'

USERNAME = 'your_username'
PASSWORD = 'your_password'

COLLABORATION_ID = 1 # Replace with the collaboration id of your account
ORGANIZATION_IDS = [2, 3, 6] # The organizations for which you would like to collect the column names

client = vtgclient.Client(HOST, PORT)
client.authenticate(USERNAME, PASSWORD)


client.setup_encryption('path/to/rsa/keyfile') # If no encryption configured do client.setup_encryption(None)

# For organization ids you need to specify the organization where the master algorithm should be run. This algorithm 
# will then query which other organizations are part of the collaboration and will in turn trigger the 
# secondary task on their  nodes. Results will be collected in this single master organization, aggregated and sent 
# back to the user. It is likely that you wish to exclude the master organization from running the secondary task. 
# This can be specified in `'exclude_orgs'` as follows.
task = client.post_task('column_names', image=IMAGE, 
                        collaboration_id=COLLABORATION_ID,
                        organization_ids=[2],
                        input_={'method': 'column_names', 'master':True, 'kwargs':{'exclude_orgs': [2]}})

result = client.get_results(task_id=task['id'])

print(result)
```
