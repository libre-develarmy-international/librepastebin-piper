# librepastebin-piper
The program reads text from `stdin`, sends it to the Pastebin.com API and prints the created paste link.

A simple command line tool to upload text to Pastebin.

## What it does

- Takes text from your keyboard or a file
- Uploads it to Pastebin.com
- Lets you set options like:
  - How long the paste stays online
  - Who can see it
  - What programming language it is

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/libre-develarmy-international/librepastebin-piper.git
cd librepastebin-piper
```

### 2. Make the compilation script executable
```bash
chmod +x pythonapp-convert-tool.sh
```

### 3. Compile the program
```bash
./pythonapp-convert-tool.sh
```

## Usage Examples

### Basic upload

```bash
echo "Hello world" | librepastebin-piper -k YOUR_API_KEY
```

### Upload a file with syntax highlighting

```bash
cat mycode.py | librepastebin-piper -k YOUR_API_KEY -l python -t "My Code"
```

## Command Line Options

| Option | Description | Required |
|--------|-------------|----------|
| `-k YOUR_API_KEY` | Pastebin API key | Yes |
| `-t "Title"` | Title for your paste | No |
| `-l python` | Programming language for syntax highlighting | No |
| `-e 1D` | Expiration time (10M, 1H, 1D, 1W etc.) | No |
| `-v private` | Visibility: public, unlisted or private | No |

## Help

Show all options:

```bash
librepastebin-piper -h
```
