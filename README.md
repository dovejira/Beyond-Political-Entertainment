# Beyond-Political-Entertainment

Welcome to the code repository for our research paper: Beyond political entertainment: How travel videos shape foreign attitude toward China. The repository contains two main parts, written in Python and R, each developed by different authors to address specific aspects of our study.

## Repository Structure

### Python Code
The Python scripts were developed by one of the authors and primarily demonstrate the core processes for data acquisition and natural language processing (NLP). Key features of this part include:

- **Flexible Acceleration Options:** We utilized CUDA-enabled PyTorch for GPU acceleration on servers and MPS-enabled PyTorch for local analysis on macOS devices. You can switch between these options based on your system configuration.
- **Model Integration:** The models used in this part can be loaded directly online via HuggingFace or downloaded for local use.

### R Code
The R scripts, developed by another author, focus on the causal inference analysis of the data. This part includes:

- **Statistical Analysis:** Robust methods for causal inference.
- **Setup Requirements:** Ensure that necessary paths are configured and essential libraries are installed before use.

## Getting Started

### Python Code
1. **Environment Setup:** Install the required Python libraries.
2. **Hardware Configuration:** Depending on your hardware, select either the CUDA or MPS version of PyTorch.
3. **Model Access:** Load models via HuggingFace online or download them locally for offline use.

### R Code
1. **Environment Setup:** Install the required R packages as listed in the scripts.
2. **Path Configuration:** Update the file paths in the R scripts to match your local environment.
3. **Run Analysis:** Execute the scripts to perform statistical and causal inference analysis.

## Feedback and Contribution
We welcome your use and feedback to improve this repository. If you encounter any issues or have suggestions, feel free to open an issue or submit a pull request.

---

Thank you for your interest in our research!
