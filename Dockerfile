# Use the official Python image as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# copy the requirements file first
COPY ./requirements.txt /app

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Copy the rest of code files into the container
COPY . /app

# Expose the port Streamlit will run on
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "launch_simple.py", "--server.port=8501", "--server.address=0.0.0.0"]