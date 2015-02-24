$( document ).ready(function() {
    var xhr;

    $( "button.serve, button.complete").on('click', function( event ) {
        event.preventDefault();
        event.stopPropagation();

        if(xhr && xhr.readyState != 4){
            xhr.abort();
        }

        var value = $(this).prev().val();
        var csrfmiddlewaretoken = $(this).prev().prev().val();
        var url_part = "";

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
            success: function(msg){
                $("div.alert").remove();
                $("div#greeting").after('<div class="alert alert-info">' + msg["request_status"] + '</div>');
                return false;
            },
            error: function(jqXHR, textStatus, errorThrown){
                console.log( "Error", jqXHR, textStatus, errorThrown);
            }
          });
    });
});
