import flask
from flask import jsonify

from . import db_session
from .users import User


blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('name', 'about', 'email', 'hashed_password'))
                 for item in users]
        }
    )


@blueprint.route('/api/users/<int:users_id>', methods=['GET'])
def get_one_users(users_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(users_id)
    if not users:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'users': users.to_dict(only=(
                'name', 'about', 'email', 'hashed_password'))
        }
    )


@blueprint.route('/api/users', methods=['POST'])
def create_users():
    db_sess = db_session.create_session()

    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['name', 'about', 'email', 'hashed_password']):
        return jsonify({'error': 'Bad request'})

    users = User(
        name=request.json['name'],
        about=request.json['about'],
        email=request.json['email']
    )

    users.set_password(request.json['hashed_password'])
    db_sess.add(users)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:id_upd>/<col_upd>/<upd_inp>', methods=['POST'])
def update_db(id_upd, col_upd, upd_inp):
    db_sess = db_session.create_session()

    try:
        db_sess.query(User).filter(User.id == id_upd).update({f"{col_upd}": upd_inp}, synchronize_session='evaluate')
        db_sess.commit()
    except SQLAlchemyError:
        db_sess.rollback()
        return {'error': 'error'}
    return True


@blueprint.route('/api/users/<int:users_id>', methods=['DELETE'])
def delete_users(users_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(users_id)
    if not users:
        return jsonify({'error': 'Not found'})
    db_sess.delete(users)
    db_sess.commit()
    return jsonify({'success': 'OK'})
