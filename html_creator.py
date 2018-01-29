

def add_table_row(variables):
    row = '<tr class="row100 body">'
    for index, var in enumerate(variables):
        row += '<td class="cell100 column%s">%s</td>' % (str(index + 1), var)
    return row + '</tr>'


def create_table(title, variables):
    table = '<hr> <h2>%s</h2> <div class="table100 ver3 m-b-110"> <div class="table100-head"> <table> <thead> <tr class="row100 head">' % title
    for index, var in enumerate(variables):
        table += '<th class="cell100 column%s">%s</th>' % (str(index + 1), var)
    return table + '</tr> </thead> </table> </div> <div class="table100-body js-pscroll"> <table> <tbody>'


def close_table():
    return '</tbody> </table> </div> </div>'


def create_html(title):
    return """<!DOCTYPE html>
<html lang="en">
   <head>
      <title>QA skills</title>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link rel="shortcut icon" href="{{ url_for('static', filename='images/icons/favicon.ico') }}">
      <link rel="stylesheet" type="text/css" href="static/vendor/bootstrap/css/bootstrap.min.css">
      <link rel="stylesheet" type="text/css" href="static/fonts/font-awesome-4.7.0/css/font-awesome.min.css">
      <link rel="stylesheet" type="text/css" href="static/vendor/animate/animate.css">
      <link rel="stylesheet" type="text/css" href="static/vendor/select2/select2.min.css">
      <link rel="stylesheet" type="text/css" href="static/vendor/perfect-scrollbar/perfect-scrollbar.css">
      <link rel="stylesheet" type="text/css" href="static/css/util.css">
      <link rel="stylesheet" type="text/css" href="static/css/main.css">
       <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Raleway">
</head>
<body>
<div class="bgimg w3-display-container w3-animate-opacity w3-text-black">
    <div class="w3-display-topleft w3-padding-large w3-xlarge">
        <a href="/">Back</a>
    </div>
</div>
      <div class="limiter">
      <div class="container-table100">
      <div class="wrap-table100">
      <h1>%s</h1>
      <h2>%s</h2>
      """ % (title[0], title[1])


def create_link(url, title):
    return """<a href = '%s' target=_blank>%s</a>""" % (url, title)


def close_html():
    return """</div>
</div>
</div>
<script src="static/vendor/jquery/jquery-3.2.1.min.js"></script>
<script src="static/vendor/bootstrap/js/popper.js"></script>
<script src="static/vendor/bootstrap/js/bootstrap.min.js"></script>
<script src="static/vendor/select2/select2.min.js"></script>
<script src="static/vendor/perfect-scrollbar/perfect-scrollbar.min.js"></script>
<script>
   $('.js-pscroll').each(function(){
   	var ps = new PerfectScrollbar(this);
   
   	$(window).on('resize', function(){
   		ps.update();
   	})
   });
</script>
<script src="static/js/main.js"></script></body></html>"""
