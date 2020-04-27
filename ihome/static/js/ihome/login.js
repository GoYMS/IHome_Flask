function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        // 将表单的数据存放到对象data中
        var data = {
            mobile:mobile,
            password:passwd
        }
        // 将data数据转换成json格式
        var json_data = JSON.stringify(data)
        $.ajax({
            url: "/api/v1.0/sessions",
            type:"post",
            data:json_data,
            contentType:"application/json;charset=UTF-8",
            dataType:"json",
            headers :{
                'X-CSRFTOKEN':getCookie('csrf_token')
            },
            success:function (resp) {
                if (resp.errno=='0'){
                    // 登录成功，跳转到主页
                    location.href = '/'
                }
                else {
                    // 其他错误信息，在页面中显示
                    $('#password-err span').html(resp.errmsg)  //将错误信息显示在前端标签中
                    $('#password-err').show()  //将原本隐藏的标签显现出来
                }
            }
        })

    });
})