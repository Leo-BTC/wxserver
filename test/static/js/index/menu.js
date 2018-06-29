jQuery(function () {




});


//当前页面路径
var pathname = window.location.pathname;

$('a').each(function () {
    //标签路径
    var href = $(this).attr("href");

    var fdStart = pathname.indexOf(href); //是否路径开头
//    if (fdStart === 0) {
//        $(this).parent("li").addClass("active");
//        var collapseDiv = $(this).parent("li").parent("ul").parent("div");
//        collapseDiv.removeClass("collapse");
//        collapseDiv.addClass("collapse in");
//    }

});


