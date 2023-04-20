import os

from factory import create_app


app = create_app()
app.app_context().push()

@app.teardown_request
def teardown_request(*args, **kwargs):
    'Expire and remove the session after each request'

    from database import db
    db.session.expire_all()
    db.session.remove()


if 'Development' in os.environ.get('SERVER_SOFTWARE', ''):
    from tests.conftest import create_dev_data
    from database import db
    create_dev_data(db.session)

if __name__ == "__main__":
    app.run()
