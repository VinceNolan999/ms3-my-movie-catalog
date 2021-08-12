$(document).ready(function () {
  $(".sidenav").sidenav({edge: "right"});
  $('select').formSelect();
  $(".datepicker").datepicker({
    format: "yyyy",
    yearRange: 100,
    showClearBtn: true,
    i18n: {
        done: "Select"
      }
  });
});