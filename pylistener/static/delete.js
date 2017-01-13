$(document).ready(function(){
    var del_contacts = $(".del_contact");
    del_contacts.on("click", function(event){
        // send ajax request to delete this contact
        event.preventDefault();
        $.ajax({
            method: 'DELETE',
            url: '/delete/' + $(this).attr("data-id"),
            data: "add",
            success: function(){
                console.log("deleted");
            }
        });        
        // fade out expense
        this_row = $(this.parentNode.parentNode);
        // delete the containing row
        this_row.animate({
            opacity: 0
        }, 500, function(){
            $(this).remove();
        })
    });

    var del_att = $(".del_att");
    del_att.on("click", function(event){
        // send ajax request to delete this attribute
        event.preventDefault();
        $.ajax({
            method: 'DELETE',
            url: '/delete/' + $(this).attr("data-id"),
            data: "att",
            success: function(){
                console.log("deleted");
            }
        });        
        // fade out expense
        this_row = $(this.parentNode.parentNode);
        // delete the containing row
        this_row.animate({
            opacity: 0
        }, 500, function(){
            $(this).remove();
        })
    });
});
