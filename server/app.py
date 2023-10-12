#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
# initialize restful API
api = Api(app)


@app.route('/')
def home():
    return ''

# get campers (name, id, and age) at route /campers


class CamperList(Resource):
    def get(self):
        campers_dict = [camper.to_dict(rules=("-signups",))
                        for camper in Camper.query.all()]
        return make_response(campers_dict, 200)

# post /campers with name and age, returns id, name, age, and 201 else 400
    def post(self):
        try:
            new_camper = Camper(
                name=request.json['name'],
                age=request.json['age'],
            )
            db.session.add(new_camper)
            db.session.commit()
            return make_response(new_camper.to_dict(rules=("-signups",)), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(CamperList, '/campers')

# get /campers/int:id if camper exist returns json with all signups else 404


class CamperItem(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            return make_response(camper.to_dict(), 200)
        else:
            return make_response({"error": "Camper not found"}, 404)

# patch /campers/:id accepts name and age, returns id, name, age, else 404 OR 400
    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        try:
            for key in request.json:
                setattr(camper, key, request.json[key])
            db.session.add(camper)
            db.session.commit()
            return make_response(camper.to_dict(rules=("-signups",)), 202)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(CamperItem, '/campers/<int:id>')

# get /activities return id, name, difficulty


class ActivitiesList(Resource):
    def get(self):
        activities_dict = [activity.to_dict(rules=("-signups",))
                           for activity in Activity.query.all()]
        return make_response(activities_dict, 200)


api.add_resource(ActivitiesList, '/activities')


class ActivityItem(Resource):
 # delete /activities/int:id returns {} and 204 else 404
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if not activity:
            return make_response({"error": "Activity not found"}, 404)
        db.session.delete(activity)
        db.session.commit()
        return make_response({}, 204)


api.add_resource(ActivityItem, '/activities/<int:id>')

# creates new /signups for an existing Camper/Activity (accepts those and time) returns affiliated data and 201 else 400


class SignupItem(Resource):
    def post(self):
        try:
            new_signup = Signup(
                camper_id=request.json['camper_id'],
                activity_id=request.json['activity_id'],
                time=request.json['time']
            )
            db.session.add(new_signup)
            db.session.commit()
            return make_response(new_signup.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(SignupItem, '/signups')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
