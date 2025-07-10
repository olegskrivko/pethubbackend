# pethubbackend

This is the backend service for the PetHub app — a platform to help find lost and found pets.

## Features

- REST API for managing pet records, users, and reports using Django REST Framework (DRF)  
- Supports custom-built push notifications for nearby lost pets  
- User authentication and role-based access control  
- Integrated guides and tips for pet owners  
- Listings of local animal shelters and contact information  
- Built-in Django admin interface for easy management of data  
- Data validation and error handling for reliable operations  
- Open source and community-driven, welcoming contributions 

## Getting Started

### Requirements

- Python 3.x  
- Django  
- Other dependencies (list them in `requirements.txt`)  

### Installation

1. Clone the repository:

```bash
  git clone https://github.com/olegskrivko/pethubbackend.git
  cd pethubbackend

2. Create a virtual environment and activate it:

```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:

```bash
  pip install -r requirements.txt

4. Configure environment variables (e.g., database, secret keys).

5. Run migrations:

```bash
  python manage.py migrate

6. Start the server:

```bash
  python manage.py runserver

## Features Usage
The backend exposes REST endpoints for pet data management.
For API details, see the documentation (if available) or contact the maintainer.

## Contributing
This project is open source and welcomes contributions! Please open issues or submit pull requests.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Author
Olegs Krivko
https://lunori.app
