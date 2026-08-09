
// ============================================================
// DRIVE WISE DASHBOARD
// ============================================================

document.addEventListener("DOMContentLoaded", () => {

    // ========================================================
    // ELEMENTS
    // ========================================================

    const brandSelect =
        document.getElementById("brandSelect");

    const carSelect =
        document.getElementById("carSelect");

    const questionInput =
        document.getElementById("questionInput");

    const askBtn =
        document.getElementById("askBtn");

    const askButtonText =
        document.getElementById("askButtonText");

    const askSpinner =
        document.getElementById("askSpinner");

    const questionMessage =
        document.getElementById("questionMessage");

    const answerCard =
        document.getElementById("answerCard");

    const answerContent =
        document.getElementById("answerContent");

    const answerVehicle =
        document.getElementById("answerVehicle");

    const characterCount =
        document.getElementById("characterCount");

    const userName =
        document.getElementById("userName");

    const userInitial =
        document.getElementById("userInitial");

    const logoutBtn =
        document.getElementById("logoutBtn");

    const historyList =
        document.getElementById("historyList");

    const refreshHistoryBtn =
        document.getElementById("refreshHistoryBtn");


    // ========================================================
    // CHECK REQUIRED ELEMENTS
    // ========================================================

    if (
        !brandSelect ||
        !carSelect ||
        !questionInput ||
        !askBtn ||
        !answerCard ||
        !answerContent
    ) {

        console.error(
            "Drive Wise: Required dashboard elements are missing."
        );

        return;

    }


    // ========================================================
    // SAFE JSON RESPONSE
    // ========================================================

    async function getJsonResponse(response) {

        const text =
            await response.text();

        if (!text) {

            return {};

        }

        try {

            return JSON.parse(text);

        }

        catch (error) {

            console.error(
                "Invalid JSON response:",
                text
            );

            throw new Error(
                "Server returned an invalid response."
            );

        }

    }


    // ========================================================
    // MESSAGE
    // ========================================================

    function showMessage(
        message,
        type = "error"
    ) {

        if (!questionMessage) {

            return;

        }

        questionMessage.textContent =
            message;

        questionMessage.className =
            `message ${type}`;

    }


    function clearMessage() {

        if (!questionMessage) {

            return;

        }

        questionMessage.textContent =
            "";

        questionMessage.className =
            "message";

    }


    // ========================================================
    // CHECK AUTHENTICATION
    // ========================================================

    async function checkAuthentication() {

        try {

            const response =
                await fetch(
                    "/api/auth/me",
                    {
                        method: "GET",

                        credentials: "include",

                        headers: {
                            "Accept":
                                "application/json"
                        }
                    }
                );


            const data =
                await getJsonResponse(
                    response
                );


            console.log(
                "Current user:",
                data
            );


            if (
                !response.ok ||
                !data.authenticated ||
                !data.user
            ) {

                window.location.href =
                    "/";

                return false;

            }


            const user =
                data.user;


            // ------------------------------------------------
            // USER NAME
            // ------------------------------------------------

            const name =
                user.name ||
                "User";


            if (userName) {

                userName.textContent =
                    name;

            }


            // ------------------------------------------------
            // USER INITIAL
            // ------------------------------------------------

            if (userInitial) {

                userInitial.textContent =
                    name
                        .trim()
                        .charAt(0)
                        .toUpperCase();

            }


            return true;

        }

        catch (error) {

            console.error(
                "Authentication error:",
                error
            );

            window.location.href =
                "/";

            return false;

        }

    }


    // ========================================================
    // LOGOUT
    // ========================================================

    if (logoutBtn) {

        logoutBtn.addEventListener(
            "click",
            async () => {

                logoutBtn.disabled =
                    true;

                logoutBtn.textContent =
                    "Logging out...";


                try {

                    const response =
                        await fetch(
                            "/api/auth/logout",
                            {
                                method: "POST",

                                credentials:
                                    "include",

                                headers: {
                                    "Accept":
                                        "application/json"
                                }
                            }
                        );


                    const data =
                        await getJsonResponse(
                            response
                        );


                    console.log(
                        "Logout:",
                        data
                    );

                }

                catch (error) {

                    console.error(
                        "Logout error:",
                        error
                    );

                }


                window.location.href =
                    "/";

            }
        );

    }


    // ========================================================
    // ASK BUTTON LOADING
    // ========================================================

    function setAskLoading(
        isLoading
    ) {

        askBtn.disabled =
            isLoading;


        if (askButtonText) {

            askButtonText.textContent =
                isLoading
                    ? "Getting answer..."
                    : "Ask Drive Wise";

        }


        if (askSpinner) {

            if (isLoading) {

                askSpinner.classList.remove(
                    "hidden"
                );

            }

            else {

                askSpinner.classList.add(
                    "hidden"
                );

            }

        }

    }


    // ========================================================
    // LOAD BRANDS
    // ========================================================

    async function loadBrands() {

        brandSelect.disabled =
            true;

        brandSelect.innerHTML =
            `
            <option value="">
                Loading brands...
            </option>
            `;


        try {

            const response =
                await fetch(
                    "/api/brands",
                    {
                        method: "GET",

                        credentials:
                            "include",

                        headers: {
                            "Accept":
                                "application/json"
                        }
                    }
                );


            const data =
                await getJsonResponse(
                    response
                );


            console.log(
                "Brands API:",
                data
            );


            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(
                    data.message ||
                    "Unable to load brands."
                );

            }


            brandSelect.innerHTML =
                `
                <option value="">
                    Select Brand
                </option>
                `;


            if (
                !Array.isArray(
                    data.brands
                ) ||
                data.brands.length === 0
            ) {

                brandSelect.innerHTML =
                    `
                    <option value="">
                        No brands available
                    </option>
                    `;

                return;

            }


            data.brands.forEach(
                brand => {

                    const option =
                        document.createElement(
                            "option"
                        );


                    option.value =
                        brand.id;


                    const brandNames = {

                        1: "Mahindra",
                        2: "Hyundai",
                        3: "Kia",
                        4: "Maruti",
                        5: "Tata"

                    };


                    option.textContent =
                        brand.name ||
                        brand.brand_name ||
                        brandNames[brand.id] ||
                        `Brand ${brand.id}`;


                    brandSelect.appendChild(
                        option
                    );

                }
            );


            brandSelect.disabled =
                false;

        }

        catch (error) {

            console.error(
                "Brand loading error:",
                error
            );


            brandSelect.innerHTML =
                `
                <option value="">
                    Unable to load brands
                </option>
                `;


            brandSelect.disabled =
                true;


            showMessage(
                "Unable to load vehicle brands. Please refresh the page.",
                "error"
            );

        }

    }


    // ========================================================
    // LOAD MODELS
    // ========================================================

    async function loadModels(
        brandId
    ) {

        carSelect.disabled =
            true;

        carSelect.innerHTML =
            `
            <option value="">
                Loading models...
            </option>
            `;


        try {

            const response =
                await fetch(
                    `/api/cars/${encodeURIComponent(brandId)}`,
                    {
                        method: "GET",

                        credentials:
                            "include",

                        headers: {
                            "Accept":
                                "application/json"
                        }
                    }
                );


            const data =
                await getJsonResponse(
                    response
                );


            console.log(
                "Models API:",
                data
            );


            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(
                    data.message ||
                    "Unable to load models."
                );

            }


            carSelect.innerHTML =
                `
                <option value="">
                    Select Model
                </option>
                `;


            if (
                !Array.isArray(
                    data.cars
                ) ||
                data.cars.length === 0
            ) {

                carSelect.innerHTML =
                    `
                    <option value="">
                        No models available
                    </option>
                    `;

                carSelect.disabled =
                    true;

                return;

            }


            data.cars.forEach(
                car => {

                    const option =
                        document.createElement(
                            "option"
                        );


                    option.value =
                        car.id;


                    option.textContent =
                        car.model_name ||
                        "Unknown Model";


                    option.dataset.modelCode =
                        car.model_code || "";


                    option.dataset.brochure =
                        car.brochure || "";


                    carSelect.appendChild(
                        option
                    );

                }
            );


            carSelect.disabled =
                false;

        }

        catch (error) {

            console.error(
                "Model loading error:",
                error
            );


            carSelect.innerHTML =
                `
                <option value="">
                    Unable to load models
                </option>
                `;


            carSelect.disabled =
                true;


            showMessage(
                "Unable to load models for this brand.",
                "error"
            );

        }

    }


    // ========================================================
    // BRAND CHANGE
    // ========================================================

    brandSelect.addEventListener(
        "change",
        async () => {

            clearMessage();


            answerCard.classList.add(
                "hidden"
            );


            carSelect.innerHTML =
                `
                <option value="">
                    Select Model
                </option>
                `;


            carSelect.disabled =
                true;


            const brandId =
                brandSelect.value;


            if (!brandId) {

                return;

            }


            await loadModels(
                brandId
            );

        }
    );


    // ========================================================
    // MODEL CHANGE
    // ========================================================

    carSelect.addEventListener(
        "change",
        () => {

            clearMessage();

            answerCard.classList.add(
                "hidden"
            );

        }
    );


    // ========================================================
    // CHARACTER COUNT
    // ========================================================

    questionInput.addEventListener(
        "input",
        () => {

            if (characterCount) {

                characterCount.textContent =
                    `${questionInput.value.length} / 1000`;

            }

        }
    );


    // ========================================================
    // ESCAPE HTML
    // ========================================================

    function escapeHtml(
        value
    ) {

        return String(
            value ?? ""
        )
            .replace(
                /&/g,
                "&amp;"
            )
            .replace(
                /</g,
                "&lt;"
            )
            .replace(
                />/g,
                "&gt;"
            )
            .replace(
                /"/g,
                "&quot;"
            )
            .replace(
                /'/g,
                "&#039;"
            );

    }


    // ========================================================
    // FORMAT ANSWER
    // ========================================================

    function formatAnswer(
        answer
    ) {

        if (!answer) {

            return `
                <p>
                    No answer was returned.
                </p>
            `;

        }


        return escapeHtml(
            answer
        )
            .replace(
                /\r\n/g,
                "\n"
            )
            .replace(
                /\r/g,
                "\n"
            )
            .split(
                /\n{2,}/
            )
            .map(
                paragraph => {

                    return `
                        <p>
                            ${paragraph.replace(
                                /\n/g,
                                "<br>"
                            )}
                        </p>
                    `;

                }
            )
            .join("");

    }


    // ========================================================
    // HISTORY LOADING
    // ========================================================

    function showHistoryLoading() {

        if (!historyList) {

            return;

        }


        historyList.innerHTML =
            `
            <div class="history-loading">
                Loading history...
            </div>
            `;

    }


    // ========================================================
    // EMPTY HISTORY
    // ========================================================

    function showEmptyHistory() {

        if (!historyList) {

            return;

        }


        historyList.innerHTML =
            `
            <div class="history-empty">

                <div class="history-empty-icon">
                    +
                </div>

                <p>
                    No questions yet.
                </p>

                <span>
                    Your previous questions
                    will appear here.
                </span>

            </div>
            `;

    }


    // ========================================================
    // DISPLAY HISTORY
    // ========================================================

    function displayHistory(
        history
    ) {

        if (!historyList) {

            return;

        }


        if (
            !Array.isArray(history) ||
            history.length === 0
        ) {

            showEmptyHistory();

            return;

        }


        historyList.innerHTML =
            "";


        history.forEach(
            item => {

                const historyItem =
                    document.createElement(
                        "button"
                    );


                historyItem.type =
                    "button";


                historyItem.className =
                    "history-item";


                const question =
                    item.question ||
                    "Previous question";


                const brand =
                    item.brand ||
                    "";


                const model =
                    item.model ||
                    "";


                const date =
                    item.created_at ||
                    item.createdAt ||
                    "";


                historyItem.innerHTML =
                    `
                    <div class="history-question">
                        ${escapeHtml(question)}
                    </div>

                    <div class="history-meta">

                        <span>
                            ${escapeHtml(
                                brand
                            )}

                            ${
                                model
                                    ? " · " +
                                      escapeHtml(model)
                                    : ""
                            }
                        </span>

                        ${
                            date
                                ? `
                                <span>
                                    ${escapeHtml(
                                        formatDate(date)
                                    )}
                                </span>
                                `
                                : ""
                        }

                    </div>
                    `;


                historyItem.addEventListener(
                    "click",
                    () => {

                        openHistoryItem(
                            item
                        );

                    }
                );


                historyList.appendChild(
                    historyItem
                );

            }
        );

    }


    // ========================================================
    // FORMAT HISTORY DATE
    // ========================================================

    function formatDate(
        dateValue
    ) {

        if (!dateValue) {

            return "";

        }


        const date =
            new Date(
                dateValue
            );


        if (
            Number.isNaN(
                date.getTime()
            )
        ) {

            return String(
                dateValue
            );

        }


        return date.toLocaleDateString(
            undefined,
            {
                day: "2-digit",
                month: "short",
                year: "numeric"
            }
        );

    }


    // ========================================================
    // LOAD HISTORY FROM DATABASE
    // ========================================================

    async function loadHistory() {

        if (!historyList) {

            return;

        }


        showHistoryLoading();


        try {

            const response =
                await fetch(
                    "/api/history",
                    {
                        method: "GET",

                        credentials:
                            "include",

                        headers: {
                            "Accept":
                                "application/json"
                        }
                    }
                );


            const data =
                await getJsonResponse(
                    response
                );


            console.log(
                "History API:",
                data
            );


            if (
                response.status === 401
            ) {

                window.location.href =
                    "/";

                return;

            }


            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(
                    data.message ||
                    "Unable to load history."
                );

            }


            const history =
                Array.isArray(
                    data.history
                )
                    ? data.history
                    : (
                        Array.isArray(
                            data.data
                        )
                            ? data.data
                            : []
                    );


            displayHistory(
                history
            );

        }

        catch (error) {

            console.error(
                "History loading error:",
                error
            );


            if (historyList) {

                historyList.innerHTML =
                    `
                    <div class="history-error">

                        <p>
                            Unable to load history.
                        </p>

                        <button
                            type="button"
                            id="retryHistoryBtn"
                        >
                            Try again
                        </button>

                    </div>
                    `;


                const retryBtn =
                    document.getElementById(
                        "retryHistoryBtn"
                    );


                if (retryBtn) {

                    retryBtn.addEventListener(
                        "click",
                        loadHistory
                    );

                }

            }

        }

    }


    // ========================================================
    // OPEN HISTORY ITEM
    // ========================================================

    function openHistoryItem(
        item
    ) {

        const brand =
            item.brand ||
            "";


        const model =
            item.model ||
            "";


        const question =
            item.question ||
            "";


        const answer =
            item.answer ||
            item.response ||
            "";


        // ----------------------------------------------------
        // RESTORE BRAND
        // ----------------------------------------------------

        if (brand) {

            const brandOptions =
                Array.from(
                    brandSelect.options
                );


            const matchingBrand =
                brandOptions.find(
                    option =>
                        option.textContent
                            .trim()
                            .toLowerCase() ===
                        brand
                            .trim()
                            .toLowerCase()
                );


            if (matchingBrand) {

                brandSelect.value =
                    matchingBrand.value;


                loadModels(
                    matchingBrand.value
                ).then(
                    () => {

                        const modelOptions =
                            Array.from(
                                carSelect.options
                            );


                        const matchingModel =
                            modelOptions.find(
                                option =>
                                    option.textContent
                                        .trim()
                                        .toLowerCase() ===
                                    model
                                        .trim()
                                        .toLowerCase()
                            );


                        if (matchingModel) {

                            carSelect.value =
                                matchingModel.value;

                        }

                    }
                );

            }

        }


        // ----------------------------------------------------
        // RESTORE QUESTION
        // ----------------------------------------------------

        questionInput.value =
            question;


        if (characterCount) {

            characterCount.textContent =
                `${question.length} / 1000`;

        }


        // ----------------------------------------------------
        // RESTORE ANSWER
        // ----------------------------------------------------

        if (answer) {

            answerContent.innerHTML =
                formatAnswer(
                    answer
                );


            answerVehicle.textContent =
                `${brand}${model ? " · " + model : ""}`;


            answerVehicle.style.display =
                "inline-block";


            answerCard.classList.remove(
                "hidden"
            );


            answerCard.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }

    }


    // ========================================================
    // REFRESH HISTORY
    // ========================================================

    if (refreshHistoryBtn) {

        refreshHistoryBtn.addEventListener(
            "click",
            async () => {

                refreshHistoryBtn.disabled =
                    true;


                await loadHistory();


                refreshHistoryBtn.disabled =
                    false;

            }
        );

    }


    // ========================================================
    // SAVE HISTORY
    // ========================================================

    async function saveHistory(
        brand,
        model,
        question,
        answer
    ) {

        console.log(
            "================================="
        );

        console.log(
            "SAVING HISTORY"
        );

        console.log(
            "Brand:",
            brand
        );

        console.log(
            "Model:",
            model
        );

        console.log(
            "Question:",
            question
        );

        console.log(
            "Answer:",
            answer
        );

        console.log(
            "================================="
        );


        try {

            const response =
                await fetch(
                    "/api/history/save",
                    {
                        method: "POST",

                        credentials:
                            "include",

                        headers: {
                            "Content-Type":
                                "application/json",

                            "Accept":
                                "application/json"
                        },

                        body:
                            JSON.stringify({

                                brand:
                                    brand,

                                model:
                                    model,

                                question:
                                    question,

                                answer:
                                    answer

                            })
                    }
                );


            // ------------------------------------------------
            // READ SERVER RESPONSE
            // ------------------------------------------------

            const data =
                await getJsonResponse(
                    response
                );


            console.log(
                "SAVE HISTORY RESPONSE:",
                data
            );


            // ------------------------------------------------
            // AUTHENTICATION CHECK
            // ------------------------------------------------

            if (
                response.status === 401
            ) {

                console.error(
                    "User is not authenticated."
                );


                window.location.href =
                    "/";


                return false;

            }


            // ------------------------------------------------
            // SAVE FAILED
            // ------------------------------------------------

            if (
                !response.ok ||
                !data.success
            ) {

                console.error(
                    "History save failed:",
                    data
                );


                return false;

            }


            // ------------------------------------------------
            // SAVE SUCCESSFUL
            // ------------------------------------------------

            console.log(
                "History saved successfully."
            );


            // ------------------------------------------------
            // REFRESH HISTORY
            // ------------------------------------------------

            await loadHistory();


            return true;

        }

        catch (error) {

            console.error(
                "SAVE HISTORY ERROR:",
                error
            );


            return false;

        }

    }


    // ========================================================
    // ASK QUESTION
    // ========================================================

    askBtn.addEventListener(
        "click",
        async () => {

            clearMessage();


            // ------------------------------------------------
            // SELECTED BRAND
            // ------------------------------------------------

            const brandOption =
                brandSelect.options[
                    brandSelect.selectedIndex
                ];


            // ------------------------------------------------
            // SELECTED MODEL
            // ------------------------------------------------

            const modelOption =
                carSelect.options[
                    carSelect.selectedIndex
                ];


            // ------------------------------------------------
            // BRAND NAME
            // ------------------------------------------------

            const brand =
                brandOption
                    ? brandOption.textContent.trim()
                    : "";


            // ------------------------------------------------
            // MODEL NAME
            // ------------------------------------------------

            const model =
                modelOption
                    ? modelOption.textContent.trim()
                    : "";


            // ------------------------------------------------
            // QUESTION
            // ------------------------------------------------

            const question =
                questionInput.value.trim();


            // =================================================
            // VALIDATION
            // =================================================

            if (!brandSelect.value) {

                showMessage(
                    "Please select a brand."
                );


                brandSelect.focus();


                return;

            }


            if (!carSelect.value) {

                showMessage(
                    "Please select a model."
                );


                carSelect.focus();


                return;

            }


            if (!question) {

                showMessage(
                    "Please enter a question."
                );


                questionInput.focus();


                return;

            }


            if (question.length < 3) {

                showMessage(
                    "Please enter a little more detail."
                );


                questionInput.focus();


                return;

            }


            // =================================================
            // START RAG REQUEST
            // =================================================

            setAskLoading(
                true
            );


            answerCard.classList.add(
                "hidden"
            );


            try {

                const response =
                    await fetch(
                        "/api/chat/",
                        {
                            method: "POST",

                            credentials:
                                "include",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Accept":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({

                                    brand:
                                        brand,

                                    model:
                                        model,

                                    question:
                                        question

                                })
                        }
                    );


                const data =
                    await getJsonResponse(
                        response
                    );


                console.log(
                    "Chat API:",
                    data
                );


                // ------------------------------------------------
                // AUTHENTICATION CHECK
                // ------------------------------------------------

                if (
                    response.status === 401
                ) {

                    window.location.href =
                        "/";


                    return;

                }


                // ------------------------------------------------
                // CHAT ERROR
                // ------------------------------------------------

                if (
                    !response.ok ||
                    !data.success
                ) {

                    throw new Error(
                        data.error ||
                        data.message ||
                        "Unable to get an answer."
                    );

                }


                // ------------------------------------------------
                // GET ANSWER
                // ------------------------------------------------

                const answer =
                    data.answer ||
                    "No answer was returned.";


                // =================================================
                // DISPLAY ANSWER
                // =================================================

                answerContent.innerHTML =
                    formatAnswer(
                        answer
                    );


                answerVehicle.textContent =
                    `${brand} · ${model}`;


                answerVehicle.style.display =
                    "inline-block";


                answerCard.classList.remove(
                    "hidden"
                );


                showMessage(
                    "Answer generated successfully.",
                    "success"
                );


                // =================================================
                // SAVE QUESTION + ANSWER
                // =================================================

                const historySaved =
                    await saveHistory(
                        brand,
                        model,
                        question,
                        answer
                    );


                if (!historySaved) {

                    console.warn(
                        "The answer was generated, but history could not be saved."
                    );

                }


                // =================================================
                // SCROLL TO ANSWER
                // =================================================

                answerCard.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }

            catch (error) {

                console.error(
                    "Chat error:",
                    error
                );


                showMessage(
                    error.message ||
                    "Unable to get an answer."
                );

            }

            finally {

                setAskLoading(
                    false
                );

            }

        }
    );


    // ========================================================
    // CTRL + ENTER
    // ========================================================

    questionInput.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter" &&
                event.ctrlKey
            ) {

                event.preventDefault();


                askBtn.click();

            }

        }
    );


    // ========================================================
    // INITIALIZE
    // ========================================================

    async function initialize() {

        // ----------------------------------------------------
        // 1. CHECK LOGGED-IN USER
        // ----------------------------------------------------

        const authenticated =
            await checkAuthentication();


        if (!authenticated) {

            return;

        }


        // ----------------------------------------------------
        // 2. LOAD BRANDS
        // ----------------------------------------------------

        await loadBrands();


        // ----------------------------------------------------
        // 3. LOAD PREVIOUS QUESTIONS
        // ----------------------------------------------------

        await loadHistory();

    }


    // ========================================================
    // START DASHBOARD
    // ========================================================

    initialize();

});

