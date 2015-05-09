jQuery(function($){
  categoryDropdown = $('select[name="category"]');

  categoryDropdown.on('change', function(e){
    if (this.value === "new-category") {
      $('#new-category').modal({
        overlayClose:true,
        opacity:80,
        overlayCss: { backgroundColor: '#222' },
        minHeight: 90
      });
      this.value = "-Category-";
      return false;
    }
  });

  $('#submit-category').bind('click', function(){
    $.getJSON("/new_category", {
      name: $('#category-form>input[type="text"]').val()
    }, function(addedCategory){
      $('select[name="category"] option:last').before(
        '<option selected="selected" value="' + addedCategory.id + '">' + addedCategory.name + '</option'
      );
      var success = $('<div>').text('Successfully added category').addClass('twelve columns notification success');
      $('.flashes').append(success);
      categoryDropdown.value = addedCategory.id;
      $.modal.close();
    });
    return false;
  });
});
