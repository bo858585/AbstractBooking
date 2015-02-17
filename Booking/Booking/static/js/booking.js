$( document ).ready(function() {
    console.log( "ready!" );

    $( "button.serve, button.complete").on('click', function( event ) {
        event.preventDefault();
        event.stopPropagation();

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

        $.ajax({
            type: "POST",
            url: "/booking/" + url_part,
            data: { "id": value, "csrfmiddlewaretoken": csrfmiddlewaretoken },
            dataType: "json",
            success: function(msg){
                console.log(msg["request_status"]);
                if (msg["request_status"] == "running") {
                    console.log($(this).parent());
                    $(this).prev().remove();
                } else {
                  console.log( "Error");
                }
                return false;
            },
            error: function(jqXHR, textStatus, errorThrown){
                console.log( "Error", jqXHR, textStatus, errorThrown);
            }
          });
    });
});
