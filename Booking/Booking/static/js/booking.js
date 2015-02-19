$( document ).ready(function() {
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
                    console.log("Назначено пользователю");
                } else {
                    if (msg["request_status"] == "insufficient funds") {
                        console.log( "Недостаточно средств");
                    } else {
                        console.log( "Error");
                    }
                }
                return false;
            },
            error: function(jqXHR, textStatus, errorThrown){
                console.log( "Error", jqXHR, textStatus, errorThrown);
            }
          });
    });
});
