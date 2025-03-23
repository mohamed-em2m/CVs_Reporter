# CVs Report Generator 
<img src="https://cdn.thuvienphapluat.vn/uploads/tintuc/2024/01/27/mau-cv.jpg"/>
This repository contains a project that leverages the Agent Gemini API to generate comprehensive survey reports from candidate CVs (in PDF format). The project extracts relevant data, creates insightful charts, and compiles the results into a final PDF report while also saving processed data to CSV format.

---

## Table of Contents

- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Arguments](#command-line-arguments)
  - [Running the Project](#running-the-project)
- [Project Components](#project-components)
- [Logging](#logging)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Repository Structure

```
├── src                      # Source code directory
│   ├── init_agent.py        # Module for initializing the extraction agent
│   ├── main.py              # Main script to process CVs and generate reports
│   ├── pdf_build.py         # Module to compile the PDF report
│   ├── utiles.py            # Utility functions used throughout the project
├── requirements.txt         # List of required Python packages
└── .gitignore               # Git ignore file
```

---

## Getting Started

### Prerequisites

- **Python 3.8+**
- **Gemini API key:** Required for authentication with Agent Gemini.
- **Dependencies:** Listed in `requirements.txt` (e.g., `pandas`, `kaleido`, etc.).

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/your-repository.git
   cd your-repository
   ```

2. **Set up a virtual environment (optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

The project is executed via the command line using `main.py`, which processes the CVs, generates a PDF report, and optionally exports the data to CSV.

### Command-Line Arguments

| Argument     | Description | Default |
|-------------|-------------|---------|
| **path** | Path to the directory containing PDF files (CVs). | Required |
| **--output** | Output PDF report file path. | `csv_report.pdf` |
| **--output_csv** | Output CSV file path for candidate data. | `candidate_data.csv` |
| **--key** | Gemini API key for authentication. | Required |
| **--model** | Model name for Agent Gemini. | `gemini-2.0-flash` |
| **--save_csv** | Flag to save processed data to CSV. | Enabled |

### Running the Project

Execute the main script with the necessary arguments:

```bash
python src/main.py /path/to/cv/directory --key YOUR_GEMINI_API_KEY --output report.pdf --output_csv data.csv --model gemini-2.0-flash --save_csv
```

This command will:

- Process the CVs located in the specified directory.
- Initialize the extraction agent using Agent Gemini.
- Generate a detailed PDF survey report.
- Optionally save the extracted data as a CSV file.

---

## Project Components

### `src/init_agent.py`

- **Purpose:** Contains the `ExtractAgent` class which initializes and interacts with the Agent Gemini API to extract data from CVs.

### `src/pdf_build.py`

- **Purpose:** Provides the `create_survey_report` function that compiles the extracted data and chart images into a final PDF report. This report integrates elements such as the title page (`title_page.pdf`).

### `src/main.py`

- **Purpose:** Orchestrates the data extraction, report generation, and CSV saving processes. It also sets the necessary environment variables for Agent Gemini.

### `src/utiles.py`

- **Purpose:** Contains various utility functions that support the main functionality of the project.

---

## Logging

- The project uses Python's built-in `logging` module for tracking the progress of data processing and report generation.
- Log messages include initialization steps, data processing stages, and confirmation messages for file outputs.

---

## Contributing

Contributions are welcome! If you have ideas for improvements or encounter any issues, please:

1. Open an issue to discuss the changes.
2. Submit a pull request with your proposed updates.

Please follow the existing code style and document your changes thoroughly.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgements

- **Agent Gemini Team:** For providing the API and technical support.
- **Dependency Authors:** For creating and maintaining the libraries used in this project.
- **Community Contributors:** For valuable feedback and contributions to enhance this project.

---

Happy reporting and data exploration!

