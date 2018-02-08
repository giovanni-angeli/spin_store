'use strict';

var Pages = {

    current_instance: null,          // instance of Page, of currently open page

    home_page_name: null,    // i.e. kiosk.home

    data: {
        global: {
            /*
            // data shared among all pages

            dispensation_notes: {
                // when creating a new dispensation, this "dict",
                // json-ned, is passed to be added in the
                // 'notes' field of the dispensation
                // (see machine/ajax.py -> dispense_color
                // can be used by any app for this purpose
            }

            params: {
                // received in main.html, see Kiosk.Pages.init
                language
                logo_url
                use_labeler
                commands
            }
            */
        }

        /*
        kiosk: {
            // data shared among all kiosk's pages
            // just logical separation (non enforced)

            // used to make user user isn't charged money twice
            charged
        },

        freesample: { ... }

        */
    }

    /*
    kiosk: {
        home
        select_color
        confirm_selection
        progress_bar
        dispensed
    },

    freesample: {
        home
        insert_code
        code_valid
        registration_form
        registration_done
    },

    */
};

Pages.get_page = function(page_name) {
    // page full names are formed by 2 dot-separated parts: app_name.page_name
    // ie kiosk.select_color,  freesample.insert_code
    if (page_name == 'HOME')
        return Pages.get_page(Pages.home_page_name);

    var split = page_name.split('.');
    var app_name = split[0];
    var name = split[1];

    var ret = null;
    //~ var ret = Pages[app_name][name];

    console.log('get_page("%o") --> %o', page_name, ret);

    // if page doesn't exist, just create a default page, and load html
    return ret? ret : new Page(app_name, name);
};

Pages.current = function (page_instance) {
    if (page_instance === undefined)
        return Pages.current_instance;

    Pages.current_instance = page_instance;
};

Pages.init = function (home_page_name, params) {
    // home_page_name -> ie kiosk.home
    Pages.home_page_name = home_page_name;
    Pages.data.global.params = params;
    Pages.get_page(home_page_name).load();
};

Pages.reload = function() {
    // makes a cleanup ald reloads WHOLE page (opening Pages.home_page)
    Kiosk.Credit.stop().then(function() {location.reload();});
};

// Pages.add_data = function (data_app_name, data_name, key, val) {
//     /*
//     * data_app_name: might be 'global'
//     * */

//     if (Pages.data[data_app_name] === undefined)
//         Pages.data[data_app_name] = {};

//     if (Pages.data[data_app_name][data_name] === undefined)
//         Pages.data[data_app_name][data_name] = {};

//     Pages.data[data_app_name][data_name][key] = val;
// };

// Pages.clear_data = function (data_app_name, data_name, key) {
//     if (Pages.data[data_app_name] === undefined)
//         return;

//     if (data_name !== undefined && Pages.data[data_app_name] === undefined)
//         return;

//     if (key !== undefined && Pages.data[data_app_name][data_name] === undefined)
//         return;

//     if (key !== undefined)
//         delete Pages.data[data_app_name][data_name][key];
//     else if (data_name !== undefined)
//         delete Pages.data[data_app_name][data_name];
//     else {
//         if (data_app_name == 'global')
//             Pages.data[data_app_name] = {};
//         else
//             delete Pages.data[data_app_name];
//     }
// };

Pages.add_data = function(key, data_obj) {
    console.log('add_data: "%o" --> %o', key, data_obj);
    Pages.data.global[key] = data_obj;
};

Pages.clear_data = function(key) {
    console.log('clear_data: "%o"', key);
    if (Pages.data.global[key] === undefined)
        return;
    delete Pages.data.global[key];
};

