# 🚗 Drive Wise – Metadata-Aware Automotive RAG Assistant

Drive Wise is an AI-based automotive assistant that helps users get information about cars by asking questions about a specific brand and model.

The main idea of this project is to use **RAG (Retrieval-Augmented Generation)** so that the answers are generated using the relevant car documents instead of depending only on the general knowledge of the AI model.

I developed this project as part of my **Celebal Technologies Excellence Internship Program**.

---

## 📌 What the Project Does

The application allows a user to:

* Login to the application
* Select a car brand
* Select a car model
* Ask questions related to the selected car
* Get an AI-generated answer from the available car documents
* Save the question and answer in the database
* View previous questions in the activity/history section
* Open a previous question and see its corresponding answer

For example:

```text
Brand: Hyundai
Model: Creta

Question:
What is the mileage of the car?

Answer:
[Answer generated using the relevant vehicle document]
```

The question and its answer are stored together in the database.

---

## 🎯 Main Objective

The main objective of Drive Wise is to make searching through vehicle information easier.

Instead of manually going through a car brochure, the user can simply select the car and ask a question.

For example:

```text
Select Brand → Hyundai
Select Model → Creta
Ask → What safety features are available?
```

The system retrieves the relevant information and generates an answer.

---

## 🔄 How the Application Works

The basic flow of the application is:

```text
User Login
    ↓
Select Brand
    ↓
Select Car Model
    ↓
Enter Question
    ↓
RAG Retrieval
    ↓
Find Relevant Vehicle Information
    ↓
Generate Answer
    ↓
Display Answer
    ↓
Save Question + Answer
    ↓
MySQL Database
    ↓
Show in User Activity
```

---

## 🤖 RAG Approach

The project uses **Retrieval-Augmented Generation (RAG)**.

The selected:

```text
Brand
+
Model
+
Question
```

are used to identify the relevant vehicle information.

For example:

```text
Brand  → Hyundai
Model  → Creta
Query  → What is the engine capacity?
```

The system retrieves information related to the Hyundai Creta and then uses that information to generate the final answer.

This helps reduce irrelevant answers from other vehicle documents.

---

## 🚘 Vehicle Selection

The vehicle information is stored in the MySQL database.

The user first selects a brand.

For example:

```text
Hyundai
Kia
Mahindra
Maruti
Tata
```

After selecting a brand, the application loads the models belonging to that brand.

For example:

```text
Hyundai
 ├── Creta
 ├── Exter
 └── Venue
```

This data is loaded dynamically using API calls.

---

## 💬 Question Answering

After selecting the vehicle, the user can ask a question.

Example questions:

```text
What is the mileage?

What is the engine capacity?

What safety features are available?

What are the available variants?
```

The question is sent to the backend through the chat API.

The RAG pipeline retrieves the relevant information and returns the generated answer to the dashboard.

---

## 📝 Question and Answer History

One important feature of the project is the **Your Activity** section.

Whenever a user asks a question and receives an answer, both are saved together.

For example:

| Brand   | Model  | Question                     | Answer                        |
| ------- | ------ | ---------------------------- | ----------------------------- |
| Hyundai | Creta  | What is the mileage?         | The mileage information is... |
| Kia     | Seltos | What is the engine capacity? | The engine capacity is...     |

So the database does not store only the question.

It stores:

```text
Question
+
Corresponding Answer
```

in the same history record.

When the user clicks a previous question, the application loads its saved answer.

---

# 🗄️ MySQL Database

I used **MySQL** for storing the application data.

The database contains tables for different parts of the application.

Main tables include:

```text
users
brands
cars
history
```

### Users

Stores user login and account information.

### Brands

Stores available car brands.

### Cars

Stores car models and their relationship with the selected brand.

### History

Stores the user's previous questions and answers.

A history record contains information such as:

```text
id
user_id
brand
model
question
answer
created_at
```

---

# 🛠️ Technologies Used

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Python
* Flask
* REST APIs

### AI

* Generative AI
* RAG
* Document Retrieval
* Metadata-based Filtering

### Database

* MySQL

### Tools

* VS Code
* Git
* GitHub
* MySQL

