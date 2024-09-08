# Contributing to YouTubeFlex

Thank you for considering contributing to YouTube Flex! We welcome all kinds of contributions, including bug fixes, feature enhancements, and documentation improvements.

## Getting Started

### Prerequisites

Ensure you have the following installed:

- Python (v3.8 or higher)
- pip (v20 or higher)
- FFmpeg (installed and accessible in your system's PATH)

### Installation

1. **Clone the repository**:

   ```sh
   git clone https://github.com/imadselka/yt_dw.git
   cd yt-dw
   ```

2. **Set up a virtual environment**:

   ```sh
   python -m venv venv
   ```

3. **Activate the virtual environment**:

   - On Windows:
     ```sh
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     source venv/bin/activate
     ```

4. **Install dependencies**:

   ```sh
   pip install -r requirements.txt
   ```

5. **Run the application**:

   ```sh
   uvicorn main:app --reload
   ```

6. **Open the application**:
   Open your browser and navigate to `http://localhost:8000`.

## Code Structure

- **app**: Contains the FastAPI application and routes.
- **models**: Contains data models and schemas.
- **utils**: Contains utility functions for video processing and downloading.

## Making Changes

### Fixing Errors

1. **Identify the error**: Check the console or logs for error messages.
2. **Locate the source**: Use the error message to find the relevant code.
3. **Fix the error**: Make the necessary changes to resolve the issue.
4. **Test your changes**: Ensure that your changes fix the error without introducing new issues.

### Refactoring Code

1. **Identify code to refactor**: Look for code that is difficult to read, maintain, or extend.
2. **Plan your refactor**: Determine how you will improve the code.
3. **Make the changes**: Refactor the code in small, incremental steps.
4. **Test your changes**: Ensure that your refactored code works as expected.

### Submitting Changes

1. **Create a new branch**:

   ```sh
   git checkout -b your-branch-name
   ```

2. **Commit your changes**:

   ```sh
   git add .
   git commit -m "Description of your changes"
   ```

3. **Push your branch**:

   ```sh
   git push origin your-branch-name
   ```

4. **Create a Pull Request**: Go to the repository on GitHub and create a pull request from your branch.

## Code Style

- Follow the existing code style and conventions.
- Use meaningful variable and function names.
- Write comments to explain complex logic.

## Testing

- Ensure that all existing tests pass.
- Write new tests for any new functionality.
- Run tests using:
  ```sh
  pytest
  ```

## Documentation

- Update the README.md file if your changes affect the usage or setup of the project.
- Add comments to your code where necessary.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to YouTubeFlex!
