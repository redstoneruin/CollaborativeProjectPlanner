"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, Field, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email, get_user_id
from py4web.utils.form import Form, FormStyleBulma
from .settings import APP_NAME

url_signer = URLSigner(session)

@action('index')
@action.uses(db, auth, auth.user, url_signer, 'index.html')
def index():

   return dict(
      # COMPLETE: return here any signed URLs you need.
      load_my_projects_url = URL('load_my_projects', signer=url_signer),
      load_member_projects_url = URL('load_member_projects', signer=url_signer),
      get_app_name_url = URL('get_app_name', signer=url_signer),
      url_signer = url_signer
   )



@action('create', method=["GET","POST"])
@action.uses(db, auth, auth.user, 
   url_signer, url_signer.verify(), 
   'create.html')
def create():

   # basic create form, to be replaced with vue implementation
   form = Form([Field('name'), Field('description')], 
      csrf_session=session,
      formstyle=FormStyleBulma,
      deletable=False)

   if form.accepted:
      db.project.insert(project_name = form.vars['name'],
         project_desc = form.vars['description'])
      redirect(URL('index'))

   return dict(form=form, url_signer=url_signer)



@action('project/<project_id:int>', method=["GET"])
@action.uses(db, auth, auth.user, 
   url_signer, 
   'project.html')
def project(project_id = None):
   assert project_id is not None

   project = db.project[project_id]
   assert project is not None
   user_id = get_user_id()
   has_access = False

   # determine if user is owner or member of the project
   if(project.owner_id != user_id):
      # check whether user is a member
      members = db(db.member.project_id == project_id).select()
      for member in members:
         if member.member_id == user_id:
            has_access = True
   else:
      has_access = True

   # not owner or member, redirect
   if has_access:
      return dict(
         load_project_url = URL('load_project', project_id, signer=url_signer),
         create_release_url = URL('create_release', project_id, signer=url_signer),
         load_tasks_url = URL('load_tasks', signer=url_signer),
         create_task_url = URL('create_task', signer=url_signer),
         get_app_name_url = URL('get_app_name', signer=url_signer),
         delete_task_url = URL('delete_task', signer=url_signer)
      )
   else:
      redirect(URL('index'))

@action('edit_project/<project_id:int>', method=["GET"])
@action.uses(db, auth, auth.user, url_signer, 'edit_project.html')
def edit_project(project_id = None):
   assert project_id is not None

   project = db.project[project_id]
   assert project is not None
   user_id = get_user_id()
   has_access = False

   # determine if user is owner or member of the project
   if(project.owner_id != user_id):
      # check whether user is a member
      members = db(db.member.project_id == project_id).select()
      for member in members:
         if member.member_id == user_id:
            has_access = True
   else:
      has_access = True

   # not owner or member, redirect
   if has_access:
      return dict(
         load_project_url = URL('load_project', project_id, signer=url_signer),
         get_app_name_url = URL('get_app_name', signer=url_signer),
         load_project_members_url = URL('load_project_members', 
            project_id, 
            signer=url_signer),
         get_user_email_url = URL('get_user_email', signer=url_signer),
         add_member_url = URL('add_member', project_id, signer=url_signer),
         edit_project_info_url = URL('edit_project_info', project_id, signer=url_signer)
      )
   else:
      redirect(URL('index'))

@action('task/<task_id:int>', method=["GET"])
@action.uses(auth, auth.user, url_signer, 'task.html')
def task(task_id=None):
   assert task_id is not None

   task = db.task[task_id]
   assert task is not None
   release = db.release[task.release_id]
   assert release is not None
   project = db.project[release.project_id]
   assert project is not None

   user_id = get_user_id()
   has_access = False

   # determine if user is owner or member of the project
   if(project.owner_id != user_id):
      # check whether user is a member
      members = db(db.member.project_id == project.id).select()
      for member in members:
         if member.member_id == user_id:
            has_access = True
   else:
      has_access = True

   if has_access:
      return dict(
         load_task_url = URL('load_task', task_id, signer=url_signer)
      )


   redirect(URL('index'))

@action('load_task/<task_id:int>', method=["GET"])
@action.uses(auth, auth.user, url_signer.verify())
def load_task(task_id=None):
   assert task_id is not None

   task = db(db.task.id == task_id).select().as_list()[0]
   subtasks = db(db.subtask.task_id == task_id).select().as_list()

   return dict(task=task, subtasks=subtasks)


