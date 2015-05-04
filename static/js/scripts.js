jQuery(function($){

  $('#category-button').click(function(e){
    $('#new-category').modal({
      overlayClose:true,
      opacity:80,
      overlayCss: { backgroundColor: '#222' },
      minHeight: 90
    });
    return false;
  });

  $('#submit-category').bind('click', function(){
    $.getJSON("/new_category", {
      name: $('#category-form>input[type="text"]').val()
    }, function(addedCategory){
      $('select[name="category"]').append(
        '<option value="' + addedCategory.id + '">' + addedCategory.name + '</option'
      );
      $.modal.close();
    });
    return false;
  });
});
