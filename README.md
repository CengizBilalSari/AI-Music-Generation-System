# AI Music Generation System

A unified code for generating music using both local large language models (MusicGen) and cloud-based APIs (Suno). This system allows for high-quality music creation from text prompts, style comparison, and local processing.

##  Features

- **Local Generation**: Use Meta's **MusicGen** (via  Transformers) to generate music directly on your hardware (CPU or GPU).
- **Cloud API**: Integration with **Suno AI** for state-of-the-art music and vocal generation.
- **Prompt Testing**: Compare results from different prompts and models in one place.
- **Extensible Architecture**: Modular structure for adding new models or APIs.

##  Project Structure

```bash
AI-Music-Generation-System/
├── MusicGenLocal/          # Local MusicGen implementation
│   ├── musicgen_generate.py # Core generation script
│   ├── musicgen_utils.py    # Configuration and utilities
│   └── generated_music/    # Default output for local tracks
├── SunoAPI/                # Suno AI API integration
│   ├── suno_generate.py    # API interaction and polling
│   ├── suno_utils.py       # API configuration and headers
│   └── example_audios/     # Downloaded/saved audio files
├── MusicGenerationSunoAndMusicGen/ # Comparison and testing
│   └── prompt_test.py      # Script to test prompts across systems
├── requirements.txt        # Project dependencies
└── .env                    # Environment variables (API keys)
```

## 🛠️ Getting Started

### Prerequisites

- Python 3.10+
- (Optional) NVIDIA GPU with CUDA for faster local generation.

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/CengizBilalSari/AI-Music-Generation-System.git
   cd AI-Music-Generation-System
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file in the root directory to store your API keys:

```env
SUNO_API_KEY=your_suno_api_key_here
```

##  Usage

### Local MusicGen
To generate music using the local model:
```bash
python MusicGenLocal/musicgen_generate.py
```
*Note: The first run will download the model weights (approx. several GBs depending on the chosen size).*

### Suno API
To generate music using the Suno Cloud API:
```bash
python SunoAPI/suno_generate.py
```

### Prompt Comparison
To run tests across different settings or models:
```bash
python MusicGenerationSunoAndMusicGen/prompt_test.py
```

## Results & Output

- **Local tracks** are saved in `MusicGenLocal/generated_music/` as `.wav` files.
- **Suno results** provide an `audioUrl` and are logged in `SunoAPI/results.json`.
- **Comparison data** is saved in `MusicGenerationSunoAndMusicGen/prompt_comparison.json`.

