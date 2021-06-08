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
from .models import get_user_email, get_user_id, get_time
from py4web.utils.form import Form, FormStyleBulma
from .settings import APP_NAME

url_signer = URLSigner(session)

# home page with dashboard
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


# create project page
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


# project page with releases and tasks
@action('project/<project_id:int>', method=["GET"])
@action.uses(db, auth, auth.user, 
   url_signer, 
   'project.html')
def project(project_id = None):
   assert project_id is not None

   project = db.project[project_id]
   assert project is not None
   user_id = get_user_id()
   perms = get_user_perms(project_id, user_id)

   # not owner or member, redirect
   if perms >= 0:
      return dict(
         load_project_url = URL('load_project', project_id, signer=url_signer),
         create_release_url = URL('create_release', project_id, signer=url_signer),
         load_tasks_url = URL('load_tasks', signer=url_signer),
         create_task_url = URL('create_task', signer=url_signer),
         get_app_name_url = URL('get_app_name', signer=url_signer),
         delete_task_url = URL('delete_task', signer=url_signer),
         set_task_done_url = URL('set_task_done', signer=url_signer),
         task_done_percent_url = URL('task_done_percent', signer=url_signer),
         release_done_percent_url = URL('release_done_percent', signer=url_signer),
         edit_release_url = URL('edit_release', signer=url_signer),
         delete_release_url = URL('delete_release', signer=url_signer),
         get_user_info_url = URL('get_user_info', project_id, signer=url_signer)
      )
   else:
      redirect(URL('index'))

# edit project page
@action('edit_project/<project_id:int>', method=["GET"])
@action.uses(db, auth, auth.user, url_signer, 'edit_project.html')
def edit_project(project_id = None):
   assert project_id is not None

   project = db.project[project_id]
   assert project is not None
   user_id = get_user_id()

   perms = get_user_perms(project_id, user_id)


   # not owner or member, redirect
   if perms > 1:
      return dict(
         load_project_url = URL('load_project', project_id, signer=url_signer),
         get_app_name_url = URL('get_app_name', signer=url_signer),
         load_project_members_url = URL('load_project_members', 
            project_id, 
            signer=url_signer),
         get_user_email_url = URL('get_user_email', signer=url_signer),
         add_member_url = URL('add_member', project_id, signer=url_signer),
         edit_project_info_url = URL('edit_project_info', project_id, signer=url_signer),
         get_user_info_url = URL('get_user_info', project_id, signer=url_signer),
         delete_member_url = URL('delete_member', project_id, signer=url_signer),
         delete_project_url = URL('delete_project', project_id, signer=url_signer)
      )
   else:
      redirect(URL('index'))



# task page
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
         load_task_url = URL('load_task', task_id, signer=url_signer),
         add_subtask_url = URL('add_subtask', task_id, signer=url_signer),
         set_subtask_done_url = URL('set_subtask_done', signer=url_signer),
         task_done_percent_url = URL('task_done_percent', signer=url_signer),
         delete_subtask_url = URL('delete_subtask', signer=url_signer),
         edit_task_url = URL('edit_task', task_id, signer=url_signer),
         edit_subtask_url = URL('edit_subtask', signer=url_signer),
         set_task_done_url = URL('set_task_done', signer=url_signer),
         delete_task_url=URL('delete_task', signer=url_signer),

         project_url = URL('project', project.id),
         get_comments_url = URL('get_comments', task_id, signer=url_signer),
         post_comment_url = URL('post_comment', task_id, signer=url_signer),
         delete_comment_url = URL('delete_comment', signer=url_signer),
         get_user_info_url = URL('get_user_info', project.id, signer=url_signer)
      )


   redirect(URL('index'))

@action('delete_project/<project_id:int>', method=["POST"])
@action.uses(db, auth, auth.user, url_signer.verify())
def delete_project(project_id=None):
   assert project_id is not None

   user_id = get_user_id()
   project = db.project[project_id]
   assert project is not None

   if user_id != project.owner_id:
      return dict(deleted=False)

   db(db.project.id == project_id).delete()
   return dict(deleted=True)

# delete a member from a project
@action('delete_member/<project_id:int>', method=["POST"])
@action.uses(db, auth, auth.user, url_signer.verify())
def delete_member(project_id=None):
   assert project_id is not None

   member_id = request.json.get('member_id')

   db((db.member.project_id == project_id) 
      & (db.member.member_id == member_id)).delete()

   return dict(deleted=True)



