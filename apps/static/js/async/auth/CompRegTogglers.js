document.getElementById('togglePassword').addEventListener('click', function () {
    const passwordInput = document.getElementById('password');
    const eyeIcon = document.getElementById('eyeIcon');
    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        eyeIcon.setAttribute("stroke", "green");
    } else {
        passwordInput.type = "password";
        eyeIcon.setAttribute("stroke", "gray");
    }
});

document.getElementById('toggleConfirmPassword').addEventListener('click', function () {
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const eyeIconConfirm = document.getElementById('eyeIconConfirm');
    if (confirmPasswordInput.type === "password") {
        confirmPasswordInput.type = "text";
        eyeIconConfirm.setAttribute("stroke", "green");
    } else {
        confirmPasswordInput.type = "password";
        eyeIconConfirm.setAttribute("stroke", "gray");
    }
});