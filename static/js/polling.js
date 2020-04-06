$(function () {
		$('button').click(function () {
			$.ajax({
				url: '/get_stat',
				data: $('form').serialize(),
				type: 'POST',
				success: function (response) {
					poll(response);
				},
				error: function (error) {
					console.log(error);
				}
			});
		});

	});

var ind = 0;

function poll(id) {
    $.get('/TaskStatus/' + id, function(result) {
        if (result != 'True' && ind < 70) {
            ind++;
            $("#wait").css("display", "block");
            $("#analyze").prop("disabled", true);
            setTimeout(poll.bind(null, id), 5000);
        } else {
            window.location.href = "/statistics"
            $("#wait").css("display", "none");
            $("#analyze").prop("disabled", false);
        }
    })
}