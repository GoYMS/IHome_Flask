function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {


    $('#form-avatar').submit(function (e) {
        // 阻止表单的默认行为
        e.preventDefault();
        // 利用jquery提供的sibmit对表单进行异步提交,也就是提交表单后页面不跳转
        $(this).ajaxSubmit({
            url:'/api/v1.0/users/avatar',
            type:'post',
            dataType:'json',
            contentType:"application/json;charset=UTF-8",
            headers:{
                'X-CSRFTOKEN':getCookie('csrf_token')
            },
            success:function (resp) {
                if(resp.errno == '0'){
                    // 上传成功,获取图片的url
                    var avatarurl = resp.data.avatar_url;
                    $('#user-avatar').attr('src',avatarurl);
                }else if (resp.errno == "4101") {
                    location.href = "/login.html";
                }
                else {
                    alter(resp.errmsg);
                }
            }
        })
    })
    $('#form-name').submit(function (e) {
        // 阻止表单的默认行为
        e.preventDefault();
        // 获取参数
        var name = $('#user-name').val();
        if (!name){
            alert('请填写用户名');
            return;
        }
        // 将数据转换成json格式
        json_data = JSON.stringify({'name':name})
        $.ajax({
            url:'/api/v1.0/user/names',
            type:'PUT',
            dataType:'json',
            data : json_data,
            contentType: 'application/json;charset=UTF-8',
            headers: {
                'X-CSRFTOKEN':getCookie('csrf_token')
            },
            success:function (resp) {
                if (resp.errno=='0'){
                    // 隐藏错误信息
                    $('.error-msg').hide();
                    showSuccessMsg()
                    $('#user-name').val(name);
                }else if ('4001'==data.errno){
                    $('.error-msg').show();
                }else if('4101'== data.errno){
                    location.href = '/login.html'
                }
            }
        })
    })
});

