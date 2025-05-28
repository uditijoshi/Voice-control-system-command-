# Smart Banking System

A modern banking application with QR code scanning, bank account linking, and secure transaction processing.

## Features

- **Secure Authentication**: Password hashing with salt for enhanced security
- **Bank Account Linking**: Connect your real bank accounts to the app
- **QR Code Scanning**: Make payments by scanning QR codes
- **Phone Number Payments**: Send money using phone numbers
- **Transaction History**: View your complete transaction history
- **Real-time Processing**: Multi-threaded transaction processing
- **Admin Panel**: Comprehensive administration tools

## System Requirements

- Windows 10 or later
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- Webcam (for QR code scanning)

## Installation

### Option 1: Executable Installation

1. Download the latest release from the releases page
2. Run the installer and follow the on-screen instructions
3. Launch the application from the desktop shortcut or start menu

### Option 2: From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/smart-banking-system.git

# Navigate to the directory
cd smart-banking-system

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Usage

1. **Login/Register**: Use the login screen to access your account or create a new one
2. **Link Bank Account**: Connect your existing bank accounts for real transfers
3. **Make Payments**: Use QR codes, phone numbers, or direct transfers
4. **View History**: Check your transaction history and account balances

## OS Concepts Implemented

- **Multithreading**: Concurrent transaction processing
- **Synchronization**: Mutex locks and semaphores for thread safety
- **CPU Scheduling**: FIFO, Priority, and Round-Robin scheduling algorithms
- **Transaction Queue Management**: Similar to process queues in OS

## Security Features

- Password hashing with unique salt per user
- Session management with timeouts
- Input validation to prevent SQL injection
- Secure transaction processing

## License

MIT License

## Contact

For support or inquiries, please contact pankajlohani2016@gmail.com
