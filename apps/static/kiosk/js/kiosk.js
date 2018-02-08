'use strict';

// Module
window.Kiosk = {};

// Kiosk Timeout manager
window.Kiosk.Timeout = (function() {
    var count = 0,
        enabled = true;

    var init = function(callback, limit) {

        if (0 < limit)
            setInterval(function() {
                if (enabled) {
                    //console.log('tick...');
                    ++ count;

                    if (count >= limit) {
                        count = 0;
                        callback();
                    }
                }
            }, 1000);
    };

    var enable = function() {
        enabled = true;
    };

    var disable = function() {
        enabled = false;
    };

    var clear = function() {
        count = 0;
    };

    return {
        init: init,
        clear: clear,
        enable: enable,
        disable: disable
    };
})();

// Kiosk Shutter manager
window.Kiosk.Shutter = (function() {

    var interval = 1000; // eventually overridden with called-supplied value
    var init = function(url, callback, _interval) {

        interval = typeof _interval !== 'undefined' ? _interval : interval;

        // this little guy here, makes up a perfect endless synchronized loop
        var launcher = function () {
            if (interval > 0) {
                setTimeout(function () {
                    $.ajax({
                        type: 'GET',
                        url: url
                    }).then(function(msg) {
                        callback(msg);
                    }).always(launcher);
                }, interval);
            }
        };

        // start the loop
        launcher();
    };

    return {
        init: init
    };
})();

// Kiosk Credit manager
window.Kiosk.Credit = (function() {

    var _credit = 0,
        _granted = false,
        _commands = null,
        _hdr = 'changeme' ;

    var init = function(hdr, interval, commands) {

        // this is used to display the localized 'Credit' string
        _hdr = hdr;

        _commands = commands;

        // this little guy here, makes up a perfect endless synchronized loop
        var launcher = function () {
            if (interval > 0) {
                setTimeout(function () {
                    $.ajax({
                        type: 'GET',
                        url: commands.credit
                    }).then(function(data) {

                        /* update credit information */
                        _credit = data.credit;
                        _granted = data.granted;

                        if (_credit) {

                            $('#credit > h6')
                                .html(_hdr)
                            ;
                            $('#credit > div')
                                .html(_credit)
                            ;
                        }
                        else {

                            $('#credit > h6')
                                .html('&nbsp;')
                            ;
                            $('#credit > div')
                                .html('&nbsp;')
                            ;
                        }
                    }).always(launcher);
                }, interval);
            }
        };

        // start the loop
        launcher();
    };

    function charge() {
        var ret = $.ajax({
            type: 'POST',
            url: _commands.charge,
            async: false
        });
        console.log('Charged');

        // returning is useless atm, but compatible with
        // old asynchronous behaviour, which allowed for use
        // of (chained) .then functions
        return ret;
    }

    function collect() {
        return $.ajax({
            type: 'POST',
            url: _commands.collect
        }).then(function() {
            console.log('Transaction completed. Thanks!');
        });
    }

    function refund() {
        return $.ajax({
            type: 'POST',
            url: _commands.refund
        }).then(function() {
            console.log('Printed refund label');
        });
    }

    function credit() {
        return _credit;
    }

    function granted() {
        return _granted;
    }

    function start() {
        return $.ajax({
            type: 'POST',
            url: _commands.start
        }).then(function() {
            console.log('Payment device started');
        });
    }

    function stop() {
        // made synchronous (see charge(), above, for more details)
        var ret = $.ajax({
            type: 'POST',
            url: _commands.stop,
            async: false
        });
        console.log('Payment device stopped');

        return ret;
    }

    return {
        init: init,
        credit: credit,
        granted: granted,
        charge: charge,
        collect: collect,
        refund: refund,
        start: start,
        stop: stop
    };

})();

