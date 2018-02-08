'use strict';

// Module
window.Dashboard = {};

window.Dashboard.MachineStatusMgr = (function() {

    /**
     * MachineStatusMgr initialization
     * @param data
     */
    function init(cfg) {

        var interval = cfg.interval || 0;

        function update_pipe(p) {
            var html = '';

            /* update current level */
            $('#current-level-' + p.id)
                .html(p.current_level);

            /* assemble html for the pipe flags field */
            if (p.is_reserve) {
                html += '<span class="flag reserve-hi"></span>';
            }
            else {
                html += '<span class="flag reserve-lo"></span>';
            }

            if (p.is_recirc) {
                html += '<span class="flag recirc-hi"></span>';
            }
            else {
                html += '<span class="flag recirc-lo"></span>';
            }

            if (p.is_stirring) {
                html += '<span class="flag stirring-hi"></span>';
            }
            else {
                html += '<span class="flag stirring-lo"></span>';
            }

            $('#pipe-flags-' + p.id)
                .html(html);
        }

        function offline_controller() {
            $('#machine-status')
                .html(sprintf('<h4>OFFLINE</h4>'))
                .addClass('critical')
                .removeClass('service')
                .removeClass('normal')
                .removeClass('idle')
            ;

            $('#machine-detail')
                .html('<h6>Unreachable</h6>')
            ;
            $('#autocap-status')
                .html(sprintf('<h4>OFFLINE</h4>'))
                .addClass('critical')
                .removeClass('service')
                .removeClass('normal')
                .removeClass('idle')
            ;

            if (cfg.is_colortester) {
                $('#canlift-status')
                    .html(sprintf('<h4>OFFLINE</h4>'))
                    .addClass('critical')
                    .removeClass('service')
                    .removeClass('normal')
                    .removeClass('idle')
                ;
                $('#doors-status')
                    .html(sprintf('<h4>OFFLINE</h4>'))
                    .addClass('critical')
                    .removeClass('service')
                    .removeClass('normal')
                    .removeClass('idle')
                ;
            }
            else if (cfg.is_colorlab) {
                $('#container-status')
                    .html(sprintf('<h4>OFFLINE</h4>'))
                    .addClass('critical')
                    .removeClass('service')
                    .removeClass('normal')
                    .removeClass('idle')
                ;
            }
        }

        /* http://stackoverflow.com/questions/15313418/javascript-assert */
        function assert(condition, message) {
            if (!condition) {
                throw new Error(message || 'Assertion failed');
            }
        }

        /**
         * This code must be kept in synch with Dashboard devices change form. This sucks :-(
         * @param statusData
         */
        function update_controller(statusData) {

            assert(statusData);
            console.log('updating controller...');

            var status_level = statusData.status_level;
            var cycle_step = statusData.cycle_step;
            var autocap_status = statusData.autocap_status;
            var canlift_status = statusData.canlift_status;
            var doors_status = statusData.doors_status;
            var container_status = statusData.container_presence;
            var error_code = statusData.error_code;
            var error_message = statusData.error_message;

            /* machine status */
            $('#machine-status').html(
                (status_level === 'ALARM' ||
                 status_level === 'DIAGNOSTIC') && error_code !== 0 ?
                    sprintf('<h4>%s (%d)</h4>', status_level, error_code) :
                    sprintf('<h4>%s</h4>', status_level)
            );

            /* machine detail */
            if (status_level === 'POWER_OFF' ||
                status_level === 'INIT'  ||
                status_level === 'IDLE') {
                $('#machine-detail')
                    .html('<h6>Unreachable</h6>');
            }
            else if (status_level === 'ALARM' ||
                     status_level === 'DIAGNOSTIC') {
                $('#machine-detail')
                    .html(sprintf('<h6>%s</h6>', error_message));
            }
            else {
                $('#machine-detail')
                    .html(sprintf('<h6>%s</h6>', cycle_step));
            }

            /* colorization via CSS classes */
            if (status_level === 'DIAGNOSTIC' ||
                status_level === 'RESET' ||
                status_level === 'INIT'  ||
                status_level === 'IDLE') {

                $('#machine-status')
                    .removeClass('critical')
                    .removeClass('normal')
                    .removeClass('idle')
                    .addClass('service');
            }
            else if (status_level === 'ALARM' ||
                status_level === 'POWER_OFF') {

                $('#machine-status')
                    .removeClass('service')
                    .removeClass('normal')
                    .removeClass('idle')
                    .addClass('critical');
            }
            else if (status_level === 'STANDBY' ||
                status_level === 'DISPENSING') {

                $('#machine-status')
                    .removeClass('idle')
                    .removeClass('critical')
                    .removeClass('service')
                    .addClass('normal');
            }

            /* autocap status */
            if (autocap_status) {
                $('#autocap-status')
                    .html(sprintf('<h4>OPEN</h4>'))
                    .removeClass('critical')
                    .addClass('service')
                    .removeClass('normal')
                    .removeClass('idle');
            }
            else {
                $('#autocap-status')
                    .html(sprintf('<h4>CLOSED</h4>'))
                    .removeClass('critical')
                    .removeClass('service')
                    .addClass('normal')
                    .removeClass('idle');
            }

            /**
             *  ColorTester specific
             */
            if (cfg.is_colortester) {
                if (canlift_status) {
                    $('#canlift-status')
                        .html(sprintf('<h4>OPEN</h4>'))
                        .removeClass('critical')
                        .addClass('service')
                        .removeClass('normal')
                        .removeClass('idle');
                }
                else {
                    $('#canlift-status')
                        .html(sprintf('<h4>CLOSED</h4>'))
                        .removeClass('critical')
                        .removeClass('service')
                        .addClass('normal')
                        .removeClass('idle');
                }

                if (doors_status) {
                    $('#doors-status')
                        .html(sprintf('<h4>OPEN</h4>'))
                        .removeClass('critical')
                        .addClass('service')
                        .removeClass('normal')
                        .removeClass('idle');
                }
                else {
                    $('#doors-status')
                        .html(sprintf('<h4>CLOSED</h4>'))
                        .removeClass('critical')
                        .removeClass('service')
                        .addClass('normal')
                        .removeClass('idle');
                }
            }

            /**
             *  ColorLab specific
             */
            else if (cfg.is_colorlab) {
                if (container_status) {
                    $('#container-status')
                        .html(sprintf('<h4>PRESENT</h4>'))
                        .removeClass('critical')
                        .removeClass('service')
                        .addClass('normal')
                        .removeClass('idle')
                    ;
                }
                else {
                    $('#container-status')
                        .html(sprintf('<h4>ABSENT</h4>'))
                        .removeClass('critical')
                        .addClass('service')
                        .removeClass('normal')
                        .removeClass('idle');
                }
            }
        }

        // this little guy here, makes up a perfect endless synchronized loop
        function update(obj) {
            var machine = obj.machine;
            var pipes = obj.pipes;

            /* update all pipes */
            _.each(pipes, update_pipe);

            /* assemble html for the machine control widget */
            update_controller(machine);
        }
        
        function offline() {
            /* assemble html for the machine control widget */
            offline_controller();
        }

        // this little guy here, makes up a perfect endless synchronized loop
        var launcher = function () {
            if (interval > 0) {
                setTimeout(function () {
                    $.ajax({
                        type: 'GET',
                        url: cfg.urls.machine_status,
                    }).then(update, offline)
                        .always(launcher);
                }, interval);
            }
        };

        // start the loop
        launcher();
        console.log('start local data mgr');
    }

    return {
        init: init,
    };
})();

