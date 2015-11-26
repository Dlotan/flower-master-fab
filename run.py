import os
if os.path.exists('../.env'):
    print('Importing environment from .env...')
    for line in open('../.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import app
from app.tasks import start_scheduler


start_scheduler()
app.run(host='0.0.0.0', port=80, debug=True, use_reloader=False)

