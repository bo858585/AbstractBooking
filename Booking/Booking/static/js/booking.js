$(document).ready(function () {
  'use strict';
  var xhr;

  $("button.serve, button.complete").on('click', function (event) {
    event.preventDefault();
    event.stopPropagation();

    if (xhr && xhr.readyState !== 4) {
      xhr.abort();
    }

    var value = $(this).prev().val(),
    csrfmiddlewaretoken = $(this).prev().prev().val(),
    url_part = "",
    that = $(this);

    if ($(this).hasClass('serve')) {
      url_part = "serve/";
    } else {
      if ($(this).hasClass('complete')) {
        url_part = "complete/";
      }
    }

    xhr = $.ajax({
      type: "POST",
      url: "/booking/" + url_part,
      data: { "id": value, "csrfmiddlewaretoken": csrfmiddlewaretoken },
      dataType: "json",
      success: function (msg) {
        $("div.alert").remove();
        $("div#greeting").after('<div class="alert alert-info">' + msg.request_status + '</div>');
        if (msg.request_status.substr(0, 15) === "Заказ завершен.") {
            that.closest('tr').html('');
        } else {
            that.closest('form').html('');
        }
        return false;
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.log("Error", jqXHR, textStatus, errorThrown);
      }
    });
  });
});
