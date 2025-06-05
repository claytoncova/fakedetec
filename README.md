# 🕵️‍♂️ FakeDetec - Image Forensics Analysis Tool

## 📝 Description
FakeDetec is a powerful command-line tool for detecting image manipulation and AI-generated content. It analyzes both image data and metadata to identify potential signs of tampering, editing, or artificial generation.

## ✨ Features
- 🔍 Metadata analysis (EXIF data, creation tools, timestamps)
- 🎨 Image manipulation detection
- 🤖 AI-generated content detection
- 📊 Error Level Analysis (ELA)
- 🎯 Copy-move detection
- 📈 Noise pattern analysis
- 🎨 Color histogram analysis
- 📝 Detailed report generation
- 🎨 Colored console output with ASCII art

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fakedetec.git
cd fakedetec
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

Basic usage:
```bash
python main.py analyze path/to/image.jpg
```

Analyze multiple images:
```bash
python main.py analyze path/to/directory
```

Get detailed help:
```bash
python main.py --help
```

## 📊 Output
The analysis results are saved in the `output` directory, including:
- Detailed analysis reports
- Visual markers of detected manipulations
- Statistical data
- Metadata analysis

## 🛠️ Technical Details
The tool uses various techniques for detection:
- Error Level Analysis (ELA)
- EXIF metadata analysis
- Noise pattern analysis
- Color histogram analysis
- Copy-move detection
- AI generation artifacts detection

## 📚 Dependencies
- Pillow: Image processing
- OpenCV: Computer vision operations
- scikit-image: Advanced image processing
- numpy: Numerical operations
- exif: Metadata extraction
- colorama & rich: Terminal formatting
- pywavelets: Wavelet analysis
- matplotlib: Visualization

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer
This tool is for educational and research purposes. Results should be verified by human experts for critical applications. 