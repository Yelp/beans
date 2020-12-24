# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os

from factory import create_app


app = create_app()
app.app_context().push()

if 'Development' in os.environ.get('SERVER_SOFTWARE', ''):
    from tests.conftest import create_dev_data
    from database import db
    create_dev_data(db.session)

if __name__ == "__main__":
    app.run()
