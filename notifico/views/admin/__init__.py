# -*- coding: utf8 -*-
from flask import (
    Blueprint,
    g,
    url_for,
    redirect,
    abort
)
from flask.ext import wtf

from notifico import db
from notifico.views import user_required, group_required
from notifico.models.user import Group
from notifico.models.channel import Channel
from notifico.models.hook import Hook

admin = Blueprint('admin', __name__, template_folder='templates')


class UserPasswordForm(wtf.Form):
    password = wtf.PasswordField('Password', validators=[
        wtf.Required(),
        wtf.Length(5),
        wtf.EqualTo('confirm', 'Passwords do not match.'),
    ])
    confirm = wtf.PasswordField('Confirm Password')


@admin.route('/make')
@user_required
def admin_make():
    """
    Adds the current user to the 'admin' group, only if there are no
    existing admins.
    """
    if Group.query.filter_by(name='admin').count():
        # A user in the 'admin' group already exists.
        return redirect(url_for('public.landing'))

    g.user.add_group('admin')
    db.session.commit()
    return redirect(url_for('public.landing'))


@admin.route('/orphan')
@group_required('admin')
def admin_orphans():
    """
    Murders all orphans.
    """
    # Clean up orphaned channels.
    db.session.query(Channel).\
        filter(~Channel.project.has()).\
        delete(synchronize_session=False)

    # Clean up orphaned hooks.
    db.session.query(Hook).\
        filter(~Hook.project.has()).\
        delete(synchronize_session=False)

    db.session.commit()

    return 'Orphans cleaned.'


@admin.route('/error/<int:code>')
@group_required('admin')
def admin_error(code):
    """
    Raise the error code provided in `code`. This is an internal
    method used to test custom error handlers.
    """
    return abort(code)
