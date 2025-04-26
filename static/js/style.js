$(document).ready(function() {
    $('form').on('submitt', function(x){
        x.preventDefault();
        var formdata = new FormData(this);

        $.ajax({
            url: $(this).attr('action'),
            type:'POST',
            data: formdata,
            processData: false,
            contentType: false,
            success: function(response){
                $('#mark-message').html('<span>Marks updated successfully!</span>');
            },
            error: function(xhr){
                $('#mark-message').html('<span>Failed to update marks.</span>');
            }
        })
    })
})