@action('edit_project_info/<project_id:int>', method=["POST"])
@action.uses(db, auth, auth.user, url_signer.verify())
def edit_project_info(project_id=None):
   assert project_id is not None

   project_name = request.json.get('name')
   project_desc = request.json.get('desc')

   if not len(project_name):
      return dict(edited=False)

   db(db.project.id == project_id).update(
      project_name=project_name,
      project_desc=project_desc
   )

   return dict(edited=True)

# get a user based on either user id or email
@action('get_user_email', method=["GET"])
@action.uses(db, auth, auth.user, url_signer.verify())
def get_user_email():
   user_id = request.params.get('user_id')

   email = db.auth_user[user_id].email

   return dict(email=email, index=request.params.get('index'))

@action('add_member/<project_id:int>', method=["POST"])
@action.uses(db, auth, auth.user, url_signer.verify())
def add_member(project_id = None):
   assert project_id is not None

   email = request.json.get('email')
   permissions = request.json.get('permissions')

   # check permissions in range 
   if permissions < 0 or permissions > 2:
      return dict(added=False)

   user = db(db.auth_user.email == email).select().first()
   
   # check if user actually exists
   if user is None:
      return dict(added=False)

   # check if user is already member
   project_user = db((db.member.project_id == project_id)
      & (db.member.member_id == user.id)).select().first()

   if project_user is not None:
      return dict(added=False)

   # check if user is project owner
   project = db.project[project_id]

   if project.owner_id == user.id:
      return dict(added=False)

   # add member
   db.member.insert(
      project_id=project_id,
      member_id=user.id,
      permissions=permissions
   )

   return dict(added=True)



# load project and releases with the given project id
@action('load_project/<project_id:int>', method=["GET"])
@action.uses(url_signer.verify(), db)
def load_project(project_id = None):
   assert project_id is not None

   projects = db(db.project.id == project_id).select().as_list()
   
   if len(projects) == 0: 
      return dict(project=None, releases=None)
   
   releases = db(db.release.project_id == project_id).select().as_list()
   return dict(project=projects[0], releases=releases)


# load the user's owned projects
@action('load_my_projects', method=["GET"])
@action.uses(url_signer.verify(), db)
def load_my_projects():
   myprojects = db(db.project.owner_id == get_user_id()).select().as_list()
   return dict(myprojects=myprojects)


@action('load_member_projects', method=["GET"])
@action.uses(url_signer.verify(), db)
def load_member_projects():
   memberprojects = []
   membership = db(db.member.member_id == get_user_id()).select().as_list()
   for member in membership:
      proj = db(db.project.id == member["project_id"]).select().as_list()[0]
      memberprojects.append(proj)
   return dict(memberprojects=memberprojects)


@action('load_project_members/<project_id:int>', method=["GET"])
@action.uses(url_signer.verify(), db)
def load_project_members(project_id = None):
   assert project_id is not None

   members = db(db.member.project_id == project_id).select().as_list()
   for member in members:
      member["email"] = db.auth_user[member["member_id"]].email

   project = db.project[project_id]

   ownerDict={}

   ownerDict["member_id"] = project.owner_id
   ownerDict["email"] = db.auth_user[project.owner_id].email
   ownerDict["permissions"] = -1

   members.insert(0, ownerDict)


   return dict(members=members)


# load the tasks for a given release
@action('load_tasks', method=["GET"])
@action.uses(url_signer.verify(), db)
def load_tasks():
   tasks = db(db.task.release_id == request.params.get('release_id')).select().as_list()
   return dict(tasks=tasks)


# create a task in a given release
@action('create_task', method=["POST"])
@action.uses(url_signer.verify())
def create_task():
   assert request.json.get('release_id') is not None

   db.task.insert(
      release_id=request.json.get('release_id'),
      task_name=request.json.get('task_name'),
      desc=request.json.get('desc'),
      due_date=request.json.get('due_date')
   )
   created=True
   return dict(created=created)


@action('delete_task', method=["POST"])
@action.uses(auth, auth.user, url_signer.verify())
def delete_task():
   assert request.json.get('task_id') is not None

   db(db.task.id == request.json.get('task_id')).delete()

   return dict(deleted=True)




# simple function to get the current app name for javascript redirects
@action('get_app_name', method=["GET"])
@action.uses(url_signer.verify())
def get_app_name():
   return dict(app_name=APP_NAME)


# create new release
@action('create_release/<project_id:int>', method=["POST"])
@action.uses(url_signer.verify())
def create_release(project_id = None):
   assert project_id is not None

   db.release.insert(
      project_id=project_id,
      release_name=request.json.get('release_name'),
      due_date=request.json.get('due_date')
      )
   created = True
   return dict(created=created)

