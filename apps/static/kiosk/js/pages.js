'use strict';


// Could be automatically filled by Page ("superclass" of all pages)
// but better do it explicitly
Pages.kiosk = {};
Pages.data.kiosk = {
    charged: false
};

function KioskHomePage(app_name, page) {
    /*
    *   can be used in other places, in freesample overrides it,
    *   but only difference is in html side
    * */
    Page.call(this, app_name, page);

    this.label_busy = null;     // error message instance,
    this.check_label_busy = function () {
        var thisObj = this;
        $.get('/kiosk/j/label-busy', function(data) {

            if (data.label_busy) {
                console.log('Label busy!');
                if (!thisObj.label_busy) {
                    thisObj.label_busy = thisObj.queue('.footer-error.label-busy', -1, -1, false, true);
                    console.log('....');
                }

                setTimeout(function() {
                    thisObj.check_label_busy();
                }, 1000);
            }

            else if (thisObj.label_busy) {
                thisObj.dequeue(thisObj.label_busy);
                thisObj.label_busy = null;
                // Pages.get_page('HOME').load();
            }
        });
    };

    this.on_page_loaded = function() {
        // to be used only the first time
        var thisObj = this;
        this.set_footer_message();

        Kiosk.Credit.stop().then(function() {
            thisObj.check_label_busy();
        });
    };
}
Pages.kiosk.home = new KioskHomePage('kiosk', 'home');


Pages.kiosk.select_color = new (function KioskSelectColorPage() {
    /*
    *
    * */
    Page.call(this, 'kiosk', 'select_color');

    this.on_page_loaded = function() {
        var keyboard = $('.keyboard.qwerty').first();
        $('#digit_color').append(keyboard);

        Kiosk.Credit.stop()
            .then(function() {
                $('#header-step-1')
                    .addClass('active');

                Kiosk.Colors.init();
                Kiosk.Keyboard.init();

                $('#clear-button')
                    .off()
                    .click(function(event) {
                        event.preventDefault();
                        Kiosk.Keyboard.clear('');
                    });
            });
    }

})();


Pages.kiosk.confirm_selection = new (function KioskConfirmSelectionPage() {
    /*
    *
    * */
    Page.call(this, 'kiosk', 'confirm_selection');
    this.first_load = true;
    this.available = null;
    this.granted = null;

    this.on_page_load = function() {

        Pages.data.kiosk.charged = false;

        // selected color in in hidden field - selected_color
        var recipe_id = $('#selected-color').attr('data-recipe-id');

        if (! recipe_id || recipe_id === '0' ) {
            // If no color selected, don't move on
            return false;
        }

        if (!this.first_load) {
            // terminate function, do not block the rest page loading
            // (obtained returning false)
            return true;
        }
        this.first_load = false;

        // Initialize the page 3 (color not available)
        $.ajax({
            type: 'POST',
            url: Pages.data.global.params.commands.color_available,
            data: {recipe: recipe_id},
            context: this,
            async: false
        }).then(function(data) {
            Pages.get_page('kiosk.confirm_selection').load({
                available: data.available,
                granted: Kiosk.Credit.granted()
            });
        });

        return false
    };

    this.on_page_loaded = function(data) {
        /*
        * data: returned from server (ajax load of confirm_selection page)
        *       includes: available, granted
        * */
        var sel = $('#selected-color');
        var description = sel.attr('data-description');

        this.first_load = true;

        // Reflect selected color in UI
        Kiosk.Colors.updateTriangle();
        $('#color-code').text($('#selected-color').text());
        $('#color-description').text($('#selected-color').attr('data-description'));
        $('#header-step-2').addClass('active');
        $('#button-no').off().click(function () {
            Pages.get_page('kiosk.select_color').load();
        });

        if (data.available) {
            console.log('Starting coin acceptor...');
            Kiosk.Credit
                .start()
                .then(function() {
                    $('#button-yes')
                        .off()
                        .click(function() {

                            if (! Kiosk.Credit.granted())
                                return; /* forget it */

                            console.log('Dispensation granted');
                            clearInterval(poller);

                            Pages.get_page('kiosk.progress_bar').load();
                        });

                    if (Kiosk.Credit.granted())
                        return;

                    var poller = setInterval(function() {

                        if (! Kiosk.Credit.granted())
                            return;

                        clearInterval(poller);

                        /* avoid loading page 3 twice due to a race */
                        Pages.get_page('kiosk.confirm_selection')
                            .load({available: true, granted: true});
                    }, 500);
                });
        }
    };

    this.on_page_leave = function() {
        this.first_load = true;
    }

})();


Pages.kiosk.progress_bar = new (function KioskProgressBarPage() {
    /*
    *
    * */
    Page.call(this, 'kiosk', 'progress_bar');

    this.on_page_load = function() {
        if (!Kiosk.Credit.granted()) {
            console.log('Not enough credit. Dispensation inhibited');
            return false;
        }

        if (!Pages.data.kiosk.charged) {
            Pages.data.kiosk.charged = true;

            // synchronous ajax call, will wait for response
            Kiosk.Credit.charge();
        }
    };

    this.on_page_loaded = function() {
        Kiosk.Credit.stop()
            .then(function() {
                var recipe_id = $('#selected-color').attr('data-recipe-id');
                var color = $('#selected-color').css('background-color');
                $('#imgLevel').css('background-color', color);
                $('#imgTopLevel').css('background-color', color);
                Kiosk.Dispensation.init(recipe_id, Pages.data.global.params);
            });
    };

    this.dispensation_completed = function () {
        var footer_step = this.html.find('.footer-step.completed');
        if (footer_step.length) {
            $('#footer-step').empty();
            footer_step.contents().appendTo('#footer-step');
        }
    }
})();


Pages.kiosk.dispensed = new (function KioskDispensedPage() {
    /*
    *
    * */
    Page.call(this, 'kiosk', 'dispensed');

    this.on_page_loaded = function() {
        var thisObj = this;
        Kiosk.Credit.stop()
            .then(function() {
                /* WARNING: for a weird bug of the shared HTML/CSS `YES` is no and `NO` is yes.
                Don't have time to fix this now :-/ */

                /* no (temporarily disabled for farbe) */
                //$('#button-yes')
                //    .off()
                //    .click(function() {
                //        Kiosk.Credit.collect()
                //            .then(Kiosk.Credit.refund)
                //            .done(goPage1);
                //    });
                /* yes */
                $('#button-yes').off().click(function ()    {
                    Pages.get_page('HOME').load();});

                /* yes */
                $('#button-no').off().click(function () {
                    thisObj.enable_link('button-no');
                });


                $('#header-step-3')
                    .addClass('active')
                ;

                // Reflect selected color in UI
                Kiosk.Colors.updateTriangle();
                $('#color-code')
                    .text($('#selected-color').text())
                ;

                $('#color-description')
                    .text($('#selected-color').attr('data-description'))
                ;
            });

    };
})();

