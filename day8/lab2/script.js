function formValidation(){
   let emailId = document.forms['loginForm'].email.value;
   let pwd = document.forms['loginForm'].pwd.value;

//    if(emailId == ""){
//     alert("Email ID Can't be empty")
//    }else if(pwd == ""){
//     alert("Password can't be empty")
//    }else{
//     alert("Success!")
//    }

if(emailId == "" ){
    document.getElementById("pwd_error").innerText ="";
    document.getElementById("email_error").innerText = "Email ID Can't be empty";
}else if(pwd == ""){
    document.getElementById("email_error").innerText="";
    document.getElementById("pwd_error").innerText = "Password can't be empty";
}else{
    document.getElementById("email_error").innerText="";
    document.getElementById("pwd_error").innerText ="";
    alert("Success!")
}

}