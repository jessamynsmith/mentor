var convertDataToDate = function(data) {
    for (var i=0; i<data.length; i++) {
        data[i][0] = Date.parse(data[i][0]);
    }
    return data;
};

var payout_history = function(data) {
    $('#id_payout_history').highcharts({
        title: {
            text: 'Payout History'
        },
        chart: {
            type: 'column',
            zoomType: 'x'
        },
        xAxis: {
            type: 'datetime'
        },
        rangeSelector: {
            enabled: true
        },
        scrollbar: {
            enabled: true
        },
        yAxis: {
            title: {
                text: 'Amount ($)'
            }
        },
        series: [{
            name: 'Payout',
            data: convertDataToDate(data.amounts)
        }, {
            name: 'Earnings',
            data: convertDataToDate(data.earnings)
        }
        ]
    });
};

var payment_history = function(data) {
    $('#id_payment_history').highcharts({
        title: {
            text: 'Payment History'
        },
        chart: {
            type: 'column',
            zoomType: 'x'
        },
        xAxis: {
            type: 'datetime',
            maxZoom: null
        },
        rangeSelector: {
            enabled: true
        },
        scrollbar: {
            enabled: true
        },
        yAxis: {
            title: {
                text: 'Earnings ($)'
            }
        },
        series: [{
            name: 'Payment',
            data: convertDataToDate(data.payments)
        }
        ]
    });
};

var hours_worked = function(data) {
    $('#id_hours_worked').highcharts({
        title: {
            text: 'Hours Worked'
        },
        chart: {
            type: 'column',
            zoomType: 'x'
        },
        xAxis: {
            type: 'datetime'
        },
        rangeSelector: {
            enabled: true
        },
        scrollbar: {
            enabled: true
        },
        yAxis: {
            title: {
                text: 'Hours'
            }
        },
        series: [{
            name: 'Hours',
            data: convertDataToDate(data.hours)
        }
        ]
    });
};

var updateView = function() {
    $('.statistics').hide();
    var viewType = $('#id_select_statistics').val();
    $("#id_" + viewType).show();

    var viewFunction = window[viewType];
    if (typeof viewFunction === "function") {
        $.ajax({
            url: viewType,
            contentType: 'application/json',
            success: function (data, textStatus, jqXHR) {
                if ($.isEmptyObject(data)) {
                    $("." + viewType + "_error").show();
                } else {
                    viewFunction(data);
                }
            }
        });
    }
};

$(document).ready(function () {
    Highcharts.setOptions({
        global: {
            getTimezoneOffset: function (timestamp) {
                var timezoneOffset = -moment.tz(timestamp, TIMEZONE).utcOffset();
                return timezoneOffset;
            }
        }
    });

    $('#id_select_statistics').on('change', updateView);
    updateView();
});