---

# 📂 Project Structure

The project is organized into frontend and backend components.

```text
Drive Wise Metadata Aware Automative RAG Assistant/
│
├── backend/
│   ├── api/
│   ├── data/
│   ├── database/
│   ├── generation/
│   ├── ingestion/
│   ├── processed/
│   ├── rag/
│   ├── retrieval/
│   ├── routes/
│   ├── services/
│   ├── test/
│   └── ...
│
├── frontend/
│   ├── css/
│   ├── js/
│   ├── public/
│   ├── api_client.py
│   ├── app.py
│   ├── dashboard.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── requirements.txt
│
├── tests/
│
├── .gitignore
└── README.md
```

The exact structure may vary depending on the final project files.

---

# 🔌 Main APIs

Some of the main APIs used in the application are:

### Authentication

```text
GET /api/auth/me
```

Checks whether the user is logged in.

```text
POST /api/auth/logout
```

Logs the user out.

### Brands

```text
GET /api/brands
```

Loads the available car brands.

### Cars

```text
GET /api/cars/<brand_id>
```

Loads models for the selected brand.

### Chat

```text
POST /api/chat/
```

Sends the selected vehicle and question to the RAG system.

Example:

```json
{
    "brand": "Hyundai",
    "model": "Creta",
    "question": "What is the mileage?"
}
```

### Save History

```text
POST /api/history/save
```

Saves:

```json
{
    "brand": "Hyundai",
    "model": "Creta",
    "question": "What is the mileage?",
    "answer": "The mileage information is..."
}
```

### Get History

```text
GET /api/history
```

Gets the user's previous questions and answers from MySQL.

---

# 🔐 Authentication

The application includes basic user authentication.

The dashboard checks whether the user is logged in before loading the application data.

The application also uses sessions to maintain the logged-in user.

---

# ⚙️ How to Run the Project

## 1. Clone the Repository

```bash
git clone <your-github-repository-url>
```

Go inside the project folder:

```bash
cd "Drive Wise Metadata Aware Automative RAG Assistant"
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

---

## 3. Install Required Libraries

If `requirements.txt` is available:

```bash
pip install -r requirements.txt
```

---

## 4. Configure MySQL

Create a MySQL database for the project.

For example:

```sql
CREATE DATABASE drive_wise;
```

Then configure the database connection in the backend.

---

## 5. Configure Environment Variables

Create a `.env` file for sensitive information such as:

```env
SECRET_KEY=your_secret_key
MYSQL_HOST=localhost
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=drive_wise
```

If an API key is required:

```env
API_KEY=your_api_key
```

Do not upload the `.env` file to GitHub.

---

## 6. Run the Application

Start the Flask backend:

```bash
python app.py
```

Then open the application in the browser:

```text
http://127.0.0.1:5000
```

---

# 📋 Example

A simple example of using the application:

### Step 1

Login to Drive Wise.

### Step 2

Select:

```text
Brand: Hyundai
```

### Step 3

Select:

```text
Model: Creta
```

### Step 4

Ask:

```text
What safety features are available?
```

### Step 5

The RAG system retrieves the relevant information from the vehicle documents.

### Step 6

The generated answer is displayed on the dashboard.

### Step 7

The application saves:

```text
Question:
What safety features are available?

Answer:
[Generated answer]
```

in the MySQL history table.

The question then appears under **Your Activity**.

---

# 🌱 Future Improvements

Some features that can be added in the future are:

* Voice-based questions
* Multi-language support
* Car-to-car comparison
* Better document citations
* Admin dashboard
* Analytics for frequently asked questions
* More vehicle brands and models
* Improved conversational memory
* Mobile-friendly application

---

# 👩‍💻 About the Project

This project was developed by **Arpita Anap** as part of the **Celebal Technologies Excellence Internship Program**.

The project helped me work practically with:

* Python
* Flask
* MySQL
* JavaScript
* REST APIs
* RAG
* Generative AI
* Document retrieval
* Git and GitHub

The main learning from this project was understanding how an AI-based application can be connected with a real database and web interface to create a complete working application.

---

# 📄 License

This project is available under the license included in the repository.
