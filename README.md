# DocAI

DocAI is a Flask-based web application designed for Breast Cancer Diagnosis Management. It allows users to upload ultrasound images of breast conditions for analysis, utilizing a deep learning model to predict whether the condition is benign, malignant, or normal. The application also supports patient registration, login, and contact functionalities to enhance user interaction and data management.

## Features

- User Authentication (Register, Login, Logout)
- Ultrasound Image Upload for Breast Condition Analysis
- Patient Information Management
- History of Uploaded Images and Diagnosis Results

## Installation

To set up DocAI on your local machine, follow these steps:

1. Clone the repository to your local machine:
   ```sh
   git clone https://github.com/sweerasingha/DocAI.git

2. Navigate to the project directory:
    ```sh
    cd DocoAI

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt

4. Set up your MySQL database and update the app.config settings in the project to match your database configuration.

5. Run the Flask application:
    ```sh
    python app.py

## Usage

After starting the application, you can access it by navigating to http://127.0.0.1:5000/ in your web browser. From there, you can:

- Register as a new user
- Log in with your credentials
- Access the prediction page to upload an ultrasound image for diagnosis
- View your upload history and diagnosis results

## Screenshots

![image02](/screenshots/image02.png)
![image01](/screenshots/image01.png)
![image03](/screenshots/image03.png)
![image04](/screenshots/image04.png)


## Contributing

We welcome contributions to DocAI! If you have suggestions for improvements or bug fixes, please feel free to make a pull request or open an issue.

## License

MIT License