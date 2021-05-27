let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        task: null,
        subtasks: [],

        adding_subtask: false,
        subtask_name: "",
        subtask_desc: "",
        subtask_duedate: null,

        name_valid: false,
        desc_valid: false,
        duedate_valid: true,

        warn_check_inputs: false
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.set_adding_subtask = (adding_subtask) => {
      app.vue.adding_subtask = adding_subtask;
    }

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

    app.validate_subtask = () => {
      if(app.vue.subtask_name.length) app.vue.name_valid = true;
      if(app.vue.subtask_desc.length) app.vue.desc_valid = true;
      app.vue.duedate_valid = true;
    }

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

    app.update_done_percent = () => {
      axios.get(task_done_percent_url, {
         params: {task_id: app.vue.task.id}
      })
         .then(function(response) {
            app.vue.task.done_percent = response.data.done_percent;
         });
    }

    app.load_task = () => {
      axios.get(load_task_url)
         .then(function(response) {
            app.vue.task = response.data.task;
            app.vue.subtasks = app.enumerate(response.data.subtasks);
         });
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
        delete_subtask: app.delete_subtask
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
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