function Page(app_name, name) {
    this.app_name = app_name;
    this.name = name;
    this.page_name = this.app_name + '.' + this.name;
    this.url = '/' + this.app_name + '/page/' + this.name + '/';
    this.html = null;   // jQuery object of full html loaded for the page
    this.nav = null;
    this.ajax_data = null;  // full received from the ajax call used to lead the page
    this._queue = [];

    if (Pages.data[this.app_name] === undefined)
        Pages.data[this.app_name] = {};

    this.load = function(ajax_data) {
        /*
        * ajax_data: dict to be sent as ajax argument when loading the page
        *
        * */

        // when going to homepage, reload so everything gets reset
        if (this.page_name == Pages.home_page) {
            Pages.reload();
        }


        if (this.on_page_load() == false)
            return;

        $.ajax({
            type: "POST",
            url: this.url,
            data: ajax_data? ajax_data : {},
            cache: false,
            crossDomain: false,
            dataType: 'json',
            context: this

        }).done(function(data) {
            var n;
            if (Pages.current() && (Pages.current().page_name != this.page_name)) {
                var old_page = Pages.current();
                for (n in old_page.nav) {
                    if (old_page.nav.hasOwnProperty(n))
                        old_page.disable_link(n);
                }
                if (old_page._queue.length) {
                    var el = old_page._queue[0];
                    old_page._queue = [];
                    if (el.timeout)
                        clearTimeout(el.timeout);
                }

                old_page.on_page_leave();
            }
            Pages.current(this);

            this.ajax_data = data;
            // Get the html string from the server (data.html), parse it,
            // get te content of the current selected .content and .footer
            // elements, and place them in the html. Store the parsed html with
            // the page object (this).
            // note the wrapping in a div element (class=__tmp__ for reference)
            // to make sure to have a root node
            this.html = $('<div class="__tmp__">' + $.trim(data.html) + '</div>');

            // clean page
            $('#header-step-1, #header-step-2, #header-step-3').removeClass('active');

            // update page elements
            $('body').attr('id', this.page_name);
            $('body').removeClass('page-ui-disabled');

            var content = this.html.find('.content.' + data.selected_content);
            if (content.length) {
                $('#content').empty();
                content.clone().contents().appendTo('#content');
            }
            $('#content').removeClass('ui-disabled'); //restore clean state, might have been used as a link

            var footer = this.html.find('.footer.' + data.selected_footer);
            if (footer.length) {
                footer.clone().contents().appendTo($('body>footer').empty());
            }

            var footer_step = this.html.find('.footer-step.' + data.selected_footer);
            if (footer_step.length) {
                $('#footer-step').empty();
                footer_step.clone().contents().appendTo('#footer-step');
            }

            var footer_error = this.html.find('.footer-error.' + data.selected_footer);
            if (footer_error.length) {
                $('#footer-error').empty();
                footer_error.clone().contents().appendTo('#footer-error');
            }

            var messages = this.html.find('#messages');
            if (messages.length) {
                $('#messages').empty();
                messages.clone().contents().appendTo('#messages');
            }

            var js = this.html.find('script');
            if (js.length)
                eval(js.text());

            // update page links
            this.nav = data.nav;
            for (n in this.nav) {
                if (this.nav.hasOwnProperty(n))
                    this.set_link(n, this.nav[n]);
            }

            // initialise specific page
            this.on_page_loaded(data);

        }).fail(function() {

        }).always(function() {
            // if (callback != null) {
            //     callback();
            // }
        });

    };
    this.on_page_load = function() {
        // might return false, in which case will interrupt the loading
        // procedure (ajax call is never made, see this.load() )
        console.log('Loading page "' + this.name + '" ...');
    };
    this.on_page_loaded = function(data) {
        // data: data (eventually) returned from ajax call to page
        console.log('Page "' + this.name + '" loaded.');
    };
    this.on_page_leave = function() {
        console.log('Just left page "' + this.name + '" ...');
    };
    this.goto_page = function (page, ajax_data) {
        /*
        * page: either a page_name of a page (ie kiosk.home) or
        *       the name of the link as listed in the Navi (ie: previous | next) or
        *       HOME
        *
        *       NB: if present, with the same name (shouldn't happen!)
        *           the Navi link-name takes precedence over the page_name
        * */

        if (page && page[0] == '!')
            page = page.slice(1);

        if (this.nav[page] !== undefined) {
            page = this.nav[page];
            if (page[0] == '!')
                page = page.slice(1);
        }

        Pages.get_page(page).load(ajax_data);
    };

    this._get_html_element_id_for_link = function(link_name) {
        if (link_name == 'previous')
            return 'footer-page-left-arrow';
        if (link_name == 'next')
            return 'footer-page-right-arrow';

        return link_name
    };
    this.get_html_element_id_for_link = function(link_name) {
        // override THIS method to add specific translations between
        // link name (as in .nav of server data) and html element id
        var ret = this._get_html_element_id_for_link(link_name);
        return ret;
    };
    this.set_link = function(link_name, linked_page_name, args) {

        //console.log('set_link(%o, %o)', link_name, linked_page_name);

        var disabled = false;
        if (linked_page_name && linked_page_name[0] == '!') {
            disabled = true;
            linked_page_name = linked_page_name.slice(1);
        }

        var el = $('#' + this.get_html_element_id_for_link(link_name));
        el.off('click');
        el.data('click-fun', function () {
            console.log("Go to Page -> " + linked_page_name);
            Pages.get_page(linked_page_name).load();
        });

        if (linked_page_name) {
            el.data('default-click-fun', function () {
                console.log("Go to Page -> " + linked_page_name);
                Pages.get_page(linked_page_name).load();
            });
            el.data('click-fun', el.data('default-click-fun'));
            if (!disabled)
                this.enable_link(link_name);
            else
                this.disable_link(link_name);
        }
        else {
            el.data('click-fun', function () {});
            this.disable_link(link_name);
        }
    };
    this.override_link_fun = function (link_name, f) {
        var el = $('#' + this.get_html_element_id_for_link(link_name));
        el.data('click-fun', f);
    };
    this.restore_link_fun = function (link_name) {
        var el = $('#' + this.get_html_element_id_for_link(link_name));
        el.data('click-fun', el.data('default-click-fun'));
    };
    this.enable_link = function(link_name) {
        var el = $('#' + this.get_html_element_id_for_link(link_name));
        el.removeClass('ui-disabled').off('click').click(el.data('click-fun'));
    };
    this.disable_link = function(link_name) {
        var el = $('#' + this.get_html_element_id_for_link(link_name));
        el.addClass('ui-disabled').off('click');
    };

    this.set_footer_message = function (msg, alarm) {
        /* msg: either a jQuery identifier of a message's div
        *        (ie  'footer-step.default')
        *       OR the jQuery instance of a messages's div
        *       OR a string which will be displayed exactly as is in the message.
        *        the string may begin with   'step:', 'error:' or 'alarm:' to specify
        *        the type of footer message (default is step)
        *
        *        NB: alarm does not remove 'the others' it simply overrides!!
        *
        *       if null: if it was in alarm, removes error,
        *           otherwise sets to '.footer-step.default'
        *
        *       alarm : if true,, and msg is none, only clears the alarm
        *           if msg != null alarm must be true if and only if msg is an alarm
        *           message!
        *
        *  NB: login in here is perverted... tries to make both old code and
        *  new one live together
        * */
        var footer_step = $('#footer-step');
        var footer_error = $('#footer-error');
        var footer_alarm = $('#footer-alarm');
        var div;

        if (!msg) {
            if (alarm) {
                footer_step.removeClass('alarm');
                footer_error.removeClass('alarm');
                footer_alarm.removeClass('alarm');
                return;
            }
            msg = '.footer-step.default';
        }

        if (typeof msg !== 'string') {
            div = msg;
        }

        else {
            div = this.html.find(msg);

            if (div.length) {
                div = div.first();
            }
            else {
                div =$('<div></div>');
                if (msg.slice(0, 6) == 'error:') {
                    if (alarm)
                        throw 'ERROR! Is this footer message an alarm or not??';
                    msg = msg.substring(6);
                    div.addClass('footer-error');

                }
                else if (msg.slice(0, 5) == 'step:') {
                    if (alarm)
                        throw 'ERROR! Is this footer message an alarm or not??';
                    msg = msg.substring(5);
                    div.addClass('footer-step');
                }
                else if (msg.slice(0, 6) == 'alarm:' || alarm) {
                    if (!alarm)
                        throw 'ERROR! Is this footer message an alarm or not??';

                    msg = msg.substring(6);
                    div.addClass('footer-alarm');
                    footer_step.addClass('alarm');
                    footer_error.addClass('alarm');
                    footer_alarm.addClass('alarm');
                }
                else {
                    div.addClass('footer-step');
                }

                div.html(msg);
            }
        }

        var footer_el;

        if (!alarm) {
            footer_step.empty();
            footer_error.empty();
            footer_step.hide();
            footer_error.hide();
            footer_el = div.hasClass('footer-step')? footer_step : footer_error;
        }
        else {
            footer_alarm.empty();
            footer_el = footer_alarm;
        }

        div.clone().contents().appendTo(footer_el);
        footer_el.show();
    };
    this._consume_queue = function () {
        var thisObj = this;

        if (!this._queue.length)
            return;

        var el = this._queue[0];
        if (el.completed) {
            this._queue.shift();
            return;
        }

        el.t0 = new Date();

        if (typeof el.queuable == 'function') {
            if (el.completed)
                return;
            el.completed = true;
            el.queuable();
            this._queue.shift();
            this._consume_queue();
        }
        else {
            el.close_message = function (mode) {
                /*
                * mode: ';' separated arguments, if any
                *       no_show: does not apply "visual" changes (hiding the message)
                *           useful when closing the message is the last action
                *           before moving to a new page (avoids flickering)
                *
                *       no_queue: does not interact with queue
                *           (no shift, no call to _consume_queue() )
                */
                var modes = typeof mode == 'string'? mode.split(';') : [];

                if (el.timeout)
                    clearTimeout(el.timeout);

                if (modes.indexOf('no_show') < 0) {
                    $('body').removeClass('page-ui-disabled');

                    if (el.queuable.hasClass('footer-step') || el.queuable.hasClass('footer-error')) {
                        thisObj.set_footer_message();
                    }
                    else {
                        el.queuable.hide();
                    }
                }

                if (modes.indexOf('no_queue') < 0) {
                    thisObj._queue.shift();
                    thisObj._consume_queue();
                }

            };

            if (el.disable_ui) {
                $('body').addClass('page-ui-disabled');
            }
            if (el.dt_max >= 0) {
                el.timeout = setTimeout(el.close_message, el.dt_max);
            }

            if (el.queuable.hasClass('footer-step') || el.queuable.hasClass('footer-error')) {
                thisObj.set_footer_message(el.queuable);
            }
            else {
                el.queuable.show();
            }
            el.queuable.off('click');

            if (el.click_dismiss) {
                el.queuable.click(el.close_message);
            }
        }
    };
    this.queue = function (queuable, dt_min, dt_max, click_dismiss, disable_ui) {
        /*
        * @param queuable: or any string that can be searched with jQuery
        *                of html element to show as message
        *                (ie "#the-evil-is-coming-error-message", ".message.I-am-drunk",
        *                #cows>.bluecow,) OR jQuery element to show,
        *                OR function to call (no need for other args)
        *                IMPORTANT: if the element has the class 'footer-step'
        *                or 'footer-error', than it is displayed in the footer,
        *                and hiding it will restore the "default" footer-step
        * @param dt_min: (minimum) time to show the message for
        *                < 0 for no minimum
        * @param dt_max: (maximum) time to show the message for
        *                < 0 for no maximum
        * @param click_dismiss: if true, clocking on the message will dismiss it
        *                (regardless of dt_min)
        * @param disable_ui: if true, while the message is visible, the ui is
        *                disabled (except message itself that MIGHT be clickable)
        *                NB: requires css support (class page-ui-disabled for body)!!
        *
        * @returns: the newly queued object (element + metadata)
        *           (so can be removed manually at will)
        * */
        var thisObj = this;

        if (typeof queuable == 'string') {
            queuable = $(queuable).first();
        }

        var el = {
            t0: null,
            timeout: null,
            close_message: null,
            completed: false,
            queuable: queuable,
            dt_min: dt_min,
            dt_max: dt_max,
            click_dismiss: click_dismiss,
            disable_ui: disable_ui
        };
        this._queue.push(el);

        if (this._queue.length >= 1)
            setTimeout(function () {
                thisObj._consume_queue();
            }, 69);

        return el;
    };
    this.dequeue = function (el, mode) {
        if (el.completed)
            return;

        if (!el.t0) {
            el.completed = true;
            return;
        }

        // here, queuable MUST be a message (jQuery element), functions get
        // executed completely when started!
        var dt = 0;
        if (el.dt_min >= 0)
            dt = el.dt_min - (new Date() - el.t0);

        var close_message = function () {
            el.close_message(mode);     // see el.close_message, assigner in this._consume_queue
        };

        if (dt <= 0) {
            close_message();
        }
        else {
            setTimeout(close_message, dt)
        }
    }

    this.notify_server = function (level, error_message, error_code) {
        /*
        * level: event | alarm | pre-alarm | .... not yet used, waiting for
        *   server-side to be ready
        * */
        $.ajax({
            type: "POST",
            url: this.ajax_data.api_url + 'alarms/',
            data: {
                error_code: error_code? error_code : 1000,
                error_message: error_message? error_message : 'unspecified message',
                device_name: 'UIPage'
            },
            cache: false,
            crossDomain: false,
            dataType: 'json',
            context: this,
            timeout: 33000
        }).done().fail().always();

    }
}








