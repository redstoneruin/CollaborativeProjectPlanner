// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
         // Complete as you see fit.
         project: null,
         releases: [],
         members: [],

         name: "",
         desc: "",

         name_valid: false,
         desc_valid: false,

         adding_member: false,
         member_email: "",
         could_not_add_member: false,
         member_permissions: -1,
         member_permissions_name: "Select Permissions",

         dropdown_expanded: false
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.edit_project = () => {
      if(!app.vue.name_valid || !app.vue.desc_valid) {
         return;
      }

      axios.post(edit_project_info_url, {
         name: app.vue.name,
         desc: app.vue.desc
      })
         .then(function(response) {
            app.load_project_info();
         });
    }

    app.set_permissions = (perm) => {
      if(app.vue.perm < 0 || app.vue.perm > 2) return;

      app.vue.member_permissions = perm;

      if(!perm) {
         app.vue.member_permissions_name = "Member";
      } else if(perm == 1) {
         app.vue.member_permissions_name = "Planner";
      } else if(perm == 2) {
         app.vue.member_permissions_name = "Admin";
      }
      app.vue.dropdown_expanded = false;

    }

    app.get_perm_name = (perm) => {
      if(!perm) {
         return "Member";
      } else if(perm == 1) {
         return "Planner";
      } else if(perm == 2) {
         return "Admin";
      } else if (perm == 10) {
         return "Owner";
      }
      return "Invalid";
    }

    app.toggle_dropdown = () => {
      app.vue.dropdown_expanded = !app.vue.dropdown_expanded;
    }

    app.cancel_member_add = () => {
      app.vue.member_permissions_name = "Select Permissions";
      app.vue.member_permissions = -1;
      app.vue.could_not_add_member = false;
      app.vue.adding_member = false;
      app.vue.member_email = "";
    }

    app.validate_edit_form = () => {
      if(!app.vue.name) {
         app.vue.name_valid = false;
      } else {
         app.vue.name_valid = true;
      }
      app.vue.desc_valid = true;
    }

    app.add_member = () => {
      if(!app.vue.member_email.length
         || app.vue.member_permissions < 0
         || app.vue.member_permissions > 2) {
         app.vue.could_not_add_member = true;
         return;
      }
    
      axios.post(add_member_url, {
         email: app.vue.member_email,
         permissions: app.vue.member_permissions
      })
         .then(function(response) {
            if(response.data.added) {
               app.cancel_member_add();
               app.load_members();
            }

            app.vue.could_not_add_member = !response.data.added;
         })
    }

    app.redirect_to_project = () => {
        axios.get(get_app_name_url).then(function (response) {
            if(response.data.app_name == '_default') {
                window.location.href = '/project/' + app.vue.project.id;
            } else {
                window.location.href = '/' 
                  + response.data.app_name 
                  + '/project/' 
                  + app.vue.project.id;
            }
        });
    };


    app.load_members = () => {
      axios.get(load_project_members_url)
         .then(function(response) {
            app.vue.members = app.enumerate(response.data.members)
         });
    }

    app.set_adding_member = (adding) => {
      app.vue.adding_member = adding;
    }

    app.load_project_info = () => {
      axios.get(load_project_url).then(function(response) {
         app.vue.project = response.data.project;
         app.vue.releases = app.enumerate(response.data.releases);
         app.vue.name = response.data.project.project_name;
         app.vue.desc = response.data.project.project_desc;
         app.validate_edit_form();
      });
    }

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        redirect_to_project: app.redirect_to_project,
        validate_edit_form: app.validate_edit_form,
        edit_project: app.edit_project,

        set_adding_member: app.set_adding_member,
        toggle_dropdown: app.toggle_dropdown,
        cancel_member_add: app.cancel_member_add,
        set_permissions: app.set_permissions,
        add_member: app.add_member,
        get_perm_name: app.get_perm_name
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods,
        watch: {
        }
    });


    // And this initializes it.
    app.init = () => {
      app.load_project_info();
      app.load_members();
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
