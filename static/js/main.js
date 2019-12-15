//// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function () {
	scrollFunction()
};

function scrollFunction() {
	if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
		document.getElementById("scrollBtn").style.display = "block";
	} else {
		document.getElementById("scrollBtn").style.display = "none";
	}
}


(function ($) {
	"use strict";
	$('.column100').on('mouseover', function () {
		var table1 = $(this).parent().parent().parent();
		var table2 = $(this).parent().parent();
		var verTable = $(table1).data('vertable') + "";
		var column = $(this).data('column') + "";

		$(table2).find("." + column).addClass('hov-column-' + verTable);
		$(table1).find(".row100.head ." + column).addClass('hov-column-head-' + verTable);
	});

	$('.column100').on('mouseout', function () {
		var table1 = $(this).parent().parent().parent();
		var table2 = $(this).parent().parent();
		var verTable = $(table1).data('vertable') + "";
		var column = $(this).data('column') + "";

		$(table2).find("." + column).removeClass('hov-column-' + verTable);
		$(table1).find(".row100.head ." + column).removeClass('hov-column-head-' + verTable);
	});

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
})(jQuery);

function polling(res) {
    var status = 'False'
    while (status === 'False') {
	$.ajax(`/TaskStatus/${res}`, {
		method: "GET",
		success: function (response) {
			status = response;
			sleep(2000);
		},
	})
}

	$(document).ajaxStart(function () {
		$("#wait").css("display", "block");
	});
	$(document).ajaxComplete(function () {
		$("#wait").css("display", "none");
	});
	$("button").click(function () {
		$("#txt").load("demo_ajax_load.asp");
	});
}

function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}

function poll(id) {
    $.get('/TaskStatus/'+id, function(result) {
        if(result != 'True') {
            $("#wait").css("display", "block");
            $("#analyze").prop( "disabled", true );
            setTimeout(poll.bind(null, id), 5000);
        }
        else{
            window.location.href = "/statistics"
            $("#wait").css("display", "none");
            $("#analyze").prop( "disabled", false );
        }
    })
}
