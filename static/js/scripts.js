jQuery(function($){

  $('#category-button').click(function(e){
    $('#new-category').modal();
    return false;
  });

  $('#submit-category').bind('click', function(){
    $.getJSON("/new_category", {
      name: $('#category-form>input[type="text"]').val()
    }, function(data){
      alert(data.addedCategory);
    });
    return false;
  });
});
