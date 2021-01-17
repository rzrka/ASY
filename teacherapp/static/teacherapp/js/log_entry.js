   $(document).ready(function() {
       // CSRF code
       function getCookie(name) {
           var cookieValue = null;
           var i = 0;
           if (document.cookie && document.cookie !== '') {
               var cookies = document.cookie.split(';');
               for (i; i < cookies.length; i++) {
                   var cookie = jQuery.trim(cookies[i]);
                   // Does this cookie string begin with the name we want?
                   if (cookie.substring(0, name.length + 1) === (name + '=')) {
                       cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                       break;
                   }
               }
           }
           return cookieValue;
       }
       var csrftoken = getCookie('csrftoken');

       function csrfSafeMethod(method) {
           // these HTTP methods do not require CSRF protection
           return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
       }
       $.ajaxSetup({
           crossDomain: false, // obviates need for sameOrigin test
           beforeSend: function(xhr, settings) {
               if (!csrfSafeMethod(settings.type)) {
                   xhr.setRequestHeader("X-CSRFToken", csrftoken);
               }
           }
       });

       var selected_items = {
           'Semester': null,
           'StudentGroup': null,
           'Discipline': null,
       };

       $('main').on('click', 'a.list-item.ajax-item', function(e) {
           //e.preventDefault();
           var $this = $(this),
               data = $this.data();

           id = data['id']
           model = data['model']
           selected_items[model] = id;

           //$this.hide();
           $.ajax({
               url: url_addres,
               headers: { "X-CSRFToken": csrftoken },
               method: 'POST',
               data: {
                   'Semester': selected_items['Semester'],
                   'StudentGroup': selected_items['StudentGroup'],
                   'Discipline': selected_items['Discipline']
               },
               success: function(data) {
                   console.log(selected_items);
                   if (data.redirect) {
                       window.location.href = data.redirect;
                   }
                   $("main").html(data);
               },
               error: function(data) {
                   console.log(data);
               }
           });
       });
   });