// Kiosk status manager
window.Kiosk.Status = (function() {
    var interval = 1000,
        status_node,
        indicator_node,
        status_info_node,
        close_button,
        dismiss_button,
        diagnostics_button,
        language_selector;

    var params = null;

    // Initialization
    // @param {integer} interval - Check status interval
    var init = function(obj) {
        // initialised here so import can be relocated even before html
        status_node = $('#status'),
        indicator_node = $('#header-status'),
        status_info_node = $('#status-info'),
        close_button = $('#status-close'),
        dismiss_button = $('#status-dismiss'),
        diagnostics_button = $('#status-diagnostics'),
        language_selector = $('.language-selector');

        params = obj;

        if (params.interval > 0) {

            // this little guy here, makes up a perfect endless synchronized loop.
            var launcher = function () {
                setTimeout(function () {
                    $.ajax({
                        type: 'GET',
                        url: params.urls.status
                    }).then(
                        function (data) {

                            function show_out_of_order() {
                                // hide all header step spans
                                _.each([1, 2, 3], function (id) {
                                    $('#header-step-' + id)
                                        .addClass('hidden');
                                });

                                Pages.current().set_footer_message('alarm:' + data.message, true);

                                $('#ooo')
                                    .removeClass('hidden');
                            }

                            function restore_normal_condition() {
                                $('#ooo')
                                    .addClass('hidden');

                                Pages.current().set_footer_message(null, true);

                                // un-hide all header step spans
                                _.each([1, 2, 3], function (id) {
                                    $('#header-step-' + id)
                                        .removeClass('hidden');
                                });
                            }

                            if (data.code !== null) {
                                show_out_of_order();

                                status_info_node.html(sprintf(
                                    '<h3>Error %(code)d: [%(device)s] %(message)s</h3>', data));

                                indicator_node.addClass('warning');
                            } else {
                                restore_normal_condition();

                                status_info_node.html('');
                                indicator_node.removeClass('alert warning');
                            }
                        })
                        .always(launcher);  //setTimeout...
                }, interval);
            };

            // Launching status updates
            console.log('Launched poller...');
            launcher();
        }

        diagnostics_button
            .off()
            .click(function() {
                window.location.href = 'diagnostics/';
            });

        indicator_node
            .off()
            .click(_open);

        language_selector.find('.flag')
            .off()
            .click(function(event) {
                event.preventDefault();
                var target = $(event.target);
                $.ajax({
                    type: 'POST',
                    url: target.attr('href')
                }).then(function (response) {
                    //language_selector.find('.flag').removeClass('active');
                    //target.addClass('active');
                    //window.location.replace("/");
                    window.location.reload(true);
                });
            });
    };

    // Open the error info node
    var _open = function() {
        status_node.removeClass('hidden');

        close_button
            .off()
            .click(_close);

        dismiss_button
            .off()
            .click(_dismiss);
    };

    // Close the error info node
    var _close = function() {
        status_node.addClass('hidden');
    };

    // Dismiss the error from the info node
    var _dismiss = function() {
        _close();
        $.ajax('/kiosk/j/status/dismiss/');
        status_info_node.html('');
    };

    return {
        init: init
    };
})();


