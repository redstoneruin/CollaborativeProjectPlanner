let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        project: null,
        releases: [],
        adding_release: false,
        new_release_name: "",
        new_release_duedate: null,
        name_valid: false,
        duedate_valid: false,
        warn_check_inputs: false
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.decorate_releases = (a) => {
      a.map((e, idx) => {
         e._expanded = true;
         e._adding_task = false;
         e._tasks_loaded = false;

         e._new_task_name = "";
         e._new_task_desc = "";
         e._new_task_duedate = null;

         e._task_name_valid = false;
         e._task_duedate_valid = true;
         e._task_desc_valid = false;
         e._warn_check_inputs = false;

         e._tasks = [];
      });

      return a;
    }

    app.load_tasks = (idx) => {

         axios.get(load_tasks_url, 
            {params: {release_id: app.vue.releases[idx].id}})
            .then(function(response) {
               app.vue.releases[idx]._tasks = app.enumerate(response.data.tasks);
               app.vue.releases[idx]._tasks_loaded = true;
            });
    };


    app.toggle_expanded = (idx) => {
      app.vue.releases[idx]._expanded = !app.vue.releases[idx]._expanded; 
    }

    app.set_adding_release = (adding) => {
      app.vue.adding_release = adding;
    }

    app.set_adding_task = (adding, idx) => {
      app.vue.releases[idx]._adding_task = adding;
    }

    app.validate_task_form = (idx) => {
      // check name
      if(app.vue.releases[idx]._new_task_name.length) {
         app.vue.releases[idx]._task_name_valid = true;
      } else {
         app.vue.releases[idx]._task_name_valid = false;
      }

      // check desc
      if(app.vue.releases[idx]._new_task_desc.length) {
         app.vue.releases[idx]._task_desc_valid = true;
      } else {
         app.vue.releases[idx]._task_desc_valid = false;
      }

      app.vue.releases[idx]._task_duedate_valid = true;
    }

    app.validate_release_form = () => {
      // check name
      if(app.vue.new_release_name.length) {
         app.vue.name_valid = true;
      } else {
         app.vue.name_valid = false;
      }
      // check duedate
      if(app.vue.new_release_duedate) {
         app.vue.duedate_valid = true;
      } else {
         app.vue.duedate_valid = false;
      }
    }

    // called when canceling form to add new task in a release
    app.cancel_task_add = (idx) => {
      app.vue.releases[idx]._task_name_valid = false;
      app.vue.releases[idx]._task_duedate_valid = false;
      app.vue.releases[idx]._task_desc_valid = false;

      app.vue.releases[idx]._new_task_name = "";
      app.vue.releases[idx]._new_task_desc = "";
      app.vue.releases[idx]._new_task_duedate = "";

      app.vue.releases[idx]._warn_check_inputs = false;
      app.vue.releases[idx]._adding_task = false;
    }

    // called when submitting form to create new task in a release
    app.submit_new_task = (idx) => {
      if(!app.vue.releases[idx]._task_name_valid
         || !app.vue.releases[idx]._task_desc_valid
         || !app.vue.releases[idx]._task_duedate_valid) {
         app.vue.releases[idx]._warn_check_inputs = true;
      } else {
         let release_id = app.vue.releases[idx].id;
         let task_name = app.vue.releases[idx]._new_task_name;
         let desc = app.vue.releases[idx]._new_task_desc;
         let due_date = app.vue.releases[idx]._new_task_duedate;
         axios.post(create_task_url, {
            release_id: release_id,
            task_name: task_name,
            desc: desc,
            due_date: due_date 
         }).then(function(response) {
            app.cancel_task_add(idx);
            app.load_tasks(idx);
         });
      }
    }

    // called when canceling form to create new release
    app.cancel_release_add = () => {
      app.vue.name_valid = false;
      app.vue.duedate_valid = false;
      app.vue.new_release_name = "";
      app.vue.new_release_duedate = null;
      app.vue.warn_check_inputs = false;
      app.vue.adding_release = false;
    }

    // called when the form to create a new release is submitted
    app.submit_new_release = () => {
      if(!app.vue.name_valid || !app.vue.duedate_valid) {
         app.vue.warn_check_inputs = true;
      } else {
         let due_date = app.vue.new_release_duedate;
         let release_name = app.vue.new_release_name;
         axios.post(create_release_url, {
            release_name: release_name, 
            due_date: due_date
         }).then(function(response) {
            // todo: handling for bad response
            app.cancel_release_add();
            app.load_project();
         });
      }
    }


    // load project, including release information
    app.load_project = () => {
      axios.get(load_project_url).then(function (response) {
         app.vue.project = response.data.project;
         app.vue.releases = app.decorate_releases(app.enumerate(response.data.releases));
      });
    }

    // watch releases and update tasks when loaded
    app.release_watcher = () => {
      var length = app.vue.releases.length;
      for(var i = 0; i != length; i++) {
         app.load_tasks(i);
      }
    }

    app.redirect_to_edit = () => {
        axios.get(get_app_name_url).then(function (response) {
            if(response.data.app_name == '_default') {
                window.location.href = '/edit_project/' + app.vue.project.id;
            } else {
                window.location.href = '/' 
                  + response.data.app_name 
                  + '/edit_project/' 
                  + app.vue.project.id;
            }
        });
    };

    app.redirect_to_task = (task_id) => {
      axios.get(get_app_name_url).then(function(response) {
         if(response.data.app_name == '_default') {
                window.location.href = '/task/' + task_id;
            } else {
                window.location.href = '/' 
                  + response.data.app_name 
                  + '/task/' 
                  + task_id;
            }
      })
    }

    app.delete_task = (idx, task_id) => {
      axios.post(delete_task_url, {task_id: task_id})
         .then(function(response) {
            app.load_tasks(idx);
         });
    }

    app.set_task_done = (r_idx, t_idx, done) => {
      task = app.vue.releases[r_idx]._tasks[t_idx];

      axios.post(set_task_done_url, {
         task_id: task.id,
         done: done
      })
         .then(function(response) {
            app.vue.releases[r_idx]._tasks[t_idx].done = done;
            app.update_done_percent(r_idx, t_idx);
         });
    }


    app.update_done_percent = (r_idx, t_idx) => {
      axios.get(task_done_percent_url, {
         params: {task_id: app.vue.releases[r_idx]._tasks[t_idx].id}
      })
         .then(function(response) {
            app.vue.releases[r_idx]._tasks[t_idx].done_percent = response.data.done_percent;
         });
    }

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        set_adding_release: app.set_adding_release,
        cancel_release_add: app.cancel_release_add,
        submit_new_release: app.submit_new_release,
        validate_release_form: app.validate_release_form,

        toggle_expanded: app.toggle_expanded,

        set_adding_task: app.set_adding_task,
        validate_task_form: app.validate_task_form,
        submit_new_task: app.submit_new_task,
        cancel_task_add: app.cancel_task_add,
        
        delete_task: app.delete_task,

        load_tasks: app.load_tasks,
        release_watcher: app.release_watcher,

        redirect_to_edit: app.redirect_to_edit,
        redirect_to_task: app.redirect_to_task,

        set_task_done: app.set_task_done
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods,
        watch: {
         releases: 'release_watcher'
        }
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        app.load_project();
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
