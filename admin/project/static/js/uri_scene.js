$(function () {
    // 创建漏洞表单提交
    $("body").on("submit", '#UriForm', function (e) {
        e.preventDefault();
        var form = $(this);
        var _this = $(this);
        var uri = _this.attr('action');
        var params = form.serializeArray();

        _this.addClass("posting");
        $.ajax({
            url: uri,
            data: params,
            dataType: "json",
            type: "POST",
            success: function (resp) {
                if (resp.state) {
                    window.location.href = resp.redirect_url;
                } else {
                    _this.removeClass("posting");
                    var error = resp.error;
                    for (var name in error) {
                        $("#id-" + name +"-error").html(error[name][0]);
                    }
                }
            },
            error: function (err) {
                if (err.statusText !== 'abort') {
                    _this.removeClass("posting");
                    swal({
                        title: "哎呀，出错了",
                        type: "error",
                        confirmButtonColor:"#1ab394"
                    });
                }
            }
        })
    });

});