# get the comments for a certain task
@action('get_comments/<task_id:int>', method=["GET"])
@action.uses(db, auth, auth.user, url_signer.verify())
def get_comments(task_id=None):
   assert task_id is not None

   comments = db(db.task_comment.task_id == task_id).select(orderby=~db.task_comment.timestamp).as_list()

   for comment in comments:
      comment["name"] = get_user_name(comment["author"])

   return dict(comments=comments)


# post a comment under a task
@action('post_comment/<task_id:int>', method=["POST"])
@action.uses(db, auth, auth.user, url_signer.verify())
def post_comment(task_id=None):
   assert task_id is not None

   data=request.json.get('data')

   assert data is not None
   assert len(data)

   db.task_comment.insert(
      task_id=task_id,
      data=data
   )

   return dict(posted=True)

# delete a comment
@action('delete_comment', method=["POST"])
@action.uses(db, auth, auth.user, url_signer.verify())
def delete_comment():

   comment_id = request.json.get('comment_id')
   assert comment_id is not None

   comment = db.task_comment[comment_id]

   user_id = get_user_id()
   if comment.author != str(user_id): 
      print(comment, user_id)
      return dict(deleted=False)

   db(db.task_comment.id == comment_id).delete()

   return dict(deleted=True)
   


# edit a task
@action('edit_task/<task_id:int>', method=["POST"])
@action.uses(db, auth, auth.user, url_signer.verify())
def edit_task(task_id=None):
   assert task_id is not None
   task_name = request.json.get('name')
   desc = request.json.get('desc')
   due_date = request.json.get('duedate')

   assert task_name is not None and desc is not None

   db(db.task.id == task_id).update(
      task_name=task_name,
      desc=desc,
      due_date=due_date
   )

   return dict(edited=True)

@action('edit_subtask', method=["POST"])
@action.uses(db, auth, auth.user, url_signer.verify())
def edit_subtask():
   subtask_id = request.json.get('subtask_id')
   subtask_name = request.json.get('name')
   desc = request.json.get('desc')
   due_date = request.json.get('duedate')

   assert subtask_id is not None
   assert subtask_name is not None 
   assert desc is not None

   db(db.subtask.id == subtask_id).update(
      subtask_name=subtask_name,
      desc=desc,
      due_date=due_date
   )

   return dict(edited=True)

@action('edit_release', method=["POST"])
@action.uses(db, auth, auth.user, url_signer.verify())
def edit_release():
   release_id = request.json.get('release_id')
   release_name = request.json.get('name')
   due_date = request.json.get('duedate')
   assert release_id is not None
   assert release_name is not None
   assert due_date is not None

   db(db.release.id == release_id).update(
      release_name=release_name,
      due_date=due_date   
   )

   return dict(edited=True)

@action('delete_release', method=["POST"])
@action.uses(db, auth, auth.user, url_signer.verify())
def delete_release():
   release_id = request.json.get('release_id')

   assert release_id is not None

   db(db.release.id == release_id).delete()

   return dict(deleted=True) 

# load a single task and subtasks
@action('load_task/<task_id:int>', method=["GET"])
@action.uses(auth, auth.user, url_signer.verify())
def load_task(task_id=None):
   assert task_id is not None

   task = db(db.task.id == task_id).select().first().as_dict()
   subtasks = db(db.subtask.task_id == task_id).select().as_list()

   # decorate task with doneness
   num_subtasks = len(subtasks)
   done_sum = 0

   task["done_percent"] = get_done_percent(task["id"], task["done"])

   return dict(task=task, subtasks=subtasks)

# mark a task's doneness
@action('set_task_done', method=["POST"])
@action.uses(auth, auth.user, url_signer.verify())
def set_task_done():
   task_id = request.json.get('task_id')
   assert task_id is not None
   done = request.json.get('done')
   assert done is not None

   # update the task
   db(db.task.id == task_id).update(
      done=done,
      done_time=get_time()
   )

   return dict(updated=True)

# mark a subtask's doneness
@action('set_subtask_done', method=["POST"])
@action.uses(auth, auth.user, url_signer.verify())
def set_subtask_done():
   subtask_id = request.json.get('subtask_id')
   assert subtask_id is not None
   done = request.json.get('done')
   assert done is not None

   # update the subtask
   db(db.subtask.id == subtask_id).update(
      done=done,
      done_time=get_time()
   )

   return dict(updated=True)

