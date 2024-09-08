# Backend Setup

## Prerequisites

- Python 3.8 or higher
- pip

## Setting Up the Environment

1. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## FFmpeg Installation

You need to install FFmpeg on your system. Follow these steps:

1. Download FFmpeg from [FFmpeg's official website](https://ffmpeg.org/download.html).
2. Copy `ffmpeg.exe` into the `backend/ffmpeg/` directory.

## Running the Application

To run the FastAPI application, use the following command:

### [fastapi](https://fastapi.tiangolo.com/deployment/manually/)

### • **fastapi run main.py**

### [uvicorn](https://www.uvicorn.org/)

### • **uvicorn main:app --reload**
