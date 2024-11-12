# BizScan - Smart Business Card Scanner 📇

BizScan is an intelligent business card management system that transforms physical business cards into organized digital contacts. Using advanced OCR technology, it streamlines the process of networking and contact management for professionals.

![BizScan Demo](demo.gif) 

## Features ✨

- **Instant Card Scanning**: Upload and digitize business cards with advanced OCR
- **Smart Information Extraction**: Automatically extracts contact details from cards
- **Contact Management**: Easy-to-use interface for managing digital contacts
- **Powerful Search**: Quickly find contacts in your database
- **Data Visualization**: See detected text regions on scanned cards
- **Edit & Update**: Modify contact information as needed

## Technology Stack 🛠️

- Python
- Streamlit
- EasyOCR
- OpenCV
- PostgreSQL
- Pandas
- Matplotlib

## Installation 🚀

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bizscan.git
cd bizscan
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database and create a `.env` file:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=business_cards
DB_USER=postgres
DB_PASSWORD=postgres
```

5. Run the application:
```bash
streamlit run business_card_scanner.py
```

## Usage 📱

1. **Upload Business Card**:
   - Click on 'Scan Card' tab
   - Upload a business card image (PNG, JPG, JPEG)

2. **Review & Edit**:
   - Verify extracted information
   - Make any necessary corrections
   - Save the contact

3. **Manage Contacts**:
   - View all contacts in the 'View & Manage Contacts' tab
   - Search for specific contacts
   - Edit or delete existing contacts

## Database Setup 💾

1. Create PostgreSQL database:
```sql
CREATE DATABASE business_cards;
```

2. The application will automatically create necessary tables on first run.

## Contributing 🤝

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- EasyOCR for providing the OCR functionality
- Streamlit for the amazing web framework
- OpenCV community for image processing tools

## Contact 📧

Pratik Paudel - [prateekpaudel2017@gmail.com](mailto:prateekpaudel2017@gmail.com)

Project Link: [https://github.com/pratikpaudel/bizscan](https://github.com/pratikpaudel/bizscan)
