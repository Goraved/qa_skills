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

	var nods = document.getElementsByClassName('NO-CACHE');
for (var i = 0; i < nods.length; i++)
{
    nods[i].attributes['src'].value += "?a=" + Math.random();
}




var ind = 0;
function poll(id) {
    $.get('/TaskStatus/'+id, function(result) {
        if(result != 'True' && ind < 70) {
            ind++;
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

var myLink = document.getElementById('mylink');

function hintAlert() {
  alert("The program gathers 500+ QA vacancies from the DOU.UA, parses vacancies info and make a statistics based on predefined skill keywords.");
}


var categories = document.getElementById('id01');
// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == categories) {
        categories.style.display = "none";
    }
}

var controller = new ScrollMagic.Controller();

	// build tween
	var tween = TweenMax.from("#animate", 0.5, {autoAlpha: 0, scale: 0.7});

	// build scene
	var scene = new ScrollMagic.Scene({triggerElement: "a#top", duration: 200, triggerHook: "onLeave"})
					.setTween(tween)
					.addIndicators() // add indicators (requires plugin)
					.addTo(controller);

	// change behaviour of controller to animate scroll instead of jump
	controller.scrollTo(function (newpos) {
		TweenMax.to(window, 0.5, {scrollTo: {y: newpos}});
	});

	//  bind scroll to anchor links
	$(document).on("click", "a[href^='#']", function (e) {
		var id = $(this).attr("href");
		if ($(id).length > 0) {
			e.preventDefault();

			// trigger scroll
			controller.scrollTo(id);

				// if supported by the browser we can even update the URL.
			if (window.history && window.history.pushState) {
				history.pushState("", document.title, id);
			}
		}
	});




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

$(document).ready(function () {
$('#dtVerticalScrollExample').DataTable({
"scrollY": "200px",
"scrollCollapse": true,
});
$('.dataTables_length').addClass('bs-select');


});