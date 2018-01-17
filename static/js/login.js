$("#bbt").click(function () {
        $.ajax({
            url:"/login/",
            type:"POST",
            data:{
                username:$("#username").val(),
                password:$("#password").val(),
                csrfmiddlewaretoken:$("[name='csrfmiddlewaretoken']").val(),
                validCode:$("#validCode").val()
            },
            success:function (data) {
                var response=JSON.parse(data);
                console.log(response);
                console.log("error");
                if (response["is_login"]){
                   location.href="/index/"
                }
                else{$("#error").html(response["error_msg"]).css("color","red")}
            }
        });
    });
    $("#validCode_img").click(function () {
        $(this)[0].src+="?"
    });