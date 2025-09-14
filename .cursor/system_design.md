### High-Level System Design

The app's system design can be broken down into three main components: the client-side application, the backend API, and the data storage system. These components work together to collect, process, and monetize user data securely and efficiently.

* **Client-side (iOS and macOS App):** This is the user-facing part of the system. It handles user registration, consent management, scheduling of photo captures, and displaying earnings. The app needs to manage permissions and run a background process to capture photos periodically without constant user interaction.

* **Backend API (Python + FastAPI):** This serves as the central hub for the entire system. It receives data from the client, validates it, and interacts with the database. Key functions include user authentication, managing data collection settings, processing photo uploads, and handling the monetary calculations. FastAPI is an excellent choice for this due to its high performance and built-in data validation capabilities.

* **Data Storage (AWS S3):** This is where the core data—the photos—will be stored. Amazon S3 is ideal for this as it's a highly scalable and durable object storage service, perfect for handling large volumes of unstructured data like images.

***

### Detailed System Components

#### 1. Client-side Application (iOS/macOS)

* **User Interface (UI):** The app's UI will guide users through the registration process, including providing their name, email, age, and an initial photo for profile creation. It will also have a dedicated section for managing data collection settings.
* **Data Collection & Permissions:**
    * The app must explicitly request and receive **camera permissions** from the user. Without this, the app cannot capture photos.
    * It also needs to request permission for **background app refresh** and **notifications** to ensure the periodic photo capture process can run and alert the user.
* **Background Process:**
    * The app will use native iOS/macOS frameworks (like `AVFoundation` for camera access and `BackgroundTasks` for background processing) to schedule and execute photo captures.
    * The user's set frequency (e.g., 29 hours, 4 days) will determine the timing of these tasks.
    * When the scheduled time arrives, the app will either display a local notification prompting the user to open the camera or, if enabled, a discreet background capture will occur.
* **Image Processing & Upload:**
    * Once a photo is captured, the app will compress and process it to reduce file size before uploading.
    * It will then securely upload the image to the backend API, which will handle the final storage in AWS S3.
    * The app should also store a log of successful uploads to track valid contributions for earnings calculation.
* **Earnings Display:** The app will fetch the latest earnings data from the backend API and display it to the user.

***

#### 2. Backend API (Python + FastAPI)

* **API Endpoints:**
    * `/api/v1/auth/register`: Handles new user registration, creating a user profile in the database.
    * `/api/v1/user/settings`: Allows users to update their photo capture frequency and notification preferences.
    * `/api/v1/photos/upload`: The main endpoint for receiving images from the client.
    * `/api/v1/photos/latest_face_id`: An endpoint to get the last known valid face ID for comparison.
    * `/api/v1/earnings`: Retrieves the user's current earnings.
    * `/api/v1/data_stream`: A secure endpoint for authorized third-party companies to purchase or access the data.
* **User Data Management:** The backend will use a database (like PostgreSQL or MongoDB) to store user metadata (name, age, email, etc.) and a unique `user_id`. It will also store the current status of their data collection settings and earnings.
* **Image Processing Pipeline:** When an image is uploaded to `/api/v1/photos/upload`, the backend will:
    1.  **Receive the image:** The FastAPI endpoint will receive the binary image data.
    2.  **Validate the image:** Use an image recognition model (e.g., **Amazon Rekognition** or another similar service) to check for a valid face. This is crucial for determining a "valid" picture. The model should also be used to verify if the face belongs to the registered user to prevent fraud.
    3.  **Store the image:** If the image is valid, it will be uploaded to a designated AWS S3 bucket. The file will be named using a unique identifier, such as `user_id/timestamp.jpg`, for easy organization.
    4.  **Update the database:** The backend will record the valid photo capture in the user's database entry. This record should include the timestamp, the S3 bucket path, and a flag indicating it's a valid, monetizable photo.
* **Earnings Calculation:**
    * A scheduled background task (cron job or similar) on the backend will run weekly.
    * This task will query the database for all valid photos captured by each user in the past week.
    * For each valid photo, it will apply the rate of `$0.05` and update the user's total redeemable earnings. This rate is a configurable parameter in the codebase.

***

#### 3. Data Storage and Monetization

* **AWS S3 Buckets:**
    * **User Data Bucket:** This is where the raw, validated photos will be stored. Each user will have a designated folder within this bucket. The data here is the primary product to be sold.
    * **Metadata Database:** While images are in S3, a relational or NoSQL database will hold the metadata about each image (e.g., S3 path, timestamp, `user_id`, face recognition results). This is essential for querying and filtering the data.
* **Data Marketplace API:**
    * A separate, secure API will be created for third-party companies. This API will not provide direct access to the raw S3 bucket.
    * Instead, it will allow companies to query the metadata database based on specific filters (e.g., "all photos of users aged 25-30 from last month").
    * The API will then provide a secure, temporary link to the corresponding images in the S3 bucket, ensuring data is only accessed by authorized parties.
* **Security and Privacy:**
    * All user-submitted data, especially photos, must be handled with the utmost security. This includes using **end-to-end encryption** for all data transfers.
    * The backend must have robust authentication and authorization mechanisms to prevent unauthorized access.
    * The data sold to third parties should be **anonymized** to protect user privacy. Instead of a direct `user_id`, a unique, anonymized identifier would be used for each data set to prevent individual identification while still allowing for data aggregation and analysis.
    * The app and backend must be compliant with data privacy regulations like GDPR and CCPA. The user's explicit consent is paramount.