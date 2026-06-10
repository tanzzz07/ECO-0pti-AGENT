FROM python:3.11

# Set up the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY ./backened/requirement.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app

# Expose port 7860 which is required by Hugging Face Spaces
EXPOSE 7860

# Set working directory to backened where main.py is
WORKDIR /app/backened

# Start the application
CMD ["python", "main.py"]
