function myForm(){
    let name = document.forms['profile'].nm.value;
    let age = document.forms['profile'].age.value;
    let email = document.forms['profile'].email.value;

    document.getElementById('name').innerHTML = name;
    document.getElementById('age').innerHTML = age;
    document.getElementById('email').innerHTML = email;
}