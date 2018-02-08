'use strict';

function spinner_on() {
    $('#spinner').css('visibility', 'visible');
}

function spinner_off() {
    $('#spinner').css('visibility', 'hidden');
}

function user_message(tag, message, timeout) {
    var id = 'alert-' + Date.now();
    var html = sprintf('<div id="%s" class="alert alert-%s"><button class="close" data-dismiss="alert">×</button>%s</div>',
        id, tag, message);
    $(html).appendTo("#messages");

    var alert = $('#' + id);
    if (timeout > 0) {
        setTimeout(function() {
            alert.fadeOut(500, function() {
                alert.remove();
            });
        }, timeout);
    }
}

function showModal(selector, options, params) {
    var modal = $(selector);
    modal.find('input[name="modal-params"]').val(JSON.stringify(params));
    modal.modal(options);
    return modal;
}

function getCookie(name) {
    var value = '; ' + document.cookie,
        parts = value.split('; ' + name + '=');
    if (parts.length == 2) return parts.pop().split(';').shift();
}

// Find an Object by attribute in an Array
// http://stackoverflow.com/questions/5579678/jquery-how-to-find-an-object-by-attribute-in-an-array#19154349
function lookup(array, prop, value) {
    for (var i = 0, len = array.length; i < len; i++)
        if (array[i] && array[i][prop] === value) return array[i];
}

// Module
window.AlfaAdmin = {};

var STATUS_PENDING = 0;
var STATUS_SUCCESS = 1;
var STATUS_FAILURE = 2;

// Poller initializations and functions
window.AlfaAdmin.CommandPoller = (function() {

    var _url_device_send_command_api = '';
    var _url_device_check_command_api = '';
    var _pending_command_id = 0;
    var _pending_command_details = null;

    function init(url_device_send_command_api, url_device_check_command_api, autorepeat_interval) {
        _url_device_send_command_api = url_device_send_command_api;
        _url_device_check_command_api = url_device_check_command_api;
        step(autorepeat_interval);
    };

    function notifyUser(tag, message) {
        user_message(tag, message, 5000);
    };

    function setResult(klass) {
        var element = $('#device_command_result');
        element.removeClass();
        element.addClass('result-' + klass);
    }

    function sendCommandToDevice(channel, command, params) {

        setResult('pending');

        _pending_command_details = {
            channel: channel,
            command: command,
            params: params
        };

        $.ajax({
            type: "POST",
            url: _url_device_send_command_api,
            data: JSON.stringify(_pending_command_details),
            dataType: 'json',
            headers: {"X-CSRFToken": getCookie('csrftoken')}
        }).done(function(response_data) {
            var msg_id = response_data.data;
            console.log('msg_id: %d', msg_id);
            _pending_command_id = msg_id;
            //notifyUser('info', sprintf('"%s" sent to "%s"', command, channel));
        }).fail(function(jqXHR, textStatus) {
            console.log('FAILURE: %o', jqXHR);
            try {
                var obj = JSON.parse(jqXHR.responseText);
                notifyUser('error', obj.message);
            }
            catch (err) {
                notifyUser('error', jqXHR.responseText);
            }
        });

    }

    function checkPendingCommand() {
        if (_pending_command_id > 0) {
            // Check pending command completion
            var url = _url_device_check_command_api.replace('/0/', sprintf('/%d/', _pending_command_id));
            $.ajax({
                type: 'GET',
                url: url,
                dataType: 'json'
            }).done(function(response_data, textStatus, jqXHR) {
                // Here we treat any error as "no response yet"
                try {
                    if (response_data.result == 'success') {
                        var status = response_data.data.status;
                        if (status == STATUS_SUCCESS) {
                            _pending_command_id = 0;
                            setResult('success');
                        }
                        else if (status == STATUS_FAILURE) {
                            setResult('failure');
                            notifyUser('error', sprintf('%s command "%s" (%d) failed with error code %d',
                                _pending_command_details.channel,
                                _pending_command_details.command,
                                _pending_command_id,
                                response_data.data.status_code
                            ));
                            _pending_command_id = 0;
                        }
                    }
                }
                catch (err) {
                }
            }).fail(function(jqXHR, textStatus, errorThrown) {
                console.log('ERROR: %o', jqXHR);
                console.log('textStatus: %o', textStatus);
            });
        }
    }

    function step(autorepeat_interval) {
        checkPendingCommand();

        // Call again ourself after specified interval
        if (autorepeat_interval > 0) {
            setTimeout(function() {
                step(autorepeat_interval);
            }, autorepeat_interval);
        }
    };

    return {
        init: init,
        step: step,
        sendCommandToDevice: sendCommandToDevice
    };

})();


$(document).ready(function($) {
    $("#device_command_result").on('click', function() {
        console.log('click');
        AlfaAdmin.CommandPoller.step(0);
    });
});
