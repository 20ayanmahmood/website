FROM python:3.9-slim
ENV CHROMA_TELEMETRY FALSE

# Set working directory
WORKDIR /app

# Copy dependency file first to leverage Docker cache
COPY req.txt .

# Install dependencies
RUN pip install -r req.txt

# Copy the rest of the application code
COPY . .

# Command to run the application
CMD ["uvicorn", "API:app", "--host", "0.0.0.0", "--port", "8000"]
