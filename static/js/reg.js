 //头像预览
    $("#avatar_file").change(function () {
     var ele_file=$(this)[0].files[0];
     var reader=new FileReader();
     reader.readAsDataURL(ele_file);
     reader.onload=function () {
         $("#avatar_img")[0].src=this.result
     }
    });

      // ajax实现注册
    $("#regBtn").click(function () {
        var form_data=new FormData();
        form_data.append("username",$("#id_username").val());
        form_data.append("password",$("#id_password").val());
        form_data.append("reg_pwd",$("#id_reg_pwd").val());
        form_data.append("email",$("#id_email").val());
        form_data.append("avatar",$("#avatar_file")[0].files[0]);
        form_data.append("csrfmiddlewaretoken",$("[name='csrfmiddlewaretoken']").val());
        console.log("hello");
        $.ajax({
            url:"/reg/",
            type:"POST",
            data:form_data,
            contentType:false,
            processData:false,
            //headers:{"X-CSRFToken":$.cookie('csrftoken')},
            success:function (data) {
                 console.log(data);
                var response=JSON.parse(data);
                if(response.user){
                    location.href="/login/"
                }else{
                   console.log(response.error_msg);
                   $.each(response.error_msg,function(i,j){
                     console.log(i,j) ;
                     $span=$("<span>") ;
                     $span.addClass("pull-right").css("color","red");
                     $span.html(j[0]);
                     $("#id_"+i).after($span).parent().addClass("has-error");
                       if (i=="__all__"){
                         $("#id_reg_pwd").after($span)
                       }
                   })
                }
            },
            error: function (jqXHR, textStatus, err) {

                        // jqXHR: jQuery增强的xhr
                        // textStatus: 请求完成状态
                        // err: 底层通过throw抛出的异常对象，值与错误类型有关
                        console.log(arguments);
                    }
        })
    });