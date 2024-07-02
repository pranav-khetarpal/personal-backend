# # Use the official image as a parent image
# FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# # Set the working directory
# WORKDIR /app

# # Copy the current directory contents into the container at /app
# COPY . /app

# # Install any needed packages specified in requirements.txt
# RUN pip install -r requirements.txt

# # Make port 80 available to the world outside this container
# EXPOSE 8080

# # Define environment variable
# ENV PORT=8080

# # Run app.py when the container launches
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]



# Use the official image as a parent image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy the Firebase service account key into the Docker image
COPY personal-app-fe948-firebase-adminsdk-jvbsy-8eff7c57ff.json /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port defined by Cloud Run (8080 by default)
EXPOSE 8080

# Define environment variable for the Firebase credentials
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/personal-app-fe948-firebase-adminsdk-jvbsy-8eff7c57ff.json"

# Run uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
