$(document).ready(function(){
  $("table").addClass("table table-striped table-bordered table-hover table-sm table-responsive");
  $("ul.pages").addClass("pagination pagination-sm justify-content-center");
  $("ul.pages li").addClass("page-item");
  $("ul.pages li a").addClass("page-link");
  $("ul.pages li span").addClass("page-link");
  $("ul.pages li span").parent().addClass("disabled");
  $("div.link-list a").addClass("btn btn-primary btn-block");
})
