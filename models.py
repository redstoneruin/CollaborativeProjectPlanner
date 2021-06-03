"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_user_id():
    return auth.current_user.get('id') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later


db.define_table(
   'project',
   Field('project_name', requires=IS_NOT_EMPTY()),
   Field('project_desc'),
   Field('owner_id', 'reference auth_user', default=get_user_id),
   Field('created_time', 'datetime', default=get_time)
)

# using ids to be able to reference the user table
db.define_table(
   'member',
   Field('project_id', 'reference project'),
   Field('member_id', 'reference auth_user'),
   Field('member_since', 'datetime', default=get_time),
   Field('permissions', 'integer', requires=IS_NOT_EMPTY())
)

db.define_table(
   'release',
   Field('project_id', 'reference project'),
   Field('created_by', default=get_user_id),
   Field('created_time', 'datetime', default=get_time),
   Field('release_name', requires=IS_NOT_EMPTY()),
   Field('due_date', 'date', requires=IS_NOT_EMPTY())
)


db.define_table(
   'task',
   Field('release_id', 'reference release'),
   Field('created_by', default=get_user_id),
   Field('created_time', 'datetime', default=get_time),
   Field('task_name', requires=IS_NOT_EMPTY()),
   Field('due_date', 'date'),
   Field('done', 'boolean', default=False),
   Field('done_time', 'datetime'),
   Field('desc', requires=IS_NOT_EMPTY())
)


db.define_table(
   'subtask',
   Field('task_id', 'reference task'),
   Field('created_by', default=get_user_id),
   Field('created_time', 'datetime', default=get_time),
   Field('subtask_name', requires=IS_NOT_EMPTY()),
   Field('due_date', 'date'),
   Field('done', 'boolean', default=False),
   Field('done_time', 'datetime'),
   Field('desc', requires=IS_NOT_EMPTY())
)

# intially comments only on tasks, can update to subtasks later
# this allows cascade ondelete
db.define_table(
   'task_comment',
   Field('task_id', 'reference task'),
   Field('author', default=get_user_id),
   Field('timestamp', default=get_time),
   Field('data', requires=IS_NOT_EMPTY())
)

# tag table for consistent naming, ability to update color/priority
db.define_table(
   'tag',
   Field('project_id', 'reference project'),
   Field('name', requires=IS_NOT_EMPTY())
)

# need 2 tables for tags, so one can reference tasks, the other subtasks
db.define_table(
   'task_tag',
   Field('task_id', 'reference task'),
   Field('added_by', default=get_user_id),
   Field('added_time', default=get_time),
   Field('tag', 'reference tag')
)

db.define_table(
   'subtask_tag',
   Field('subtask_id', 'reference subtask'),
   Field('added_by', default=get_user_id),
   Field('added_time', default=get_time),
   Field('tag', 'reference tag')
)




db.commit()
