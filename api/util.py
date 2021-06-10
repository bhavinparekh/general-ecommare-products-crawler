import json
from bson import json_util

from bson import json_util

def restJsonify(data):
    return json.loads(json_util.dumps(data))