// Color list widget
window.Kiosk.Colors = (function() {

    var duration  = 1000, // Scroll duration (ms)
        query  = '',
        page   = 0;   // for Pagination


    function resetClickHandlers() {
        disarmClickHandlers();
        armClickHandlers();
    }

    function disarmClickHandlers() {

        $('#color_list-up')
            .off('click')
        ;

        $('#color_list-down')
            .off('click')
        ;

        $('#color_list')
            .off('click')
        ;

        window.Kiosk.Keyboard.disableClickHandlers();
    }

    function armClickHandlers() {

        $('#color_list-up')
            .off()
            .click(function() {

                /* turn handlers off, perform animation, then re-arm 'em */
                disarmClickHandlers();

                scrollUp()
                    .then(function() {
                        console.log('animation done');
                        resetClickHandlers();
                    });
            });

        $('#color_list-down')
            .off()
            .click(function() {

                /* turn handlers off, perform animation, then re-arm 'em */
                disarmClickHandlers();

                scrollDown()
                    .then(function(){
                        console.log('animation done');
                        resetClickHandlers();
                    });
            });

        $('#color_list')
            .off()
            .on('click', '.color_list-item', onClickColor); /* cannot use .click here, we go with .on */

        window.Kiosk.Keyboard.enableClickHandlers();
    }

    // Initialization
    function init() {

        // feed color_list with some color to start with
        updateColors();
    }

    // Update the list of colors
    // @param {string} data - HTML replacement
    // @param (number} dir  - direction (0 = first load, -1 scroll up, 1 scroll down}
    function _updateHtmlColors(data, dir) {

        var dfd = new $.Deferred();

        /* pad items list */
        var orig_length = data.recipes.length;
        while (data.recipes.length < 7) {
            data.recipes.push({
                placeholder: true
            });
        }

        /* let's go functional! */
        var items = _.map( data.recipes, function(obj) {

            var res;

            if (obj.placeholder) {
                return '<li class="color_list-placeholder"></li>';
            }

            res = sprintf(
                '<li class="color_list-item" data-recipe-id="%(id)s" data-description="%(description)s">' +
                '<div style="background-color: %(color)s;" class="color_preview"></div>', obj
            );

            if (obj.description)
                res += sprintf(
                    '<div class="color-code ueberscript">%(code)s</div>' +
                    '<div class="color-description">%(description)s</div></li>', obj);

            else
                res += sprintf('<div class="color-code">%(code)s</div></li>', obj);

            return res;
        });

        var previous = $('#color_list-items').html(),
            html = _.reduce( items, function( acc, item) {
                return acc + item;
            });

        if (!html)
            html = '';

        if (dir === 'up') {

            $('#color_list-items')
                .html(html + previous)
                .scrollTop(335)
                .animate({
                    scrollTop: 0,
                }, duration, function() {
                    $(this)
                        .scrollTop(0)
                        .html(html);

                    /* completed */
                    dfd.resolve();
                });

        }
        else if (dir === 'down') {

            $('#color_list-items')
                .html(previous + html)
                .animate({
                    scrollTop: 340
                }, duration, function() {
                    $(this)
                        .scrollTop(0)
                        .html(html);

                    /* completed */
                    dfd.resolve();
                });
        }
        else {
            /* update color list: if query yielded no items, color list is cleared */
            $('#color_list-items')
                .html(html);

            /* completed */
            dfd.resolve();
        }

        /* if only one item is shown, select it automatically */
        var color_items = $('#color_list li');
        if (orig_length === 1) {
            selectColor($(color_items[0]));
        }
        else {
            selectColor(null);
        }

        return dfd;
    }

    // Update the colors using the search string
    // @param {string} query - Color search query
    function updateColors (q) {
        page = 0;  /* new search */
        query = q || '';

        $.get('/kiosk/j/colors/', {
            p: page,
            q: query
        }, function(data) {
            _updateHtmlColors(data, null)
                .then(function() {
                    resetClickHandlers();
                    console.log('Color list populated');
                });
        });
    }

    // Scroll the color list up (promise)
    function scrollUp () {

        var dfd = new $.Deferred();

        if (0 < page) {
            -- page;

            $.get('/kiosk/j/colors/', {
                p: page,
                q: query
            }, function (data) {
                _updateHtmlColors(data, 'up')
                    .then(function() {
                        dfd.resolve();
                    });
            });
        } else dfd.resolve();
        /* completed */

        return dfd.promise();
    }

    // Scroll the color list down (promise)
    function scrollDown () {

        var dfd = new $.Deferred();

        $.get('/kiosk/j/colors/', {
            p: ++ page,
            q: query
        }, function(data) {
            if (0 < data.recipes.length) {
                _updateHtmlColors(data, 'down')
                    .then(function() {
                        dfd.resolve();
                    });
            } else {
                -- page; /* bottom reached, restore previous page number */
                dfd.resolve();
            }
        });

        return dfd.promise();
    }

    // Select a color
    // @param {Event} event - jQuery event
    var onClickColor = function(event) {
        Kiosk.Keyboard.write($(this).children('.color-code').text());
        selectColor($(this));
    };

    var selectColor = function(color_list_item) {
        if (color_list_item) {

            // Save selected color properties
            var recipe_id = color_list_item.attr('data-recipe-id');
            var description = color_list_item.attr('data-description');
            var css_color = color_list_item.children('.color_preview').css('background-color');

            $('#selected-color')
                .text(color_list_item.children('.color-code').text())
                .css('background-color', css_color)
                .attr('data-recipe-id', recipe_id)
                .attr('data-description', description)
            ;

            // Enable buttons to move on
            $('.keyboard-command[data-command="confirm"]').removeClass('ui-disabled');
            // $('#footer-page-right-arrow').removeClass('ui-disabled');
            Pages.current().enable_link('next');
        }
        else {
            // Reset selected color properties
            $('#selected-color')
                .text('')
                .css('background-color', 'rgb(204,204,204)')
                .attr('data-recipe-id', 0)
                .attr('data-description', '')
            ;

            // Disable buttons to move on
            $('.keyboard-command[data-command="confirm"]').addClass('ui-disabled');
            // $('#footer-page-right-arrow').addClass('ui-disabled');
            Pages.current().disable_link('next');
        }

        // Reflect selected color in UI
        updateTriangle();
    };

    var updateTriangle = function() {
        var color = $('#selected-color').css('background-color');
        $('#triangle').css('border-top-color', color);
        $('#color_list, #left-bar').css('border-right-color', color);
        $('#digit_color, #right-bar').css('border-left-color', color);
        $('#triangle').attr('data-recipe-id', $('#selected-color').attr('data-recipe-id'));

        try {
            var n = $('#tty').val().length;
            if (n > 0) {
                $('#clear-button').addClass('enabled');
            }
            else {
                $('#clear-button').removeClass('enabled');
            }
        }
        catch(e) {
        }
    };

    return {
        init: init,
        updateColors: updateColors,
        updateTriangle: updateTriangle
    };
})();


