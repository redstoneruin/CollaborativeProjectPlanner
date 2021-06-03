let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        task: null,
        subtasks: [],

        editing_task: false,
        task_name: "",
        task_desc: "",
        task_duedate: "",

        adding_subtask: false,
        subtask_name: "",
        subtask_desc: "",
        subtask_duedate: null,

        name_valid: false,
        desc_valid: false,
        duedate_valid: true,

        edited_name_valid: true,
        edited_desc_valid: true,
        edited_duedate_valid: true,

        warn_check_inputs: false,
        warn_check_edit_inputs: false,


        comments: [],
        adding_comment: false,
        comment_data: "",
        comment_valid: false
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.decorate_subtasks = (a) => {
      a.map((e) => {
         e.edited_name = e.subtask_name;
         e.edited_duedate = e.due_date;
         e.edited_desc = e.desc;

         e.name_valid = true;
         e.desc_valid = true;
         e.duedate_valid = true;

         e.editing = false;
         e.warn_check_inputs = false;
      });
      return a;
    }

    app.set_adding_comment = (adding) => {
      app.vue.adding_comment = adding;
    }

    app.cancel_adding_comment = (adding) => {
      app.vue.comment_data = "";
      app.vue.adding_comment = false;
    }

    app.validate_comment = () => {
      if(app.vue.comment_data.length) {
         app.vue.comment_valid = true;
      } else {
         app.vue.comment_valid = false;
      }
    }

    app.load_comments = () => {
      axios.get(get_comments_url)
         .then(function(response) {
            app.vue.comments = response.data.comments;
            console.log(response.data.comments);
         });
    }

    app.post_comment = () => {
      if(!app.vue.comment_valid) return;

      axios.post(post_comment_url, {
         data: app.vue.comment_data
      })
         .then(function(response) {
            if(response.data.posted) {
               app.cancel_adding_comment();
               app.load_comments();
            }
         });
    }


    app.set_editing_task = (adding) => {
      app.vue.editing_task = adding;
    }

    app.cancel_editing_task = () => {
      t = app.vue.task;
      app.vue.task_name = t.task_name;
      app.vue.task_desc = t.desc;
      app.vue.task_duedate = t.due_date;

      app.vue.edited_name_valid = true;
      app.vue.edited_desc_valid = true;
      app.vue.edited_duedate_valid = true;

      app.vue.warn_check_edit_inputs = false;
      app.vue.editing_task = false;

    }

    // validate the edit form for task
    app.validate_edited_task = () => {
      if(!app.vue.task_name.length) {
         app.vue.edited_name_valid = false;
      } else {
         app.vue.edited_name_valid = true;
      }
      if(!app.vue.task_desc.length) {
         app.vue.edited_desc_valid = false;
      } else {
         app.vue.edited_desc_valid = true;
      }

      app.vue.edited_duedate_valid = true;
    }

    // publish the edit to a task, given inputs valid
    app.edit_task = () => {
      if(!app.vue.edited_name_valid
         || !app.vue.edited_desc_valid
         || !app.vue.edited_duedate_valid) {
         app.vue.warn_check_edit_inputs = true;
         return;
      }

      axios.post(edit_task_url, {
         name: app.vue.task_name,
         desc: app.vue.task_desc,
         duedate: app.vue.task_duedate
      })
         .then(function(response) {
            if(response.data.edited) {
               app.load_task();
               app.cancel_editing_task();
            }
         })
    }

    // set the openness of the edit form for a particular subtask
    app.set_editing_subtask = (idx, editing) => {
      app.vue.subtasks[idx].editing = editing;
    }

    // cancel editing a particular subtask
    app.cancel_editing_subtask = (idx) => {
      s = app.vue.subtasks[idx];

      app.vue.subtasks[idx].edited_name = s.subtask_name;
      app.vue.subtasks[idx].edited_duedate = s.due_date;
      app.vue.subtasks[idx].edited_desc = s.desc;

      app.vue.subtasks[idx].name_valid = true;
      app.vue.subtasks[idx].desc_valid = true;
      app.vue.subtasks[idx].duedate_valid = true;

      app.vue.subtasks[idx].editing = false;
      app.vue.subtasks[idx].warn_check_inputs = false;
    }

    app.validate_edited_subtask = (idx) => {
      s = app.vue.subtasks[idx];
      if(s.edited_name.length) {
         app.vue.subtasks[idx].name_valid = true;
      } else {
         app.vue.subtasks[idx].name_valid = false;
      }

      if(s.edited_desc.length) {
         app.vue.subtasks[idx].desc_valid = true;
      } else {
         app.vue.subtasks[idx].desc_valid = false;
      }

      app.vue.subtasks[idx].duedate_valid = true;
    }

    // submit an edited subtask
    app.edit_subtask = (idx) => {
      app.validate_edited_subtask(idx);
      s = app.vue.subtasks[idx];
      if(!s.name_valid || !s.desc_valid || !s.duedate_valid) {
         app.vue.subtasks[idx].warn_check_inputs = true;
         return;
      }

      axios.post(edit_subtask_url, {
         subtask_id: s.id,
         name: s.edited_name,
         desc: s.edited_desc,
         duedate: s.edited_duedate
      })
         .then(function(response) {
            if(response.data.edited) {
               app.cancel_editing_subtask(idx);
               app.load_task();
            } else {
               app.vue.subtasks[idx].warn_check_inputs = true;
            }
         })
    }

    // set whether form for adding task is open
    app.set_adding_subtask = (adding) => {
      app.vue.adding_subtask = adding;
    }

    // cancel the form for adding a new subtask
    app.cancel_adding_subtask = () => {
      app.vue.adding_subtask = false;

      app.vue.subtask_name = "";
      app.vue.subtask_desc = "";
      app.vue.subtask_duedate = null;
    
      app.vue.name_valid = false;
      app.vue.desc_valid = false;
      app.vue.duedate_valid = true;

      app.vue.warn_check_inputs = false;
    }

    // add a new subtask, update list
    app.submit_new_subtask = () => {
      if(!app.vue.name_valid
         || !app.vue.desc_valid
         || !app.vue.duedate_valid)
         app.vue.warn_check_inputs

      axios.post(add_subtask_url, {
         name: app.vue.subtask_name,
         desc: app.vue.subtask_desc,
         duedate: app.vue.subtask_duedate
      })
         .then(function(response) {
            if(response.data.added) {
               app.cancel_adding_subtask();
               app.load_task();
            } else {
               app.vue.warn_check_inputs = true;
            }
         });
      app.vue.warn_check_inputs = true;
    }

    // delete a subtask, update list
    app.delete_subtask = (idx) => {
      axios.post(delete_subtask_url, {
         subtask_id: app.vue.subtasks[idx].id
      })
         .then(function(response) {
            if(response.data.deleted) {
               app.load_task();
            }
         })
    }

    // validate form for adding subtask
    app.validate_subtask = () => {
      if(app.vue.subtask_name.length) app.vue.name_valid = true;
      else app.vue.name_valid = false;
      if(app.vue.subtask_desc.length) app.vue.desc_valid = true;
      else app.vue.desc_valid = false;
      app.vue.duedate_valid = true;
    }

    // set the task's doneness
    app.set_task_done = (done) => {
      axios.post(set_task_done_url, {
         task_id: app.vue.task.id,
         done: done
      })
         .then(function(response) {
            if(response.data.updated) {
               app.vue.task.done = done;
               app.update_done_percent();
            }
         });
    }

    // set a subtask's doneness, update task progress
    app.set_subtask_done = (idx, done) => {
      subtask = app.vue.subtasks[idx];
      axios.post(set_subtask_done_url, {
         subtask_id: subtask.id,
         done: done
      })
         .then(function(response) {
            if(response.data.updated) {
               app.vue.subtasks[idx].done = done;
               app.update_done_percent();
            }
         });
    }

    // update the progress bar for the task
    app.update_done_percent = () => {
      axios.get(task_done_percent_url, {
         params: {task_id: app.vue.task.id}
      })
         .then(function(response) {
            app.vue.task.done_percent = response.data.done_percent;
         });
    }

    // load task and subtasks
    app.load_task = () => {
      axios.get(load_task_url)
         .then(function(response) {
            app.vue.task = response.data.task;
            app.vue.subtasks = app.decorate_subtasks(
               app.enumerate(response.data.subtasks)
            );
            app.cancel_editing_task();
         });
    
   }
  
   // delete the task 
    app.delete_task = () => {
      axios.post(delete_task_url, {
         task_id: app.vue.task.id
      })
         .then(function(response) {
            if(response.data.deleted) {
               window.location.href = project_url; 
            }
         })
    }
    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        load_task: app.load_task,
        set_adding_subtask: app.set_adding_subtask,
        cancel_adding_subtask: app.cancel_adding_subtask,
        submit_new_subtask: app.submit_new_subtask,
        validate_subtask: app.validate_subtask,
        submit_new_subtask: app.submit_new_subtask,
        set_subtask_done: app.set_subtask_done,
        delete_subtask: app.delete_subtask,

        set_editing_task: app.set_editing_task,
        cancel_editing_task: app.cancel_editing_task,
        validate_edited_task: app.validate_edited_task,
        edit_task: app.edit_task,
        

        set_editing_subtask: app.set_editing_subtask,
        cancel_editing_subtask: app.cancel_editing_subtask,
        validate_edited_subtask: app.validate_edited_subtask,
        edit_subtask: app.edit_subtask,
        set_task_done: app.set_task_done,

        delete_task: app.delete_task,

        validate_comment: app.validate_comment,
        set_adding_comment: app.set_adding_comment,
        cancel_adding_comment: app.cancel_adding_comment,
        load_comments: app.load_comments,
        post_comment: app.post_comment
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
      app.load_task();
      app.load_comments();
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
