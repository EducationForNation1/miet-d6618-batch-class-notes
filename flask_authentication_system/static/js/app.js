const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/;
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

document.querySelectorAll('.toggle-password').forEach((button) => {
  button.addEventListener('click', () => {
    const input = document.getElementById(button.dataset.target);
    if (!input) return;
    input.type = input.type === 'password' ? 'text' : 'password';
    button.textContent = input.type === 'password' ? 'Show' : 'Hide';
  });
});

document.querySelectorAll('[data-confirm]').forEach((button) => {
  button.addEventListener('click', (event) => {
    if (!window.confirm(button.dataset.confirm)) event.preventDefault();
  });
});

const registerForm = document.getElementById('registerForm');
if (registerForm) registerForm.addEventListener('submit', (event) => {
  let ok = true;
  const values = {
    fullName: document.getElementById('fullName').value.trim(),
    username: document.getElementById('username').value.trim(),
    email: document.getElementById('email').value.trim(),
    phone: document.getElementById('phone').value.trim(),
    password: document.getElementById('password').value,
    confirmPassword: document.getElementById('confirmPassword').value,
  };
  ['fullName','username','email','phone','password','confirmPassword'].forEach(id => {
    const el = document.getElementById(id+'Error'); if (el) el.textContent='';
  });
  document.getElementById('termsError').textContent='';
  if (values.fullName.length < 3 || !/^[A-Za-z ]+$/.test(values.fullName)) {document.getElementById('fullNameError').textContent='Enter a valid full name.';ok=false;}
  if (!/^[A-Za-z0-9_]{4,20}$/.test(values.username)) {document.getElementById('usernameError').textContent='Use 4-20 letters, numbers or underscore.';ok=false;}
  if (!emailPattern.test(values.email)) {document.getElementById('emailError').textContent='Enter a valid email.';ok=false;}
  if (!/^[0-9]{10}$/.test(values.phone)) {document.getElementById('phoneError').textContent='Enter a valid 10 digit phone number.';ok=false;}
  if (!passwordPattern.test(values.password)) {document.getElementById('passwordError').textContent='Use 8+ chars with upper, lower, number and special character.';ok=false;}
  if (values.password !== values.confirmPassword) {document.getElementById('confirmPasswordError').textContent='Passwords do not match.';ok=false;}
  if (!document.getElementById('terms').checked) {document.getElementById('termsError').textContent='Please accept the Terms & Conditions.';ok=false;}
  if (!ok) event.preventDefault();
});

const loginForm = document.getElementById('loginForm');
if (loginForm) loginForm.addEventListener('submit', (event) => {
  let ok=true; const identifier=document.getElementById('identifier').value.trim(); const password=document.getElementById('password').value;
  document.getElementById('identifierError').textContent=''; document.getElementById('passwordError').textContent='';
  if(!identifier){document.getElementById('identifierError').textContent='Email or username is required.';ok=false;}
  if(!password){document.getElementById('passwordError').textContent='Password is required.';ok=false;}
  if(!ok) event.preventDefault();
});

const editForm=document.getElementById('editProfileForm');
if(editForm) editForm.addEventListener('submit',(event)=>{
  let ok=true; const name=document.getElementById('fullName').value.trim(), username=document.getElementById('username').value.trim(), email=document.getElementById('email').value.trim(), phone=document.getElementById('phone').value.trim();
  ['fullName','username','email','phone'].forEach(id=>document.getElementById(id+'Error').textContent='');
  if(name.length<3||!/^[A-Za-z ]+$/.test(name)){document.getElementById('fullNameError').textContent='Enter a valid full name.';ok=false;}
  if(!/^[A-Za-z0-9_]{4,20}$/.test(username)){document.getElementById('usernameError').textContent='Use 4-20 letters, numbers or underscore.';ok=false;}
  if(!emailPattern.test(email)){document.getElementById('emailError').textContent='Enter a valid email.';ok=false;}
  if(!/^[0-9]{10}$/.test(phone)){document.getElementById('phoneError').textContent='Enter a valid 10 digit phone number.';ok=false;}
  if(!ok) event.preventDefault();
});

const changeForm=document.getElementById('changePasswordForm');
if(changeForm) changeForm.addEventListener('submit',(event)=>{
  let ok=true; const cur=document.getElementById('currentPassword').value,newp=document.getElementById('newPassword').value,conf=document.getElementById('confirmPassword').value;
  ['currentPassword','newPassword','confirmPassword'].forEach(id=>document.getElementById(id+'Error').textContent='');
  if(!cur){document.getElementById('currentPasswordError').textContent='Current password is required.';ok=false;}
  if(!passwordPattern.test(newp)){document.getElementById('newPasswordError').textContent='Use 8+ chars with upper, lower, number and special character.';ok=false;}
  else if(cur===newp){document.getElementById('newPasswordError').textContent='New password must be different.';ok=false;}
  if(newp!==conf){document.getElementById('confirmPasswordError').textContent='Passwords do not match.';ok=false;}
  if(!ok) event.preventDefault();
});

const forgotForm=document.getElementById('forgotPasswordForm');
if(forgotForm) forgotForm.addEventListener('submit',(event)=>{const email=document.getElementById('forgotEmail').value.trim();document.getElementById('forgotEmailError').textContent='';if(!emailPattern.test(email)){document.getElementById('forgotEmailError').textContent='Enter a valid email address.';event.preventDefault();}});

const resetForm=document.getElementById('resetPasswordForm');
if(resetForm) resetForm.addEventListener('submit',(event)=>{let ok=true;const newp=document.getElementById('newPassword').value,conf=document.getElementById('confirmPassword').value;document.getElementById('newPasswordError').textContent='';document.getElementById('confirmPasswordError').textContent='';if(!passwordPattern.test(newp)){document.getElementById('newPasswordError').textContent='Use 8+ chars with upper, lower, number and special character.';ok=false;}if(newp!==conf){document.getElementById('confirmPasswordError').textContent='Passwords do not match.';ok=false;}if(!ok)event.preventDefault();});