// Keyboard widget
window.Kiosk.Keyboard = (function() {
    var tty = null,
        updateCallback = function(colorCode) {};

    // Initialization
    // @param {function} callback - Callback function on input update
    var init = function() {

        tty = $('#tty');

        tty
            .off()
            .on('input', colorUpdated)
        ;
    };

    var disableClickHandlers = function() {
        $('#keyboard li')
            .off()
        ;

        $('#keyboard li[data-command]')
            .off()
        ;

        $('.color_list-item')
            .off()
        ;
    };

    var enableClickHandlers = function() {
        $('#keyboard li')
            .off()
            .click(keyPressed)
        ;

        $('#keyboard li[data-command]')
            .off()
            .click(commandPressed)
        ;

        $('.color_list-item')
            .off()
            .click(colorChoose)
        ;
    };

    // A keyboard key is pressed
    // @param {Event} event - jQuery event
    var keyPressed = function(event) {
        /* skip keyboard-command elements */
        if (event.target.className.indexOf('keyboard-command') >= 0)
            return;

        tty.val(tty.val() + $(this).text());
        colorUpdated();
    };

    // On color updated
    var colorUpdated = function() {
        Kiosk.Colors.updateColors(tty.val());
    };

    var clear = function() {
        write('');
        colorUpdated();
    };

    // A keyboard command key is pressed
    // @param {Event} event - jQuery event
    var commandPressed = function(event) {

        switch ($(this).attr('data-command')) {
            case 'delete':
                keyDelete(event);
                break;

            case 'confirm':
                keyConfirm(event);
                break;
        }
    };

    // Delete the last key
    // @param {Event} event - jQuery event
    var keyDelete = function(event) {
        var str = tty.val();
        tty.val(str.substring(0, str.length - 1));
        colorUpdated();
    };

    // Confirm the color
    // @param {Event} event - jQuery event
    var keyConfirm = function(event) {
        Pages.get_page('kiosk.confirm_selection').load();
    };

    // Choose a color from the list
    // @param {Event} event - jQuery event
    var colorChoose = function(event) {
        //TODO: da implementare
        console.log('colorChoose');
    };

    // Put a string in to the input field
    // @param {string} input - Input text
    var write = function(input) {
        tty.val(input);
    };

    return {
        init: init,
        write: write,
        clear: clear,

        enableClickHandlers: enableClickHandlers,
        disableClickHandlers: disableClickHandlers
    };
})();

