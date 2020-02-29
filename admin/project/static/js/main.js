// 侧边栏控制
jQuery(function ($) {

    // Dropdown menu
    $(".sidebar-dropdown > a").click(function () {
        $(".sidebar-submenu").slideUp(200);
        if ($(this).parent().hasClass("active")) {
            $(".sidebar-dropdown").removeClass("active");
            $(this).parent().removeClass("active");
        } else {
            $(".sidebar-dropdown").removeClass("active");
            $(this).next(".sidebar-submenu").slideDown(200);
            $(this).parent().addClass("active");
        }
    });

    // 三级菜单控制
    $(".sidebar-dropdown-3 > a").click(function () {
        $(".sidebar-submenu-3").slideUp(200);
        if ($(this).parent().hasClass("active")) {
            $(".sidebar-dropdown-3").removeClass("active");
            $(this).parent().removeClass("active");
        } else {
            $(".sidebar-dropdown-3").removeClass("active");
            $(this).next(".sidebar-submenu-3").slideDown(200);
            $(this).parent().addClass("active");
        }
    });

    //toggle sidebar
    $("#toggle-sidebar").click(function () {
        $(".page-wrapper").toggleClass("toggled");
    });
    //Pin sidebar
    $("#pin-sidebar").click(function () {
        if ($(".page-wrapper").hasClass("pinned")) {
            // unpin sidebar when hovered
            $(".page-wrapper").removeClass("pinned");
            $("#sidebar").unbind("hover");
        } else {
            $(".page-wrapper").addClass("pinned");
        }
    });

    $(".sidebar-menu").click(function () {
        if ($(".page-wrapper").hasClass("pinned")) {
            $(".page-wrapper").removeClass("pinned");
        }
    });

    //toggle sidebar overlay
    $("#overlay").click(function () {
        $(".page-wrapper").toggleClass("toggled");
    });

});


function goToUrlByParams(key, value) {
    let url = new URL(window.location.href);
    url.searchParams.set(key, value);
    window.location.href = url.href;
}

// 跳转至分页页面
function goToPageNum() {
    $("#soc-go-page-btn").click(function () {
        let num = $("#soc-go-page-input").val();
        goToUrlByParams("page", num);
    })
}

// 更新页面展示条数
function goToPageSize() {
    $("#soc-change-page-size").on('change', function () {
        goToUrlByParams("page_size", this.value);
    });
}


// 是否是暗黑模式
function isDarkModeEnabled() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
}


// 替换底部LOGO图片
function replaceFooterLogoImage(url) {
    $(".soc-footer-logo").attr("src", url);
}


// 展开URL对应的侧边栏
function showSidebarForUrl(path) {
    let selector = '.sidebar-menu a[href="' + path + '"]';
    let currentNav = $(selector);
    currentNav.parents('li').addClass('active');
    currentNav.parents(".sidebar-dropdown").addClass('active');
    currentNav.parents(".sidebar-submenu").slideDown(0);
    currentNav.parents(".sidebar-dropdown-3").addClass('active');
    currentNav.parents(".sidebar-submenu-3").slideDown(0);
    currentNav.addClass("soc-sidebar-active");
}

// 普通表单改为Horizontal form
function toFormHorizontal() {
    $(".form-horizontal").children(".form-group").addClass("row");
}



function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
// 为POST请求添加csrftoken
function djangoAjaxSetup() {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                let csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}

// 关掉浏览器自动补全[日期、时间input]
function turnAutoCompleteOff() {
    $(".datetime").attr("autocomplete", "off")
}


$(function () {
    showSidebarForUrl();

    toFormHorizontal();

    goToPageNum();

    goToPageSize();

    turnAutoCompleteOff();
});
