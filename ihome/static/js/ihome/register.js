// js读取cookie的方法
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

var imageCodeId = "";

function generateUUID() {
    // 生成uuid
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode() {
    // 形成图片验证码的后端地址，设置到页面中，让浏览器请求验证码图片
    // 1. 生成图片验证码的编号  imageCodeId这个是全局变量，因为后边还需要
    imageCodeId = generateUUID()
    // 生成图片的url
    var url = 'api/v1.0/image_codes/' + imageCodeId
    // 将生成的url传入到对应的标签的src中
    $('.image-code img').attr('src', url)
}

function sendSMSCode() {
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }

    var req_data ={
        image_code :imageCode, //图片验证码
        image_code_id:imageCodeId  //图片验证码的编号
    }
    // 向后端发送请求
    $.get('/api/v1.0/sms_code/'+mobile, req_data,function (resp) {
        //resp是后端返回的响应值，因为后端返回的是json
        // 所以ajax帮助我们把这个json转换成js对象，resp就是转换后的对象
        if (resp.errno == '0'){   // 发送成功
            var num = 60;
            // 创建一个计时器
            var timer = setInterval(function () {
                if (num>1){
                    // num >1 就表示时间没有结束
                    // 修改倒计时文本
                    $(".phonecode-a").html(num+'秒');
                    num -=1;
                }else {
                    // 时间结束，按钮的文本改为原来的
                    $(".phonecode-a").html('获取验证码');
                    // 重新添加点击按钮
                    $(".phonecode-a").attr("onclick", "sendSMSCode();");
                    // 清除时间计时器
                    clearInterval(timer);

                }
            // 多长时间调用一次  总共多长时间
            },1000,60)
        }else {
            alert(resp.errmsg);
            $(".phonecode-a").attr("onclick", "sendSMSCode();");

    }

    })
}



$(document).ready(function() {
    generateImageCode();
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });


    // 为表单的提交补充自定义的函数行为  （提交事件e）
    $(".form-register").submit(function(e){
        e.preventDefault();  // 阻止浏览器对于表单的默认自动提交行为
        var mobile = $("#mobile").val();
        var phoneCode = $("#phonecode").val();
        var passwd = $("#password").val();
        var passwd2 = $("#password2").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        }
        if (!phoneCode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (passwd != passwd2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }
        // 调用ajax向后端发送请求

        // 向后端发送的数据
        var req_data = {
            mobile : mobile,
            sms_code : phoneCode,
            password : passwd,
            password2 : passwd2,
        };
        // 将数据转换成json格式
        var req_json = JSON.stringify(req_data);
        $.ajax({
            url:'/api/v1.0/users',
            type:'post',
            data:req_json,
            contentType:'application/json;charset=UTF-8',
            dataType:'json',
            headers:{
                'X-CSRFToken': getCookie('csrf_token')
            },// 获取cookie中的csrf_token的值 ，使用上边的方法可以获取
            success:function (resp) {
                if (resp.errno == '0'){
                    // 注册成功。跳转主页面
                    location.href = '/index.html';
                }else {
                    alert(resp.errmsg)
                }
            }
        })


    });
})