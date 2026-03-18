# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install uv
RUN pip install uv

# Set the working directory in the container
WORKDIR /app

# Copy only necessary files for building and testing
COPY pyproject.toml uv.lock Makefile /app/
COPY src/ /app/src/
COPY test/ /app/test/
COPY .git /app/.git

# Set PYTHONPATH before installing/running
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y make libatomic1 git

# Install dependencies and run checks
RUN make install && \
    make lint && \
    make check && \
    make quality && \
    make test-unit

# Create non-root user with UID 1000 and GID 1000
RUN groupadd -r -g 1000 appgroup && useradd -r -u 1000 -g appgroup appuser

RUN mkdir -p /home/appuser/.cache && chown appuser:appgroup /home/appuser/.cache

# Set ownership of application directory
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER 1000:1000

# Make port 8001 available to the world outside this container
EXPOSE 8001

# Run app via the template Makefile target (which itself uses uv)
CMD ["make", "run"]