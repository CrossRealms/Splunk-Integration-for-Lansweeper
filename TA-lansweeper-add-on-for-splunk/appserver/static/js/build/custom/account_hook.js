define([
    "jquery",
    "underscore",
    "backbone",
    "splunkjs/mvc","splunk.util"], function($, _, Backbone, mvc, splunkUtils)  {
    
    // Update CSRF token value from the cookie with JQuery ajaxPrefilter for CSRF validation
    // Below block of code is required while using jQuery in the account hook with UCC and OAuth as OAuth uses service.post() which requires CSRF validation with POST.
    var HEADER_NAME = 'X-Splunk-Form-Key';
    var FORM_KEY = splunkUtils.getFormKey();
    if (!FORM_KEY) {
        return;
    }
    if ($) {
        $.ajaxPrefilter(function(options, originalOptions, jqXHR) {
            if (options['type'] && options['type'].toUpperCase() == 'GET') return;
            FORM_KEY = splunkUtils.getFormKey();
            jqXHR.setRequestHeader(HEADER_NAME, FORM_KEY);
        });
    }
    
    class Hook {
        /**
         * Form hook
         * @constructor
         * @param {Object} globalConfig - Global configuration.
         * @param {object} serviceName - Service name
         * @param {object} model - Backbone model for form, not Splunk model
         * @param {object} util - {
                    displayErrorMsg,
                    addErrorToComponent
                    removeErrorFromComponent
                }.
         */
        constructor(globalConfig, serviceName, model, util) {
            this.globalConfig = globalConfig;
            this.serviceName = serviceName;
            this.model = model;
            this.util = util;
        }
        /*
         * This method will be called on create
         */
        onCreate() {
             //No implementation required as of now
        }

        /*
         * Put your render logic here. This function will be called on create or edit.
         */
        onRender() {
            // Clear passwords on render
            document.getElementsByClassName("input_auth")[1].value = ""
        }
        
    }
    return Hook;
});
