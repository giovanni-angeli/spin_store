'use strict';

function Keyboard(el_keys, el_display, el_clear, args) {
    /*
    * el_keys: jQuery object of div containing ul-elements (rows of the keyboard)
    * ed_display: jQuery element used as the "screen' of the keyboard
    *   (normally div or input, may non exists)
    * el_clear: jQuery object of div containing the clear button (not required)
    * args: "dict" which ca be used to replace Keyboard's properties
    *   ie placeholder, min_chars, max_chars
    *
    *  NB: adds class keyboard-active, to active display
    * */
    this.enabled = true;
    this.input = '';
    this.keys = el_keys;
    this.display = el_display;
    this.clear_bt = el_clear;   // if set, requires a display, once applied, will keep working
    this.clear_bt_take_focus = true;   // if true, when clearing a display, that display will be set (if it had lost focus for this keyboard)
    this.placeholder = '';  // char to use to signal an empty slot gor a char, ie  '-'
    this.min_chars = 0;
    this.max_chars = -1;     // <0 for unlimited

    // function to execute each time the value of input changes.
    // in function, this will refer to this Keyboard!!
    this._on_change = null;

    if (args)
        for (var arg in args)
            this[arg] = args[arg];

    if (this.on_change) {
        // in case on_change arrived with the args, move it to this._on_change
        this._on_change = this.on_change;
        this.on_change = undefined;
    }

    this._init_bt = function (thisObj) {
        /* returns a function which should be called in the context of the
        *  button's DOM element */

        var bt_click_fn = function bt_click_fn(bt) {
            /* bt: jQuery instance of html element of the button (the <li>) */

            return function () {
                /* key: the key being pressed, ie  q | w | e | del | ... */
                var key = bt.text();
                if (bt.data('command'))
                    key = bt.data('command');

                var input = thisObj.input;
                switch (key) {
                    case 'del':
                        if (input.length > thisObj.min_chars)
                            input = input.slice(0, -1);
                        break;

                    default:
                        if (thisObj.max_chars < 0 || thisObj.max_chars > input.length)
                            input += key;
                }

                thisObj.set(input);
            }
        };

        return function () {
            var bt = $(this);   //jQuery instance of button element
            bt.click(bt_click_fn(bt));
        }
    }(this);

    this.on_change = function (f) {
        // f: function to set function, null to set to null, undefined to call (if set)
        // NB: thanks to below closure, f will be able to use   this, to refer to
        // this keyboard instance
        if (f) {
            this._on_change = (function () {
                f.apply(this);
            });
        }

        else if (f === null) {
            this._on_change = null;
        }

        else if (this._on_change) {
            this._on_change();
        }

        if (this.clear_bt) {
            if (this.input.length == 0)
                this.clear_bt.removeClass('enabled').addClass('disabled');
            else
                this.clear_bt.removeClass('disabled').addClass('enabled');
        }
    };
    this.set = function (input) {
        var old_input = this.input;

        if (input !== undefined)
            this.input = input;

        if (this.display) {
            this.display.val(this.input);
            if (this.placeholder)
                while (this.display.val().length < this.max_chars)
                    this.display.val(this.display.val() + this.placeholder)
        }

        if (this.input != old_input) {
            this.on_change();
        }
    };
    this.get = function () {
        return this.input;
    };
    this.disable = function () {
        this.enabled = false;
        this.keys.addClass('disabled');
        this.keys.find('li').off('click');
    };
    this.enable = function () {
        this.enabled = true;
        this.keys.removeClass('disabled');
        this.keys.find('li').each(this._init_bt);
    };
    this.set_display = function (el_display, el_clear, args) {
        // el_display: jQuery element
        // args: might replace args
        if (this.display)
            this.display.removeClass('keyboard-active');

        this.display = null;
        this.clear_bt = null;

        if (el_display) {
            this.display = el_display;
            var val = el_display.val();
            if (this.placeholder)
                while (val[val.length - 1] == this.placeholder)
                    val = val.slice(0, -1);
            this.input = val;
            this.display.addClass('keyboard-active');
        }

        if (el_clear) {
            this.clear_bt = el_clear;
            this.clear_bt.off('click');
            var thisObj = this;
            var thisDisplay = thisObj.display;
            var thisClearBt = thisObj.clear_bt;
            this.clear_bt.click(function () {
                //set focus to display the button refers to
                thisObj.set_display(thisDisplay, thisClearBt);
                thisObj.set('');
            })
        }

        if (args)
            for (var arg in args)
                this[arg] = args[arg];

        this.on_change();
    };

    if (this._on_change)
        this.on_change(this._on_change);    // initialise function (add context)
    if (this.display)
        this.set_display(this.display, this.clear_bt);  // includes initializations

    this.set();
    this.on_change();
    this.enabled? this.enable() : this.disable();
}