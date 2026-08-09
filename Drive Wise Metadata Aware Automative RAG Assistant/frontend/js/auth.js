// ============================================================
// DRIVE WISE - AUTHENTICATION
// ============================================================


// ============================================================
// HELPER: SHOW MESSAGE
// ============================================================

function showAuthMessage(element, text, type) {

    if (!element) {
        return;
    }

    element.textContent = text;
    element.className = `message ${type}`;

}


// ============================================================
// HELPER: READ API RESPONSE
// ============================================================

async function readApiResponse(response) {

    const contentType =
        response.headers.get("content-type") || "";

    // --------------------------------------------------------
    // JSON RESPONSE
    // --------------------------------------------------------

    if (contentType.includes("application/json")) {

        return await response.json();

    }


    // --------------------------------------------------------
    // NON-JSON RESPONSE
    // --------------------------------------------------------

    const text =
        await response.text();

    console.error(
        "Server returned non-JSON response:",
        text
    );


    throw new Error(
        `Server returned an unexpected response (${response.status}).`
    );

}


// ============================================================
// REGISTER
// ============================================================

const registerForm =
    document.getElementById("registerForm");


if (registerForm) {

    registerForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            // ------------------------------------------------
            // GET FORM VALUES
            // ------------------------------------------------

            const name =
                document.getElementById("name")
                    ?.value
                    .trim() || "";


            const email =
                document.getElementById("email")
                    ?.value
                    .trim() || "";


            const password =
                document.getElementById("password")
                    ?.value || "";


            const confirmPassword =
                document.getElementById("confirmPassword")
                    ?.value || "";


            const message =
                document.getElementById(
                    "registerMessage"
                );


            showAuthMessage(
                message,
                "",
                ""
            );


            // ------------------------------------------------
            // VALIDATION
            // ------------------------------------------------

            if (!name) {

                showAuthMessage(
                    message,
                    "Please enter your name.",
                    "error"
                );

                return;

            }


            if (!email) {

                showAuthMessage(
                    message,
                    "Please enter your email.",
                    "error"
                );

                return;

            }


            if (password.length < 6) {

                showAuthMessage(
                    message,
                    "Password must contain at least 6 characters.",
                    "error"
                );

                return;

            }


            if (password !== confirmPassword) {

                showAuthMessage(
                    message,
                    "Passwords do not match.",
                    "error"
                );

                return;

            }


            // ------------------------------------------------
            // DISABLE BUTTON
            // ------------------------------------------------

            const registerButton =
                document.getElementById(
                    "registerButton"
                );


            if (registerButton) {

                registerButton.disabled = true;

                registerButton.textContent =
                    "Creating account...";

            }


            // ------------------------------------------------
            // SEND REQUEST
            // ------------------------------------------------

            try {

                const response =
                    await fetch(
                        "/api/auth/register",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Accept":
                                    "application/json"
                            },

                            credentials:
                                "include",

                            body:
                                JSON.stringify({
                                    name: name,
                                    email: email,
                                    password: password
                                })
                        }
                    );


                const data =
                    await readApiResponse(
                        response
                    );


                console.log(
                    "Register API:",
                    data
                );


                // ------------------------------------------------
                // SUCCESS
                // ------------------------------------------------

                if (
                    response.ok &&
                    data.success
                ) {

                    showAuthMessage(
                        message,
                        "Registration successful! Redirecting...",
                        "success"
                    );


                    setTimeout(
                        function () {

                            window.location.href =
                                "/";

                        },
                        1200
                    );


                    return;

                }


                // ------------------------------------------------
                // ERROR
                // ------------------------------------------------

                showAuthMessage(
                    message,
                    data.message ||
                    "Registration failed.",
                    "error"
                );


            } catch (error) {

                console.error(
                    "Registration error:",
                    error
                );


                showAuthMessage(
                    message,
                    error.message ||
                    "Unable to connect to server.",
                    "error"
                );


            } finally {

                if (registerButton) {

                    registerButton.disabled =
                        false;

                    registerButton.textContent =
                        "Create account";

                }

            }

        }
    );

}


// ============================================================
// LOGIN
// ============================================================

const loginForm =
    document.getElementById("loginForm");


if (loginForm) {

    loginForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            // ------------------------------------------------
            // GET FORM VALUES
            // ------------------------------------------------

            const email =
                document.getElementById("email")
                    ?.value
                    .trim() || "";


            const password =
                document.getElementById("password")
                    ?.value || "";


            const message =
                document.getElementById(
                    "loginMessage"
                );


            showAuthMessage(
                message,
                "",
                ""
            );


            // ------------------------------------------------
            // VALIDATION
            // ------------------------------------------------

            if (!email) {

                showAuthMessage(
                    message,
                    "Please enter your email.",
                    "error"
                );

                return;

            }


            if (!password) {

                showAuthMessage(
                    message,
                    "Please enter your password.",
                    "error"
                );

                return;

            }


            // ------------------------------------------------
            // DISABLE LOGIN BUTTON
            // ------------------------------------------------

            const loginButton =
                document.getElementById(
                    "loginButton"
                );


            if (loginButton) {

                loginButton.disabled =
                    true;

                loginButton.textContent =
                    "Signing in...";

            }


            // ------------------------------------------------
            // SEND LOGIN REQUEST
            // ------------------------------------------------

            try {

                console.log(
                    "Sending login request..."
                );


                const response =
                    await fetch(
                        "/api/auth/login",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Accept":
                                    "application/json"
                            },

                            credentials:
                                "include",

                            body:
                                JSON.stringify({
                                    email: email,
                                    password: password
                                })
                        }
                    );


                console.log(
                    "Login HTTP status:",
                    response.status
                );


                const data =
                    await readApiResponse(
                        response
                    );


                console.log(
                    "Login API:",
                    data
                );


                // ------------------------------------------------
                // SUCCESS
                // ------------------------------------------------

                if (
                    response.ok &&
                    data.success
                ) {

                    showAuthMessage(
                        message,
                        "Login successful!",
                        "success"
                    );


                    setTimeout(
                        function () {

                            window.location.href =
                                "/dashboard";

                        },
                        500
                    );


                    return;

                }


                // ------------------------------------------------
                // LOGIN FAILED
                // ------------------------------------------------

                showAuthMessage(
                    message,
                    data.message ||
                    "Invalid email or password.",
                    "error"
                );


            } catch (error) {

                console.error(
                    "Login error:",
                    error
                );


                showAuthMessage(
                    message,
                    error.message ||
                    "Unable to connect to server.",
                    "error"
                );


            } finally {

                if (loginButton) {

                    loginButton.disabled =
                        false;

                    loginButton.textContent =
                        "Sign in";

                }

            }

        }
    );

}