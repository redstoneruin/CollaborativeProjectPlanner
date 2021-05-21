// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        myprojects: [],
        memberprojects: []
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.redirect_to_project = (project_id) => {
        axios.get(get_app_name_url).then(function (response) {
            if(response.data.app_name == '_default') {
                window.location.href = '/project/' + project_id;
            } else {
                window.location.href = '/' + response.data.app_name + '/project/' + project_id;
            }
        });
    };

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        redirect_to_project: app.redirect_to_project
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // get my projects
        axios.get(load_my_projects_url).then(function (response) {
            app.vue.myprojects = app.enumerate(response.data.myprojects);
        });
        axios.get(load_member_projects_url).then(function (response) {
            app.vue.memberprojects = app.enumerate(response.data.memberprojects);
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
