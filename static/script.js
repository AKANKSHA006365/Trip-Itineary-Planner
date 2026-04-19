document.getElementById("loginForm").addEventListener("submit", function(event) {

    event.preventDefault(); // stop form reload

    let name = document.getElementById("name").value.trim();
    let email = document.getElementById("email").value.trim();
    let password = document.getElementById("password").value.trim();

    let emailPattern = /^[^ ]+@[^ ]+\.[a-z]{2,3}$/;

    // Empty check
    if (name === "" || email === "" || password === "") {
        alert("All fields are required!");
        return;
    }

    // Email check
    if (!email.match(emailPattern)) {
        alert("Enter a valid email!");
        return;
    }

    // Password check
    if (password.length < 6) {
        alert("Password must be at least 6 characters!");
        return;
    }

    // Success
    alert("Login Successful!");

    //  Redirect
    window.location.href = "/planner";
});
