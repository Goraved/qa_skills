//// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function() {
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
for (var i = 0; i < nods.length; i++) {
    nods[i].attributes['src'].value += "?a=" + Math.random();
}




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


var myLink = document.getElementById('mylink');

function hintAlert() {
    alert("The program gathers 500+ QA vacancies from the DOU.UA, parses vacancies info and make a statistics based on predefined skill keywords.");
}

// When the user clicks anywhere outside of the modal, close it
var categories = document.getElementById('id01');
var graph_img = document.getElementById('graph_img');
window.onclick = function(event) {
    if (categories != null) {
        if (event.target == categories) {
            categories.style.display = "none";
        }
    }
    if (graph_img != null) {
        if (event.target == graph_img) {
            location.href = "#"
        }
    }
}

// Select all links with hashes
$('a[href*="#"]')
    // Remove links that don't actually link to anything
    .not('[href="#"]')
    .not('[href="#0"]')
    .click(function(event) {
        // On-page links
        if (
            location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') &&
            location.hostname == this.hostname
        ) {
            // Figure out element to scroll to
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            // Does a scroll target exist?
            if (target.length) {
                // Only prevent default if animation is actually gonna happen
                event.preventDefault();
                $('html, body').animate({
                    scrollTop: target.offset().top
                }, 1000, function() {
                    // Callback after animation
                    // Must change focus!
                    var $target = $(target);
                    $target.focus();
                    if ($target.is(":focus")) { // Checking if the target was focused
                        return false;
                    } else {
                        $target.attr('tabindex', '-1'); // Adding tabindex for elements not focusable
                        $target.focus(); // Set focus again
                    };
                });
            }
        }
    });