// Kiosk dispensation page
window.Kiosk.Dispensation = (function() {
    var interval = 1000,
        last_progress = 0,
        dispensation_command_issued = false,
        params = null;

    // @param {string} pickedColor - Color
    var init = function(recipe_id, obj) {
        params = obj;
        startDispensation(recipe_id);
    };

    // Run the dispensation command, avoid multiple dispensations
    // @param {string} color - Color to dispense
    var startDispensation = function(recipe_id) {

        if (dispensation_command_issued)
            return;

        last_progress = 0;
        dispensation_command_issued = true;

        var url = sprintf('/machine/j/dispensation/dispense/%s/', recipe_id);

        $.ajax({
            url: url,
            type: 'POST',
            data: {
                dispensation_notes: Pages.data.global.dispensation_notes?
                    JSON.stringify(Pages.data.global.dispensation_notes) : ''
            }
        }).then(startChecks, function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus);
        });
    };

    // Start the progress check loop
    var startChecks = function(data) {

        var is_done = false;
        var grace_time = false;

        // this little guy here, makes up a perfect endless synchronized loop
        var launcher = function () {

            if (interval > 0) {
                setTimeout(function () {

                    if (data.job_id !== null) {
                        var url = sprintf('/machine/j/dispensation/status/%s/', data.job_id);

                        $.ajax({
                            url: url,
                            type: 'GET'
                        }).then( function(data) {

                            // status consts
                            var STATUS_COMPLETED = 3,
                                STATUS_ABORTED = 4,
                                STATUS_DONE = 5;

                            console.log(JSON.stringify(data));

                            // update progress only if current value is greater than previously recorded one.
                            var progress = data.progress;
                            if (progress < last_progress)
                                progress = last_progress;
                            else
                                last_progress = progress;

                            $('#page_4 #progress').attr('value', progress);

                            /* drawing progress */
                            var height = Math.round((240.0 / 100.0) * progress);
                            var top = 390 - height;
                            $('#imgLevel').css('height', height);
                            $('#imgLevel').css('top', top);
                            $('#imgTopLevel').css('top', 380 - 2 * height);

                            if (data.status === STATUS_ABORTED) {
                                var error_message = 'Dispensation failed';
                                if (data.reason.length > 0) {
                                    error_message += ': ' + data.reason;
                                }

                                // FIXME: better looking error message
                                alert(error_message);

                                window.location.reload();
                            }

                            else if (data.status === STATUS_COMPLETED) {
                                if (! is_done) {
                                    is_done = true;
                                    Pages.get_page('kiosk.progress_bar')
                                        .dispensation_completed();

                                    grace_time = false;
                                    setTimeout(function() {
                                        grace_time = true;
                                    }, 3000);  /* label grace time (= 3 secs) */
                                }

                                /* Wait till the user picks the label */
                                if (! params.use_labeler || data.picked_label && grace_time) {

                                    Pages.get_page('kiosk.dispensed').load();

                                    data.status = STATUS_DONE;

                                    /* Re-Arm dispensation start */
                                    dispensation_command_issued = false;
                                }
                            }

                            /* re-arm status update request? */
                            if (data.status !== STATUS_DONE) {
                                launcher();
                            }
                        });
                    }
                }, interval);
            }
        };

        // start the loop
        launcher();
    };

    return {
        init: init
    };
})();