window.Dashboard.LocalDataMgr = (function() {

    /**
     * MachineStatusMgr initialization
     * @param data
     */
    function init(cfg) {

        var interval = cfg.interval || 0;

        function update(obj) {

            function update_jobs(jobs) {
                _.each(jobs, function (job, i) {
                    $('#job-id-' + i)
                        .html(job.id)
                    ;

                    $('#job-date_modified-' + i)
                        .html(job.date_modified)
                    ;

                    $('#job-recipe-' + i)
                        .html(job.recipe)
                    ;

                    $('#job-type-' + i)
                        .html(job.type)
                    ;

                    $('#job-status-' + i)
                        .html(job.status)
                    ;

                    $('#job-package-' + i)
                        .html(job.package)
                    ;

                    $('#job-size-' + i)
                        .html(job.size)
                    ;
                });
            }

            function update_alarms(alarms) {
                _.each(alarms, function (alarm, i) {
                    $('#alarm-id-' + i)
                        .html(alarm.id)
                    ;

                    $('#alarm-date_modified-' + i)
                        .html(alarm.date_modified)
                    ;

                    $('#alarm-device_name-' + i)
                        .html(alarm.device_name)
                    ;

                    $('#alarm-error_code-' + i)
                        .html(alarm.error_code)
                    ;

                    $('#alarm-error_message-' + i)
                        .html(alarm.error_message)
                    ;
                });
            }

            function update_events(events) {
                _.each(events, function (event, i) {
                    $('#event-id-' + i)
                        .html(event.id)
                    ;
                
                    $('#event-date_modified-' + i)
                        .html(event.date_modified)
                    ;

                    $('#event-type-' + i)
                        .html(event.type)
                    ;

                    $('#event-message-' + i)
                        .html(event.message)
                    ;
                });
            }

            update_jobs(obj.jobs);
            update_alarms(obj.alarms);
            update_events(obj.events);
        }

        // this little guy here, makes up a perfect endless synchronized loop
        var launcher = function () {
            if (interval > 0) {
                setTimeout(function () {
                    $.ajax({
                        type: 'GET',
                        url: cfg.urls.machine_localdata,
                    }).then(update)
                        .always(launcher);
                }, interval);
            }
        };

        // start the loop
        launcher();
        console.log('started machine status mgr');
    }

    return {
        init: init,
    };
})();

window.Dashboard.Controller = (function() {

    function action(el, url) {
        $(document).on('click', '#' + el, function () {
            $('#shutter').
                css('display', 'block');

            console.log( sprintf('Invoking %s ...', url));
            $.ajax({
                'method': 'POST',
                'url': url
            }).always(function () {
                console.log('...completed!');
                $('#shutter')
                    .css('display', 'none');
            });
        });
    } /* action() */

    return {
        action: action
    };
})();


