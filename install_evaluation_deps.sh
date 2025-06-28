#!/bin/bash
# Install evaluation dependencies for DocuScribe AI

echo "Installing evaluation dependencies..."

# Install Python packages
pip install nltk rouge-score scikit-learn scipy

# Download NLTK data
python -c "
import nltk
print('Downloading NLTK data...')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
print('NLTK data download complete!')
"

echo "Evaluation dependencies installed successfully!"
echo ""
echo "You can now run evaluations using:"
echo "  python run_evaluation.py --run-sample"
echo "  or use the evaluation features in the Streamlit app"
