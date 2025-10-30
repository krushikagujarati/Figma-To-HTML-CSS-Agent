# Figma to HTML/CSS Converter

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment (.env)

Create a `.env` file in the project root with:

```
FIGMA_ACCESS_TOKEN=your_token_here
FIGMA_FILE_KEY=your_file_key_here
```

How to find them:
- FIGMA_ACCESS_TOKEN: Figma → Settings → Account → Personal access tokens → Create new token.
- FIGMA_FILE_KEY: From the Figma file URL, the part after `/file/` or `/design/`, for example: `https://www.figma.com/design/FILE_KEY/...`.

## Usage

Run the converter:

```bash
python figma_converter.py
```
