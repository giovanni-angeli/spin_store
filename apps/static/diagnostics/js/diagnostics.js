'use strict';

// Module
window.Diagnostics = {

    // this callback is used in the synoptic SVG inclusion template
    pigmentClick: function(index) {
        console.log( sprintf('Received click on pigment %d', index));
        var el = sprintf('#pigment%d', index);

        var rgb;

        try {
            rgb = d3.select(el)
                .style('fill');

            // yields a triple of floats :-)
            rgb = _.map(rgb
                .substring(4, rgb.length - 1)
                .replace(/ /g, '')
                .split(','), parseFloat)
            ;

            var tint = [
                rgb[0] + (255 - rgb[0]) * 0.5,
                rgb[1] + (255 - rgb[1]) * 0.5,
                rgb[2] + (255 - rgb[2]) * 0.5
            ];

            d3.select(el)
                .style('fill', sprintf('rgb(%d, %d, %d)',
                    tint[0], tint[1], tint[2]))
            ;
        }
        catch (e) {
            console.warn('No pigment!');
        }

        window.Diagnostics.Pages.circuit(index);
    }

};

// Diagnostics Timeout manager
window.Diagnostics.Timeout = (function() {
    var count = 0,
        enabled = true,
        limit = 0;

    var init = function(callback, orig_limit) {

        limit = orig_limit;
        if (0 < limit)
            setInterval(function() {
                if (enabled) {
                    console.log('tick...');
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

    var set_limit = function(new_limit) {
        limit = new_limit;
    };

    return {
        init: init,
        clear: clear,
        enable: enable,
        disable: disable,
        set_limit: set_limit
    };
})();

// Keyboard widget
window.Diagnostics.Keyboard = (function() {
    var tty = null,
        keyConfirm = null,

        init = function (confirmCallback) {
            tty = $('#tty');

            $('#keyboard li')
                .off()
                .on('click', function (event) {
                    var text = tty.val() + $(this).text();
                    updateText(text);
                });

            $('#keyboard li[data-command]')
                .off()
                .on('click', function (event) {
                    switch ($(this).attr('data-command')) {
                        case 'delete':
                            keyDelete(event);
                            break;
                        case 'confirm':
                            keyConfirm(event);
                            break;
                    }
                });

            keyConfirm = confirmCallback || function (evt) {
                    console.log('Empty callback!');
            };
        },

        updateText = function (input) {
            tty.val(input);

            if (0 < input.length) {
                $('.keyboard-command[data-command="confirm"]')
                    .removeClass('ui-disabled');
                $('#footer-page-right-arrow')
                    .removeClass('ui-disabled');
            }
            else {
                $('.keyboard-command[data-command="confirm"]')
                    .addClass('ui-disabled');
                $('#footer-page-right-arrow')
                    .addClass('ui-disabled');
            }
        },

        keyDelete = function (event) {
            var str = tty.val();
            updateText(str.substring(0, str.length - 1));
        };

    return {
        init: init,
        text: function() {
            return tty.val();
        },
        clear: function() {
            updateText('');
        }
    };
})();

// Diagnostics page initializations and functions
window.Diagnostics.Pages = (function() {

    var AUTH_LEVEL_OPERATOR = 1,
        AUTH_LEVEL_TECHNICIAN = 2;

    function nop()
    {}

    var params = null,
        config = null,
        auth   = null,
        updateStatus = nop,
        failedStatus = nop,
        machine_query  = true,
        updateLocked = false,
        machine_status = null;

    var init = function(obj) {
        params = obj;
        config = JSON.parse(params.config);

        // this little guy here, makes up a perfect endless synchronized loop. Changing pages,
        // we just switch the success and fail callbacks, while keeping the status poll going.
        var launcher = function() {
            setTimeout(function () {
                $.ajax({
                    type: 'POST',
                    url: params.urls.status
                }).then(updateStatus, failedStatus)
                    .always(launcher);
            }, params.millis);
        };

        // Launching status updates
        console.log('Launched poller...');
        launcher();
    };

    var exit = function() {

        // if machine is not responding bypass avoid blocking exit view altogether
        if (machine_status !== null) {
            window.location = params.urls.exit;
        }
        else {
            window.location = params.urls.kiosk;
        }
    };

    var force_cold_reset = function() {

        $.ajax({
            type: 'POST',
            url: params.urls.reset
        });
    };

    // Load a page and paste it in the content
    // @param {string} page - Page name, like "page_2".
    var _load_page = function(page, callback) {
        $('#content')
            .load('/kiosk/j/' + page + '/', function() {

                $('body')
                    .attr('id', page);

                if (typeof callback === 'function') {
                    callback();
                }

                $.get('/kiosk/j/' + page + '/footer/', function(data) {
                    console.log('Loaded footer for ' + page);
                    Pages.current().set_footer_message('step:' + data);
                });
            });
    };

    function disableButton(el) {
        $('#' + el)
            .attr('disabled', 'true')
            .removeClass('btn-enabled')
            .addClass('btn-disabled');
    }

    function enableButton(el) {
        $('#' + el)
            .removeAttr('disabled')
            .removeClass('btn-disabled')
            .addClass('btn-enabled');
    }

    var goPageCarriage = function() {

        function enableReset() {
            enableButton('reset');
        }
        function disableReset() {
            disableButton('reset');
        }

        function enableWithdrawal() {
            enableButton('withdrawal1');
            enableButton('withdrawal2');
            enableButton('withdrawal3');
            enableButton('withdrawal4');
        }
        function disableWithdrawal() {
            disableButton('withdrawal1');
            disableButton('withdrawal2');
            disableButton('withdrawal3');
            disableButton('withdrawal4');
        }

        function enableFilling() {
            enableButton('filling');
        }
        function disableFilling() {
            disableButton('filling');
        }

        function enableCapping() {
            enableButton('capping1');
            enableButton('capping2');
        }
        function disableCapping() {
            disableButton('capping1');
            disableButton('capping2');
        }

        function enableDischarge() {
            enableButton('positive');
            enableButton('negative');
        }
        function disableDischarge() {
            disableButton('positive');
            disableButton('negative');
        }

        function enableHoming() {
            enableButton('home');
        }

        function disableHoming() {
            disableButton('home');
        }

        function enableCPC() {
            enableButton('load1');
            enableButton('load2');
            enableButton('load3');
            enableButton('load4');
        }

        function enableCover() {
            enableButton('cap1');
            enableButton('cap2');
        }

        function enableCanLifter() {
            enableButton('cl_extend');
            enableButton('cl_retract');
        }

        function enableAutocap() {
            enableButton('ac_open');
            enableButton('ac_close');
        }

        function disableCanLifter() {
            disableButton('cl_extend');
            disableButton('cl_retract');
        }

        function disableAutocap() {
            disableButton('ac_open');
            disableButton('ac_close');
        }

        function disableCommands() {
            disableButton('load1');
            disableButton('load2');
            disableButton('load3');
            disableButton('load4');

            disableButton('cap1');
            disableButton('cap2');

            disableAutocap();
            disableCanLifter();
        }

        function stateCommon() {
            /* RESET always on */
            enableReset();

            /* CPC and COVER acts always on */
            enableCPC();
            enableCover();

            /* AUTOCAP always on */
            enableAutocap();

            /* CAN LIFTER on iff AUTOCAP is open */
            if (machine_status.autocap_status)
                enableCanLifter();
            else
                disableCanLifter();
        }

        function stateReadyPosition() {
            stateCommon();

            /* Withdrawal motion only */
            enableWithdrawal();
            disableFilling();
            disableCapping();
            disableDischarge();
            disableHoming();
        }

        function stateWithdrawalPosition() {
            stateCommon();

            /* Filling motion only */
            disableWithdrawal();
            enableFilling();
            disableCapping();
            disableDischarge();
            disableHoming();
        }

        function stateFillingPosition() {
            stateCommon();

            /* Capping motion only */
            disableWithdrawal();
            disableFilling();
            enableCapping();
            disableDischarge();
            disableHoming();
        }

        function stateCappingPosition() {
            stateCommon();

            /* discharge motion only */
            disableWithdrawal();
            disableFilling();
            disableCapping();
            enableDischarge();
            disableHoming();
        }

        function stateDischargePosition() {

            stateCommon();

            /* homing motion only */
            disableWithdrawal();
            disableFilling();
            disableCapping();
            disableDischarge();
            enableHoming();
        }

        function disableMotions() {
            disableWithdrawal();
            disableFilling();
            disableCapping();
            disableDischarge();
            disableHoming();
        }

        function lockUpdate() {
            updateLocked = true;
        }

        function unlockUpdate() {
            updateLocked = false;
        }

        function updatePage() {

            if (machine_status !== null) {

                var pathetic_messages = {
                    'ALARM': 'youwontseeme',
                    'STANDBY': 'Idle',
                    'RESET': 'In progress',
                    'DISPENSING': 'In progress',
                    'DIAGNOSTIC': 'Maintenance mode'
                };

                if (machine_status.status_level === 'ALARM') {
                    var status_line = sprintf('%s (%d)',
                        machine_status.status_level,
                        machine_status.error_code);

                    $('#status-level')
                        .html(status_line);

                    $('#err-code')
                        .html(machine_status.error_message)
                    ;
                }
                else if (machine_status.status_level === 'RESET' ||
                         machine_status.status_level === 'DISPENSING') {

                    $('#status-level')
                        .html(machine_status.status_level)
                    ;

                    $('#err-code')
                        .html(machine_status.cycle_step)
                    ;
                }
                else {
                    $('#status-level')
                        .html(machine_status.status_level);

                    $('#err-code')
                        .html(pathetic_messages[machine_status.status_level]);
                }

                /** clamp position */
                if (updateLocked || machine_status.status_level === 'RESET') {
                    disableReset();
                    disableCommands();
                    disableMotions();
                }

                /* unlocked and in STANDBY or DIAGNOSTIC */
                else if (machine_status.clamp_position === 'POS0') {
                    stateReadyPosition();
                }
                else if (machine_status.clamp_position === 'POS1' ||
                         machine_status.clamp_position === 'POS2' ||
                         machine_status.clamp_position === 'POS3' ||
                         machine_status.clamp_position === 'POS4') {
                    stateWithdrawalPosition();
                }
                else if (machine_status.clamp_position === 'POS5') {
                    stateFillingPosition();
                }
                else if (machine_status.clamp_position === 'POS6' ||
                         machine_status.clamp_position === 'POS7') {
                    stateCappingPosition();
                }
                else if (machine_status.clamp_position === 'POSF' ||
                         machine_status.clamp_position === 'POSG') {
                    stateDischargePosition();
                }
                else {
                    console.log(
                        sprintf('Unsupported clamp position: %s', machine_status.clamp_position));
                }
            }

            else if (! machine_query) {
                $('#status-level')
                    .html('Device not ready');

                $('#err-code')
                    .html('Could not retrieve machine status');
            }
        }

        _load_page('page_carriage', function () {

            updateStatus = function(statusData) {

                machine_status = statusData;
                machine_query  = false;
                updatePage();
            };

            failedStatus = function () {
                machine_status = null;
                machine_query  = false;
                updatePage();
            };

            var withdrawalStation = null,
                cappingStation    = null,
                dischargeType     = null;

            /* RESET */
            $('#reset')
                .off()
                .on('click', function (e) {

                    e.preventDefault();
                    console.log('RESET...');

                    disableReset();
                    disableCommands();
                    disableMotions();
                    lockUpdate();

                    $.ajax({
                        type: 'POST',
                        url: params.urls.reset
                    }).always(function() {
                        unlockUpdate();
                        console.log('...request sent!');
                    });
                });

            /* WITHDRAWAL MOTION 1..4 */
            _.each([1, 2, 3, 4], function(ndx) {
                $('#withdrawal' + ndx)
                    .off()
                    .on('click', function (e) {
                        e.preventDefault();
                        console.log( sprintf('HOME -> WITHDRAWAL%d...', ndx));

                        withdrawalStation = ndx - 1;

                        disableReset();
                        disableCommands();
                        disableMotions();
                        lockUpdate();

                        $.ajax({
                            type: 'POST',
                            url: params.urls.enter_diagnostic
                        }).then(function () {
                            $.ajax({
                                type: 'POST',
                                url: params.urls.pos_withdrawal,
                                data: {
                                    station: withdrawalStation
                                }
                            }).always(function () {
                                unlockUpdate();
                                console.log('...request sent!');
                            });
                        });
                    });
                });

            /* EXECUTE WITHDRAWAL 1..4 */
            _.each([1, 2, 3, 4], function(ndx) {
                var button_name = sprintf('load%d', ndx);
                $('#' + button_name)
                    .off()
                    .on('click', function(e) {
                        e.preventDefault();
                        console.log( sprintf('WITHDRAWAL%d...', ndx));

                        disableReset();
                        disableCommands();
                        disableMotions();
                        lockUpdate();

                        $.ajax({
                            type: 'POST',
                            url: params.urls.enter_diagnostic,
                        }).then(function () {
                            $.ajax({
                                type: 'POST',
                                url: params.urls.act_withdrawal,
                                data: {
                                    station: ndx - 1
                                }
                            }).always(function() {
                                unlockUpdate();
                                console.log('...request sent!');
                            });
                        });
                    });
            });

            /* FILLING MOTION */
            $('#filling')
                .off()
                .on('click', function (e) {
                    e.preventDefault();
                    console.log( sprintf(' -> FILLING...'));

                    disableReset();
                    disableCommands();
                    disableMotions();
                    lockUpdate();

                    $.ajax({
                        type: 'POST',
                        url: params.urls.enter_diagnostic
                    }).then(function () {
                        $.ajax({
                            type: 'POST',
                            url: params.urls.pos_filling,
                        }).always(function () {
                            unlockUpdate();
                            console.log('...request sent!');
                        });
                    });
                });

            /* CAPPING MOTION 1..2 */
            _.each([1, 2], function(ndx) {
                $('#capping' + ndx)
                    .off()
                    .on('click', function (e) {
                        e.preventDefault();
                        console.log( sprintf('FILLING -> CAPPING%d...', ndx));

                        disableReset();
                        disableCommands();
                        disableMotions();
                        lockUpdate();

                        cappingStation = ndx - 1;

                        $.ajax({
                            type: 'POST',
                            url: params.urls.enter_diagnostic
                        }).then(function () {
                            $.ajax({
                                type: 'POST',
                                url: params.urls.pos_capping,
                                data: {
                                    station: cappingStation
                                }
                            }).always(function () {
                                unlockUpdate();
                                console.log('...request sent!');
                            });
                        });
                    });
                });

            /* EXECUTE CAPPING 1..2 */
            _.each([1, 2], function(ndx) {
                var button_name = sprintf('cap%d', ndx);
                $('#' + button_name)
                    .off()
                    .on('click', function(e) {
                        e.preventDefault();
                        console.log('CAPPING%d...', ndx);

                        disableReset();
                        disableCommands();
                        disableMotions();
                        lockUpdate();

                        $.ajax({
                            type: 'POST',
                            url: params.urls.enter_diagnostic,
                        }).then(function () {
                            $.ajax({
                                type: 'POST',
                                url: params.urls.act_cap,
                                data: {
                                    station: ndx - 1
                                }
                            }).always(function() {
                                unlockUpdate();
                                console.log('...request sent!!');
                            });
                        });
                    });
            });

            /* POSITIVE DISCHARGE POSITION */
            $('#positive')
                .off()
                .on('click', function (e) {
                    e.preventDefault();
                    console.log('CAPPING%d -> POSITIVE...', cappingStation);

                    disableReset();
                    disableCommands();
                    disableMotions();
                    lockUpdate();

                    dischargeType = 1; /* positive */

                    $.ajax({
                        type: 'POST',
                        url: params.urls.enter_diagnostic
                    }).then(function () {
                        $.ajax({
                            type: 'POST',
                            url: params.urls.pos_discharge,
                            data: {
                                station: cappingStation,
                                discharge: dischargeType
                            }
                        }).always(function () {
                            unlockUpdate();
                            console.log('...request sent!');
                        });
                    });
                });

            /* NEGATIVE DISCHARGE POSITION */
            $('#negative')
                .off()
                .on('click', function (e) {
                    e.preventDefault();
                    console.log('CAPPING%d -> NEGATIVE...', cappingStation);

                    disableReset();
                    disableCommands();
                    disableMotions();
                    lockUpdate();

                    dischargeType = 0; /* negative */

                    $.ajax({
                        type: 'POST',
                        url: params.urls.enter_diagnostic
                    }).then(function () {
                        $.ajax({
                            type: 'POST',
                            url: params.urls.pos_discharge,
                            data: {
                                station: cappingStation,
                                discharge: dischargeType
                            }
                        }).always(function () {
                            unlockUpdate();
                            console.log('...request sent!');
                        });
                    });
                });

            /* HOMING POSITION */
            $('#home')
                .off()
                .on('click', function (e) {
                    e.preventDefault();
                    console.log('%s -> HOMING...', dischargeType === 0 ? 'NEGATIVE' : 'POSITIVE');

                    disableReset();
                    disableCommands();
                    disableMotions();
                    lockUpdate();

                    $.ajax({
                        type: 'POST',
                        url: params.urls.enter_diagnostic
                    }).then(function () {
                        $.ajax({
                            type: 'POST',
                            url: params.urls.pos_home,
                            data: {
                                discharge: dischargeType
                            }
                        }).always(function () {
                            unlockUpdate();
                            console.log('...request sent!');
                        });
                    });
                });

            /* AUTOCAP */
            $('#ac_open')
                .off()
                .on('click', function(e) {
                    e.preventDefault();
                    console.log('AUTOCAP OPEN...');

                    disableReset();
                    disableCommands();
                    disableMotions();
                    lockUpdate();

                    $.ajax({
                        type: 'POST',
                        url : params.urls.enter_diagnostic
                    }).then(function() {
                        $.ajax({
                            type: 'POST',
                            url : params.urls.autocap_open
                        });
                    }).always(function() {
                        unlockUpdate();
                        console.log('...request sent!');
                    });
                });

            $('#ac_close')
                .off()
                .on('click', function(e) {
                    e.preventDefault();
                    console.log('AUTOCAP CLOSE...');

                    disableReset();
                    disableCommands();
                    disableMotions();
                    lockUpdate();

                    $.ajax({
                        type: 'POST',
                        url : params.urls.enter_diagnostic
                    }).then(function() {
                        $.ajax({
                            type: 'POST',
                            url : params.urls.autocap_close
                        });
                    }).always(function() {
                        unlockUpdate();
                        console.log('...request sent!');
                    });
                });

            /* CAN LIFTER */
            $('#cl_extend')
                .off()
                .on('click', function(e) {
                    e.preventDefault();
                    console.log('CAN LIFTER EXTEND...');

                    disableReset();
                    disableCommands();
                    disableMotions();
                    lockUpdate();

                    $.ajax({
                        type: 'POST',
                        url : params.urls.enter_diagnostic
                    }).then(function() {
                        $.ajax({
                            type: 'POST',
                            url : params.urls.canlifter_extend
                        });
                    }).always(function() {
                        unlockUpdate();
                        console.log('...request sent!');
                    });
                });

            $('#cl_retract')
                .off()
                .on('click', function(e) {
                    e.preventDefault();
                    console.log('CAN LIFTER RETRACT...');

                    disableReset();
                    disableCommands();
                    disableMotions();
                    lockUpdate();

                    $.ajax({
                        type: 'POST',
                        url : params.urls.enter_diagnostic
                    }).then(function() {
                        $.ajax({
                            type: 'POST',
                            url : params.urls.canlifter_retract
                        });
                    }).always(function() {
                        unlockUpdate();
                        console.log('...request sent!');
                    });
                });

            /* NAVIGATION */
            $('#footer-page-left-arrow')
                .removeClass('ui-disabled')
                .off()
                .on('click', function (e) {
                    e.preventDefault();
                    goPageMain(auth);
                });

            $('#footer-page-right-arrow')
                .addClass('ui-disabled')
                .off()
            ;
        });
    };

    function goPageCircuit(index) {

        var recirculationData = null,
            stirringData = null;

        // helpers
        function updateInput(value) {
            $('#keyboard-value')
                .val(value);
        }

        function clearInput() {
            updateInput('');
        }

        function hideLevels() {
            $('#levels')
                .hide();
        }

        function showLevels() {
            $('#levels')
                .show();
        }

        function setMessage(msg) {
            $('.main-overlay h3')
                .html(msg)
                .show()
            ;
        }

        function hideStopButton() {
            $('#stop-button')
                .hide();
        }

        function showStopButton(callback) {
            $('#stop-button')
                .show()
                .off()
                .on('click', callback);
        }

        function hideStartButton() {
            $('#start-button')
                .hide();
        }

        function showStartButton(callback) {
            $('#start-button')
                .show()
                .off()
                .on('click', callback);
        }

        function hideKeyboard() {
            $('.main-overlay h3')
                .hide();

            $('#keyboard')
                .hide();
        }

        function blankKeyboard() {
            $('#keyboard-value')
                .val('');
        }

        function setKeyboard(value) {
            $('#keyboard-value')
                .val(value);
        }

        function showKeyboard() {

            blankKeyboard();
            $('#keyboard')
                .show();
        }

        function showIndicator() {
            $('#running-indicator')
                .show();
        }

        function hideIndicator() {
            $('#running-indicator')
                .hide();
        }

        // derived from _load_page
        var _load_circuit = function(index, callback) {
            $('#content')
                .load( sprintf('/kiosk/j/circuit/%d', index), function() {

                    $('body')
                        .attr('id', sprintf('circuit-%d', index));

                    if (typeof callback === 'function') {
                        callback();
                    }

                    $.get(sprintf('/kiosk/j/circuit/%d/footer/', index), function(data) {
                        console.log('Loaded footer for circuit ' + index);
                        Pages.current().set_footer_message('step:' + data);
                    });
            });
        };

        _load_circuit(index, function() {

            $(document)
                .off()
                .on('reload-levels', function() {
                    $.ajax({
                        type: 'POST',
                        url: params.urls.circuit_levels[index]
                    }).then(function (data) {

                        var current_volume = data.current_volume;
                        var maximum_volume = data.maximum_volume;
                        var reserve_volume = data.reserve_volume;
                        var minimum_volume = data.minimum_volume;

                        var y_scale = d3.scale
                                .linear()
                                .range([380, 20])
                                .domain([0.00, maximum_volume])
                            ;

                        // mown the flowerbed
                        $('#beaker-overlay')
                            .html('');

                        var svg = d3.select('#beaker-overlay')
                                .append('svg')
                                .attr('width', 400)
                                .attr('height', 400)
                                .append('g')
                            ;

                        svg.append('g')
                            .append('rect')
                            .attr('x', 0)
                            .attr('y', 0)
                            .attr('width', 220)
                            .attr('height', y_scale(current_volume))
                            .style('fill', 'whitesmoke')
                        ;

                        svg.append('g')
                            .append('line')
                            .attr('x1', 0)
                            .attr('y1', y_scale(reserve_volume))
                            .attr('x2', 220)
                            .attr('y2', y_scale(reserve_volume))
                            .attr('stroke', 'blue')
                        ;

                        svg.append('g')
                            .append('line')
                            .attr('x1', 0)
                            .attr('y1', y_scale(minimum_volume))
                            .attr('x2', 220)
                            .attr('y2', y_scale(minimum_volume))
                            .attr('stroke', 'red')
                        ;

                        svg.append('g')
                            .append('line')
                            .attr('x1', 0)
                            .attr('y1', y_scale(current_volume))
                            .attr('x2', 220)
                            .attr('y2', y_scale(current_volume))
                            .attr('stroke', 'black')
                        ;

                        // matte background
                        svg.append('g')
                            .append('rect')
                            .attr('x', 0)
                            .attr('y', 0)
                            .attr('width', 220)
                            .attr('height', 400)
                            .style('fill', 'whitesmoke')
                            .style('opacity', 0.4)
                            .attr('ry', 20)
                        ;

                        svg.append('g')
                            .attr('transform', 'translate(210, 0)')
                            .attr('class', 'axis')
                            .call(d3.svg.axis()
                                .scale(y_scale)
                                .orient('left')
                                .ticks(20)
                                .tickSize(10, 2)
                                .tickFormat(function (d) {
                                    return d.toLocaleString( params.language, {
                                        minimumFractionDigits: 2
                                    });
                                }))
                        ;

                        $('#current-volume')
                            .html(current_volume.toLocaleString( params.language, {
                                minimumFractionDigits: 2
                            }))
                            .css('color', minimum_volume <= current_volume ? '#2B2B2A' : 'darkred')
                        ;

                        $('#maximum-volume')
                            .html(maximum_volume.toLocaleString( params.language, {
                                minimumFractionDigits: 2
                            }));

                        $('#reserve-volume')
                            .html(reserve_volume.toLocaleString( params.language, {
                                minimumFractionDigits: 2
                            }));

                        $('#minimum-volume')
                            .html(minimum_volume.toLocaleString( params.language, {
                                minimumFractionDigits: 2
                            }));
                    });
                });


            // fire it once to draw the beaker
            $(document)
                .trigger('reload-levels')
            ;

            var current_action = null;
            var update_pending = false;
            function switchAction(action) {
                hideLevels();
                hideKeyboard();
                hideStopButton();
                hideStartButton();
                showIndicator();
                current_action = action;
                update_pending = true;
            }

            updateStatus = function(statusData) {

                machine_status = statusData;
                machine_query = false;

                // do it just once...
                if (! update_pending)
                    return ;
                update_pending = false;

                hideIndicator();

                if (current_action === 'purge') {

                    showIndicator();

                    $.ajax({
                        type: 'POST',
                        url: params.urls.circuit_purge_volume[index]
                    }).then(function (data) {

                        hideIndicator();
                        setMessage('Enter the amount of pigment to purge<br />[cc] and press \'Ok\'.');

                        showKeyboard();
                        setKeyboard(data.purge_volume.toString());
                    });
                }
                else if (current_action === 'refill') {
                    setMessage('Enter the amount of pigment to refill<br />[cc] and press \'Ok\'.');
                    showKeyboard();
                }

                else if (current_action === 'recirculation') {
                    if (-1 !== statusData.recirculation_status.indexOf(index)) {
                        setMessage('Recirculation activated. Press \'Stop\' to interrupt.');
                        showStopButton(function() {

                            hideStopButton();
                            showIndicator();

                            $.ajax({
                                type: 'POST',
                                url: params.urls.enter_diagnostic,
                            }).then(function () {
                                $.ajax({
                                    type: 'POST',
                                    url: params.urls.circuit_recirculation_control[index],
                                    data: {
                                        control: false
                                    }
                                }).then(function () {
                                    console.log('Recirculation stopped');

                                    update_pending = true;
                                });
                            });
                        });
                    }
                    else {
                        hideStopButton();
                        showIndicator();

                        console.log("........circuit_settings");
                        $.ajax({
                            type: 'POST',
                            url: params.urls.circuit_settings[index]
                        }).then(function (data) {
                            recirculationData = {
                                n_step_cycle: data.pump_settings.n_steps_stroke,
                                speed_cycle: data.circuit_settings.recirculation_speed,
                                n_cycles: 65535,  // (= infinity)
                                pause: data.circuit_settings.recirculation_pause
                            };
                            console.log("........pump data");
                            console.log(data);

                            hideIndicator();
                            setMessage('Enter recirculation speed [rpm] and press \'Ok\'.');
                            showKeyboard();
                            setKeyboard(recirculationData.speed_cycle.toString());
                        });
                    }
                }
                else if (current_action === 'stirring') {
                    if (-1 !== statusData.stirring_status.indexOf(index)) {
                        setMessage('Stirring activated. Press \'Stop\' to interrupt.');
                        showStopButton(function() {
                            hideStopButton();
                            showIndicator();

                            $.ajax({
                                type: 'POST',
                                url: params.urls.enter_diagnostic,
                            }).then(function () {
                                $.ajax({
                                    type: 'POST',
                                    url: params.urls.circuit_stirring_control[index],
                                    data: {
                                        control: false
                                    }
                                }).always(function () {
                                    update_pending = true;
                                });
                            });
                        });
                    }
                    else {
                        setMessage('Press \'Start\' to activate stirring.');
                        showStartButton(function() {
                            hideStartButton();
                            showIndicator();

                            $.ajax({
                                type: 'POST',
                                url: params.urls.enter_diagnostic,
                            }).then(function () {
                                $.ajax({
                                    type: 'POST',
                                    url: params.urls.circuit_stirring_control[index],
                                    data: {
                                        control: true
                                    }
                                }).always(function () {
                                    update_pending = true;
                                });
                            });
                        });
                    }
                }
            };

            failedStatus = function() {
                machine_query = false;
                machine_status = null;
            };

            $('#keyboard li')
                .off()
                .on('click', function (event) {
                    var ch = $(this).text(),
                        old_value, new_value;

                    if (ch === '-') {
                        old_value = $('#keyboard-value').val();
                        new_value = - old_value;
                        updateInput(new_value);
                        return;
                    }

                    old_value = $('#keyboard-value').val();
                    new_value = old_value + ch;
                    updateInput(new_value);
                });

            var confirm = nop;
            $('#keyboard li[data-command]')
                .off()
                .on('click', function (event) {
                    switch ($(this).attr('data-command')) {
                        case 'cancel':
                            hideKeyboard();
                            showLevels();
                            current_action = null;
                            break;

                        case 'clear':
                            clearInput();
                            return;

                        case 'confirm':
                            confirm();
                            break;
                    }
                });

            $('#refill-proceed')
                .off()
                .bind('click', function () {

                    switchAction('refill');
                    var validator = new FormValidator(
                        'data-entry-form', [{
                            name: 'keyboard-value',
                            display: 'value',
                            rules: 'required|decimal'
                        }],
                        function (errors) {
                            if (0 < errors.length) {
                                blankKeyboard();
                                return;
                            }

                            var value = $('#keyboard-value').val();
                            console.log('Accepted value: %s', value);

                            hideKeyboard();
                            showIndicator();

                            $.ajax({
                                type: 'POST',
                                url: params.urls.circuit_refill[index],
                                data: {
                                    qty: parseFloat(value)
                                }
                            }).always(function (res) {
                                hideIndicator();
                                showLevels();

                                $(document)
                                    .trigger('reload-levels')
                                ;
                            });
                        });

                    confirm = function () {
                        validator._validateForm();
                    };
                });


            // Purge
            $('#purge-proceed')
                .off()
                .bind('click', function () {

                    switchAction('purge');
                    var validator = new FormValidator(
                        'data-entry-form', [{
                            name: 'keyboard-value',
                            display: 'value',
                            rules: 'required|decimal|greater_than[0]'
                        }],
                        function (errors) {
                            if (0 < errors.length) {
                                blankKeyboard();
                                return;
                            }

                            var value = $('#keyboard-value').val();
                            console.log('Accepted value: %s', value);

                            hideKeyboard();
                            showIndicator();

                            $.ajax({
                                type: 'POST',
                                url: params.urls.enter_diagnostic,
                            }).then(function () {
                                return $.ajax({
                                    type: 'POST',
                                    url: params.urls.circuit_manual_purge[index],
                                    data: {
                                        qty: parseFloat(value)
                                    }
                                }).then(function() {
                                    return $.ajax({
                                        type: 'POST',
                                        url: params.urls.circuit_refill[index],
                                        data: {
                                            qty: - parseFloat(value)
                                        }
                                    });
                                }).always(function () {
                                    hideIndicator();
                                    showLevels();

                                    $(document)
                                        .trigger('reload-levels')
                                    ;
                                });
                            });
                        });

                    confirm = function () {
                        validator._validateForm();
                    };
                });

            // Recirculation
            $('#recirculation-proceed')
                .off()
                .bind('click', function () {

                    switchAction('recirculation');
                    var validator = new FormValidator(
                        'data-entry-form', [{
                            name: 'keyboard-value',
                            display: 'value',
                            rules: 'required|decimal|greater_than[0]'
                        }],
                        function (errors) {
                            if (0 < errors.length) {
                                blankKeyboard();
                                return;
                            }

                            var value = $('#keyboard-value').val();
                            console.log('Accepted value: %s', value);

                            // update speed
                            recirculationData.speed_cycle = value;

                            hideKeyboard();
                            showIndicator();

                            $.ajax({
                                type: 'POST',
                                url: params.urls.enter_diagnostic,
                            }).then(function () {
                                console.log("........recirculation_setup");
                                console.log("........recitculation data");
                                console.log(recirculationData);
                                $.ajax({
                                    type: 'POST',
                                    url: params.urls.circuit_recirculation_setup[index],
                                    data: recirculationData
                                }).then(function () {
                                    console.log("........recirculation_control");
                                    console.log("........recitculation data");
                                    console.log(recirculationData);
                                    $.ajax({
                                        type: 'POST',
                                        url: params.urls.circuit_recirculation_control[index],
                                        data: {
                                            control: true
                                        }
                                    }).then(function () {
                                        console.log('Recirculation started');
                                        update_pending = true;
                                    });
                                });
                            });
                        });

                    confirm = function () {
                        validator._validateForm();
                    };
                });

            // Stirring
            $('#stirring-proceed')
                .off()
                .bind('click', function () {

                    switchAction('stirring');
                    $('#stirring-start')
                        .off()
                        .on('click', function (e) {
                            e.preventDefault();

                            $.ajax({
                                type: 'POST',
                                url: params.urls.enter_diagnostic
                            }).then(function () {
                                $.ajax({
                                    type: 'POST',
                                    url: params.urls.positive
                                }).then(function () {
                                    console.log('positive sent');
                                });
                            });
                        });

                });


            // set up navigation
            $('#footer-page-left-arrow')
                .removeClass('ui-disabled')
                .off()
                .on('click', function (e) {
                    e.preventDefault();
                    goPageMain(auth);
                });

            $('#footer-page-right-arrow')
                .addClass('ui-disabled')
                .off()
            ;
        });
    }

    var goPageMain = function(_auth) {

        auth = _auth;

        function updatePage() {

            function markNormal(el) {
                d3.select('#' + el)
                    .style('fill', 'green');
            }

            function markWarning(el) {
                d3.select('#' + el)
                    .style('fill', 'orange');
            }

            function markUnavailable(el) {
                d3.select('#' + el)
                    .style('fill', 'gray');
            }

            function markDisabled(el) {
                d3.select('#' + el)
                    .style('fill', 'black');
            }

            function markCritical(el) {
                d3.select('#' + el)
                    .style('fill', 'darkred');
            }

            function showActivityIndicator(el) {
                d3.select('#' + el)
                    .style('display', 'inline');
            }

            function hideActivityIndicator(el) {
                d3.select('#' + el)
                    .style('display', 'none');
            }

            function markNone(el) {
                d3.select('#' + el)
                    .style('fill', 'black');
            }

            if (machine_status !== null) {

                var pathetic_messages = {
                    'ALARM': 'youwontseeme',
                    'STANDBY': 'Idle',
                    'RESET': 'In progress',
                    'DISPENSING': 'In progress',
                    'DIAGNOSTIC': 'Maintenance mode'
                };

                if (machine_status.status_level === 'ALARM') {
                    var status_line = sprintf('%s (%d)',
                        machine_status.status_level,
                        machine_status.error_code);

                    $('#status-level')
                        .html(status_line);

                    $('#err-code')
                        .html(machine_status.error_message)
                    ;
                }
                else if (machine_status.status_level === 'RESET' ||
                         machine_status.status_level === 'DISPENSING') {

                    $('#status-level')
                        .html(machine_status.status_level)
                    ;

                    $('#err-code')
                        .html(machine_status.cycle_step)
                    ;
                }
                else {
                    $('#status-level')
                        .html(machine_status.status_level);

                    $('#err-code')
                        .html(pathetic_messages[machine_status.status_level]);
                }

                if (machine_status.status_level === 'STANDBY' &&
                    0 === machine_status.level_alerts.length) {
                    enableButton('autopurge');
                }
                else {
                    disableButton('autopurge');
                }

                // update pigments
                if( Object.prototype.toString.call( machine_status.color_reserve ) === '[object Array]' ) {
                    _.each(_.range(14), function (index) {
                        var el = sprintf('status%d', index);

                        if (0 <= machine_status.level_alerts.indexOf(index))
                            markCritical(el);

                        else {
                            if (0 <= config.machine.pipes.indexOf(index)) {
                                if (-1 !== machine_status.color_reserve.indexOf(index))
                                    markWarning(el);
                                else
                                    markNormal(el);
                            }
                        }
                    });
                }
                else {
                    _.each(_.range(14), function (index) {
                        if (0 <= config.machine.pipes.indexOf(index)) {
                            var el = sprintf('status%d', index);
                            markUnavailable(el);
                        }
                    });
                }

                // update recirculation indicators
                _.each(_.range(14), function(index) {
                    if (0 <= config.machine.pipes.indexOf(index)) {
                        var el = sprintf('recirculation-%d', index);
                        if (-1 !== machine_status.recirculation_status.indexOf(index))
                            showActivityIndicator(el);
                        else
                            hideActivityIndicator(el);
                    }
                });

                // update stirring indicators
                _.each(_.range(14), function(index) {
                    if (0 <= config.machine.pipes.indexOf(index)) {
                        var el = sprintf('stirring-%d', index);
                        if (-1 !== machine_status.stirring_status.indexOf(index))
                            showActivityIndicator(el);
                        else
                            hideActivityIndicator(el);
                    }
                });

                // update containers
                _.each(_.range(5), function(index) {
                    var el = sprintf('can%d-indicator', index);

                    if (0 <= config.machine.containers.indexOf(index)) {
                        if (-1 === machine_status.container_enabled.indexOf(index)) {
                            markDisabled(el);
                        }
                        else if (-1 === machine_status.container_availability.indexOf(index)) {
                            markWarning(el);
                        }
                        else if (-1 === machine_status.container_reserve.indexOf(index)) {
                            markNormal(el);
                        }
                        else {
                            markCritical(el);
                        }
                    }
                });

                // update caps
                _.each(_.range(3), function(index) {
                    var el = sprintf('cap%d-indicator', index);

                    if (0 <= config.machine.caps.indexOf(index)) {
                        if (-1 === machine_status.cover_enabled.indexOf(index)) {
                            markDisabled(el);
                        }
                        else if (-1 === machine_status.cover_availability.indexOf(index)) {
                            markWarning(el);
                        }
                        else if (-1 === machine_status.cover_reserve.indexOf(index)) {
                            markNormal(el);
                        }
                        else {
                            markCritical(el);
                        }
                    }
                });

                // container presence
                if (machine_status.container_presence)
                    markNormal('presence-indicator');
                else
                    markCritical('presence-indicator');

                // door status
                if (machine_status.doors_status)
                    markCritical('door-indicator');
                else
                    markNormal('door-indicator');
            }

            else if (! machine_query) {
                $('#status-level')
                    .html('Device not ready');

                $('#err-code')
                    .html('Could not retrieve machine status');

                // update pigments
                _.each(_.range(14), function (index) {
                    if (0 <= config.machine.pipes.indexOf(index)) {
                        var el = sprintf('status%d', index);
                        markNone(el);
                    }
                });

                // update containers
                _.each(_.range(5), function (index) {
                    if (0 <= config.machine.containers.indexOf(index)) {
                        var el = sprintf('can%d-indicator', index);
                        markNone(el);
                    }
                });

                // update caps
                _.each(_.range(3), function (index) {
                    if (0 <= config.machine.caps.indexOf(index)) {
                        var el = sprintf('cap%d-indicator', index);
                        markNone(el);
                    }
                });
            }
        }

        updateStatus = function (statusData) {
            machine_status = statusData;
            machine_query  = false;
            updatePage();
        };

        failedStatus = function () {
            machine_status = null;
            machine_query = false;
            updatePage();
        };

        _load_page('page_main', function() {

            updatePage();

            // Change timeout after diagnostic login
            Diagnostics.Timeout.set_limit(params.timeout);

            // Set up command buttons
            $('#reset')
                .off()
                .on('click', function(e) {
                    e.preventDefault();
                    disableButton('reset');
                    $.ajax({
                        type: 'POST',
                        url: params.urls.reset
                    }).always(function() {
                        enableButton('reset');
                    });
                });

            $('#autopurge')
                .off()
                .on('click', function(e) {
                    e.preventDefault();
                    disableButton('autopurge');
                    $.ajax({
                        type: 'POST',
                        url: params.urls.auto_purge
                    }).always(function() {
                        enableButton('autopurge');
                    });
                });

            $('#label-feed')
                .off()
                .on('click', function(e) {
                    e.preventDefault();
                    disableButton('label-feed');
                    $.ajax({
                        type: 'POST',
                        url: params.urls.label_feed
                    }).always(function() {
                        enableButton('label-feed');
                    });
                });

            $('#ac_open')
                .off()
                .on('click', function(e) {
                    e.preventDefault();
                    disableButton('ac_open');
                    $.ajax({
                        type: 'POST',
                        url : params.urls.enter_diagnostic
                    }).then(function() {
                        $.ajax({
                            type: 'POST',
                            url : params.urls.autocap_open
                        });
                    }).always(function() {
                        enableButton('ac_open');
                    });
                });

            $('#ac_close')
                .off()
                .on('click', function(e) {
                    e.preventDefault();
                    disableButton('ac_close');
                    $.ajax({
                        type: 'POST',
                        url : params.urls.enter_diagnostic
                    }).then(function() {
                        $.ajax({
                            type: 'POST',
                            url : params.urls.autocap_close
                        });
                    }).always(function() {
                        enableButton('ac_close');
                    });
                });

            $('#footer-page-left-arrow')
                .off()
                    .on('click', function(e) {
                    e.preventDefault();
                    exit();
                });

            if (AUTH_LEVEL_OPERATOR < auth.level) {
                $('#footer-page-right-arrow')
                    .removeClass('ui-disabled')
                    .off()
                    .on('click', function(e) {
                        e.preventDefault();
                        goPageCarriage();
                    });
            }
        });
    };

    return {
        init: init,
        exit: exit,
        main: goPageMain,
        circuit: goPageCircuit,
        carriage: goPageCarriage,

        /* reserved for debugging */
        force_cold_reset: force_cold_reset
    };
})();
