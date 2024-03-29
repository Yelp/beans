from flask import Blueprint
from flask import jsonify
from flask import request

from yelp_beans.logic.user import get_user

user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/", methods=["GET"])
def user_api():
    user = get_user(request.args.get("email"))

    if not user:
        resp = jsonify({})
        resp.status_code = 200
        return resp

    resp = jsonify(
        {"first_name": user.first_name, "last_name": user.last_name, "photo_url": user.photo_url, "metadata": user.meta_data}
    )
    resp.status_code = 200
    return resp
