var timer = null;

function status_display(status) {
    var status_values = ["unknown", "queued", "in progress", "completed", "aborted"];
    var text = '???';
    if ( status >= 0 && status < status_values.length ) {
        text = status_values[status];
    }
    return text;
}

function is_pending(status) {
    if (status==1 || status==2) {
        // "queued" or "in progress"
        return true;
    }
    return false;
}

function updateLastSentFormulaStatus() {

    if (timer != null) {
        clearTimeout(timer);
        timer = null;
    }

    $.ajax({
        url: URL_CHECK_LAST_FORMULA,
        cache: false,
        crossDomain: false,
        type: 'get',
        dataType: 'json',
        contentType: 'application/json; charset=utf-8'
    }).done(function(data) {
        $('#last_sent_formula_status').html(status_display(data.status));
        if (is_pending(data.status)) {
            timer = setTimeout(updateLastSentFormulaStatus, 1000);
        }
    }).fail(function (jqXHR, textStatus, errorThrown) {
        $('#last_sent_formula_status').html('???');
        timer = setTimeout(updateLastSentFormulaStatus, 5000);
    });

}

function loadStockRecipesPage(page) {
    $.ajax({
        url: URL_STOCK_RECIPES,
        data: {page: page},
        dataType: 'html'
    }).done(function(html) {
        $("#stock-content").html(html);
        // After html fragment has been loaded, bind the pagination links
        $('#stock-content .pagination li a').click( function(e) {
            e.preventDefault();
            var href = $(e.target).attr('href'); // es: "?page=3"
            var page = href.substr(href.indexOf('=')+1);
            loadStockRecipesPage(page);
        });

    });
}

function loadCustomRecipesPage(page) {
    $.ajax({
        url: URL_CUSTOM_RECIPES,
        data: {page: page},
        dataType: 'html'
    }).done(function(html) {
        $("#custom-content").html(html);
        // After html fragment has been loaded, bind the pagination links
        $('#custom-content .pagination li a').click( function(e) {
            e.preventDefault();
            var href = $(e.target).attr('href'); // es: "?page=3"
            var page = href.substr(href.indexOf('=')+1);
            loadCustomRecipesPage(page);
        });
    });
}


function displayLastFormulaAsTable() {
    $.ajax({
        url: URL_LAST_FORMULA_AS_TABLE,
        cache: false,
        crossDomain: false,
        type: 'get'
    }).done(function(data) {
        $('#last_formula_as_table').html(
            '<br />' +
            data +
            '<a href="javascript:window.print()">Print</a>'
        );
    }).fail(function (jqXHR, textStatus, errorThrown) {
        $('#last_formula_as_table').html('');
    });
}

