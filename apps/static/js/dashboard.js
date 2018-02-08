'use strict';

// Module
window.Dashboard = {};

window.Dashboard.Controller = (function() {

    var _url_device_check_status_api = '';

    function init(url_device_check_status_api, autorepeat_interval) {
        _url_device_check_status_api = url_device_check_status_api;
        $('#refresh_button').on('click', function() {
            updateDashboard(0);
        });
        updateDashboard(autorepeat_interval);
    };

    function cleanup() {
        $('#machine-status').text('');
        $('#machine-detail').text('');
        $('#autocap-status').text('');
        $('#container-status').text('');
        $('#canlift-status').text('');
        $('#doors-status').text('');
        $('#pipes_table .pipe-flags span').attr('class', 'disabled');
    }

    function updateDashboard(autorepeat_interval) {

        $('#refresh_button span').addClass('spinning');

        $.ajax({
            type: 'GET',
            url: _url_device_check_status_api
        }).done(function(response_data) {

            try {
                var machine = response_data.data.machine;
                $('#machine-status').text(machine.device_status);
                //$('#machine-status').text(machine.annotations.device_status_display);
                $('#machine-status').attr("class", machine.annotations.machine_status_class);

                $('#machine-detail').text(machine.annotations.machine_status_display);
                $('#machine-detail').attr("class", machine.annotations.machine_status_class);

                $('#autocap-status').text(machine.annotations.autocap_status_display);
                $('#autocap-status').attr("class", machine.annotations.autocap_status_class);

                $('#container-status').text(machine.annotations.container_status_display);
                $('#container-status').attr("class", machine.annotations.container_status_class);

                $('#canlift-status').text(machine.annotations.canlift_status_display);
                $('#canlift-status').attr("class", machine.annotations.canlift_status_class);

                $('#doors-status').text(machine.annotations.doors_status_display);
                $('#doors-status').attr("class", machine.annotations.doors_status_class);

                $('#pipes_table .pipe-row').each(function(index, item) {

                    var row = $(item);
                    var index = row.data('pipe-index');
                    var flags = row.find('.pipe-flags');

                    // Update levels
                    var pipe = lookup(machine.annotations.pipes, "index", index);
                    var current_level = pipe.current_level;
                    var current_level_element = row.find('.current-level');
                    current_level_element.html(sprintf('%.2f', current_level));
                    var is_reserve = (current_level >= pipe.minimum_level);
                    if (is_reserve) {
                        current_level_element.removeClass('low');
                    }
                    else {
                        current_level_element.addClass('low');
                    }

                    // Update flags
                    var is_recirc = jQuery.inArray(index, machine.recirculation_status) >= 0;
                    var is_stirring = jQuery.inArray(index, machine.stirring_status) >= 0;
                    flags.find('.flag-reserve span').attr('class', is_reserve ? 'high' : 'low');
                    flags.find('.flag-recirc span').attr('class', is_recirc ? 'high' : 'low');
                    flags.find('.flag-stirring span').attr('class', is_stirring ? 'high' : 'low');
                })
            }
            catch (err) {
                console.log('error: %o', err);
                cleanup();
            }

        }).fail(function(jqXHR, textStatus, errorThrown) {
            console.log('ERROR: %o', jqXHR);
            console.log('textStatus: %o', textStatus);
            cleanup();

        }).always(function() {
            setTimeout(function() {$('#refresh_button span').removeClass('spinning')}, 200);
            if (autorepeat_interval > 0) {
                setTimeout(
                    function() { updateDashboard(autorepeat_interval); },
                    autorepeat_interval
                );
            }
        });

    };

    function onMachinePipeRefill(event) {
        var button = $(event.target);
        var buttonClass = button.attr('class');
        var pipeId = button.closest('.pipe-row').data('pipe-id');
        var modal = showModal(
            '#refill-modal', {
                width: 400,
                height: 210
            }, {
                pipeId: pipeId
            }
        );

        modal = $(modal);

        // Clean previous data, if any
        modal.find('h1 span.name, .pipe-table td:nth-child(2)').html('');
        modal.find('input.increment-quantity').val('');
        modal.find(".btn-save").off('click');

        // Load new data
        var url = modal.find('.detail-url').attr('href').replace('/0/', '/'+pipeId+'/');
        $.ajax({
            type: "GET",
            url: url,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function(result) {
                console.log('result: %o', result);
                modal.find('.modal-body .name').html(result.name);
                modal.find('.pipe-table td.index').html(result.index);
                modal.find('.pipe-table td.name').html(result.name);
                modal.find('.pipe-table td.device').html(result.device);
                modal.find('.pipe-table td.pigment_code').html(result.pigment_code);
                modal.find('.pipe-table td.current_level').html(result.current_level);
                modal.find('.pipe-table td.minimum_level').html(result.minimum_level);
                modal.find('.pipe-table td.maximum_level').html(result.maximum_level);
                modal.find('.modal-body .increment-quantity').focus();

                modal.find(".btn-save").on('click', function() {
                    onMachinePipeRefillSave(modal);
                });
            },
            error: function(jqXHR, textStatus) {
                var html = '<div class="system-error"><h2>ERRORE</h2><div class="description">' + jqXHR.responseText + '</div></div>';
                //setEditorBody(modal, html);
            },
            complete: function() {
                //setEditorStatusBar(modal, '');
            }
        });
    }

    function onMachinePipeRefillSave(modal) {

        var params = JSON.parse(modal.find('input[name="modal-params"]').val());
        var pipeId = params.pipeId;
        var url = modal.find('.detail-url').attr('href').replace('/0/', '/' + pipeId + '/');

        var index = modal.find('.pipe-table td.index').text();
        var name = modal.find('.pipe-table td.name').text();
        var device = modal.find('.pipe-table td.device').text();
        var current = parseInt(modal.find('.pipe-table td.current_level').text());
        var max = parseInt(modal.find('.pipe-table td.maximum_level').text());
        var increment = parseInt(modal.find('input.increment-quantity').val());

        var new_level = current + increment;
        if (new_level > max) {
            new_level = max;
        }
        else if (new_level < 0) {
            new_level = 0;
        }
        console.log('new_level: %o', new_level);

        $.ajax({
            type: "PUT",
            url: url,
            data: {
                index: index,
                name: name,
                device: device,
                current_level: new_level
            },
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function(result) {
                console.log('result: %o', result);
                modal.modal('hide');
            },
            error: function(jqXHR, textStatus) {
                alert(jqXHR.responseText);
            }
        });
    }

    function onMachinePipeCommand(event, channel, command) {
        var button = $(event.target);
        var buttonClass = button.attr('class');
        var pipeIndex = button.closest('.pipe-row').data('pipe-index');
        var cycle_command = (buttonClass == 'low');
        AlfaAdmin.CommandPoller.sendCommandToDevice(channel, command, [cycle_command, [pipeIndex]]);
    }

    return {
        init,
        onMachinePipeRefill,
        onMachinePipeCommand
    };

})();
