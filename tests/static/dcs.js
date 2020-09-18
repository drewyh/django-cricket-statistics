$(document).ready(function(){
  $("table").addClass("table table-striped table-bordered table-hover table-sm table-responsive-md");
  $("nav.paginator ul").addClass("pagination pagination-sm justify-content-center");
  $("nav.paginator ul li").addClass("page-item");
  $("nav.paginator ul li a").addClass("page-link");
  $("nav.paginator ul li span").addClass("page-link");
  $("nav.paginator ul li span").parent().addClass("disabled");
  $("div.link-list a").addClass("btn btn-primary btn-block");
  $("h1 small").addClass("text-muted");
})
