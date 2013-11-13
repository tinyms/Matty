(function ($) {

    $.fn.JsonTable = function (options) {
        var settings = $.extend({
            head: [],
            json: [],
            render: function (field_name, field_val, row) {
                return field_val;
            }
        }, options);
        this.data("settings", settings);
        var thead = $(this.selector + ' thead').append("<tr></tr>\n");
        for (var i = 0; i < settings.head.length; i++) {
            $(this.selector + ' tr').append("<th>" + settings.head[i] + "</th>\n")
        }
        return this;
    };

    $.fn.JsonTableUpdate = function (options) {
        var opt = $.extend({
            source: undefined,
            rowClass: undefined,
            callback: undefined
        }, options);
        var settings = this.data("settings");
        var sel = this.selector;
        $(this.selector + ' tbody > tr').remove();

        if (typeof opt.source == "string") {
            $.get(opt.source, function (data) {
                $.fn.UpdateFromObj(data, settings, sel, opt.rowClass, opt.callback);
            });
        }
        else if (typeof opt.source == "object") {
            $.fn.UpdateFromObj(opt.source, settings, sel, opt.rowClass, opt.callback);
        }
    }

    $.fn.UpdateFromObj = function (obj, settings, selector, trclass, callback) {
        var row = "";

        for (var i = 0; i < obj.length; i++) {
            if (!trclass) {
                row += "<tr>";
            } else {
                row += "<tr class='" + trclass + "'>";
            }

            for (var j = 0; j < settings.json.length; j++) {
                var cell_value = settings.render(settings.json[j], obj[i][settings.json[j]], obj[i])
                row += "<td>" + cell_value + "</td>";
            }
            row += "</tr>";
        }
        $(selector + '> tbody:last').append(row);

        if (typeof callback == "function") {
            callback();
        }

        $(window).trigger('resize'); // trigger the resize event to reposition dialog once all the data is loaded
    }

}(jQuery));
