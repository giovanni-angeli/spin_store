/**
 * This class provides for the creation of a grey-out layer on top of the whole
 * page, with an inner pip-up like div, to which is possible to add custom content
 */

function Overlay(content, args) {
    /*
    * content: jQuery isntance
    * */
    this.div = $(''
        + '<div id="overlay-outer">'
        + '    <div id="overlay-middle">'       // used for vertical-centering
        + '        <div id="overlay-content">'
        + '        </div>'
        + '    </div>'
        + '</div>'
    );

    this.outer = this.div.find('#overlay-outer').addBack('#overlay-outer');
    this.middle = this.div.find('#overlay-middle');
    this.content = this.div.find('#overlay-content');
    this.content.append(content.clone());

    this.t0 = new Date();
    this.duration_min = 0;      // milliseconds of minimum duration (will wait if delayed_destroy is called before that)
    this.duration = 0;          // milliseconds to self-destroy. 0 to disable
    this.outer_css = {};        // css values to add or override defaults
    this.middle_css = {};
    this.content_css = {};

    if (args)
        for (var arg in args)
            this[arg] = args[arg];


    this.outer.css($.extend({
        display: 'table',
        position: 'absolute',
        top: 0,     // required to display on top of everything
        width: '100%',
        height: '100%',
        background: 'rgba(0, 0, 0, 0.69)'
    }, this.outer_css));

    this.middle.css($.extend({
        position: 'relative',
        width: '100%',
        display: 'table-cell',
        'vertical-align': 'middle'
    }, this.middle_css));

    this.content.css($.extend({
        position: 'relative',
        margin: 'auto',
        width: '69%',
        height: '69%',
        background: 'rgba(255, 255, 255, 1)'
    }, this.content_css));

    $('html').append(this.div);

    if (this.duration)
        setTimeout(function(thisObj) {
            return function() {
                thisObj.destroy();
            }
        }(this), this.duration);

    this.destroy = function(delayed) {
        if (!delayed) {
            this.div.remove();
            return;
        }

        var thisObj = this;
        return new Promise(function(resolve, reject) {
            var dt = thisObj.duration_min - (new Date() - thisObj.t0);

            setTimeout(function() {
                thisObj.div.remove();
                resolve();
            }, dt);
        });
    };
}