# get the percent a task is done
@action('task_done_percent', method=["GET"])
@action.uses(auth, auth.user, url_signer.verify())
def task_done_percent():
   task_id = request.params.get('task_id')
   assert task_id is not None
   task = db.task[task_id]
   assert task is not None

   done_percent = get_done_percent(task_id, task.done)

   return dict(done_percent=done_percent)

#get the percent a release is done
@action('release_done_percent', method=["GET"])
@action.uses(auth, auth.user, url_signer.verify())
def release_done_percent():
   release_id = request.params.get('release_id')
   assert release_id is not None
   release = db.release[release_id]
   assert release is not None

   done_percent = get_release_done_percent(release_id)

   return dict(done_percent=done_percent)

# add a subtask to a given task
@action('add_subtask/<task_id:int>', method=["POST"])
@action.uses(auth, auth.user, url_signer.verify())
def add_subtask(task_id=None):
   assert task_id is not None

   subtask_name = request.json.get('name')
   desc = request.json.get('desc')
   due_date = request.json.get('duedate')

   if(not len(subtask_name)): return dict(added=False)

   db.subtask.insert(
      task_id=task_id,
      subtask_name=subtask_name,
      desc=desc,
      due_date=due_date
   )

   return dict(added=True)

# delete a subtask
@action('delete_subtask', method=["POST"])
@action.uses(auth, auth.user, url_signer.verify())
def delete_subtask():
   subtask_id = request.json.get('subtask_id')
   assert subtask_id is not None

   db(db.subtask.id == subtask_id).delete()

   return dict(deleted=True)

# edit name and description of a project
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


# get user with name, email and permissions
@action('get_user_info/<project_id:int>', method=["GET"])
@action.uses(db, auth, auth.user, url_signer.verify())
def get_user_info(project_id=None):
   assert project_id is not None
   user = {}

   user_id = get_user_id()
   assert user_id is not None
   user_name = get_user_name(user_id)
   user_email = db.auth_user[user_id].email
   user_perms = get_user_perms(project_id, user_id)

   user["id"] = user_id
   user["name"] = user_name
   user["email"] = user_email
   user["perms"] = user_perms

   return dict(user=user)


# add a member to a project with specified permissions
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
   
   if not len(projects): 
      return dict(project=None, releases=None)
   
   releases = db(db.release.project_id == project_id).select().as_list()

   # get done percent for each release
   for release in releases:
      release["done_percent"] = get_release_done_percent(release["id"])

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


# load the members for a project
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
   ownerDict["permissions"] = 10

   members.insert(0, ownerDict)


   return dict(members=members)


# load the tasks for a given release
@action('load_tasks', method=["GET"])
@action.uses(url_signer.verify(), db)
def load_tasks():
   tasks = db(db.task.release_id == request.params.get('release_id')).select().as_list()

   # decorate with doneness
   for task in tasks:
      task["done_percent"] = get_done_percent(task["id"], task["done"])

   return dict(tasks=tasks)

# get the done percentage for a task
def get_done_percent(task_id=None, task_done=None):
   assert task_id is not None and task_done is not None

   if task_done:
      return 100

   subtasks = db(db.subtask.task_id == task_id).select()
   num_subtasks = len(subtasks)
   done_sum = 0

   if not num_subtasks: return 0

   # add one so if not done, the task progress bar will not be full
   num_subtasks += 1

   for subtask in subtasks:
      if subtask.done: done_sum += 1

   return done_sum / num_subtasks * 100

# get the done percentage for a release
def get_release_done_percent(release_id=None):
   assert release_id is not None

   tasks = db(db.task.release_id == release_id).select()
   num_tasks = len(tasks)
   done_sum = 0

   if not num_tasks: return 100

   for task in tasks:
      done_percent = get_done_percent(task.id, task.done)
      done_sum += done_percent / 100

   return done_sum / num_tasks * 100

# get user permissions, 10 for owner
def get_user_perms(project_id=None, user_id=None):
   assert project_id is not None and user_id is not None

   project = db.project[project_id]
   assert project is not None

   # check if owner
   if project.owner_id == user_id: return 10

   member = db((db.member.project_id == project_id) 
      & (db.member.member_id == user_id)).select().first();
   
   if member is None: return -1
   return member.permissions

def get_user_name(user_id=None):
   assert user_id is not None
   user = db.auth_user[user_id]
   assert user is not None

   name = user.first_name
   if len(user.last_name):
      name += " " + user.last_name

   return name


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

