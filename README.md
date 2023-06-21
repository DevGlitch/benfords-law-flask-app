# Benford's Law Analysis - Flask App

Welcome to the Benford's Law Analysis web application! This Flask application is designed to validate Benford's Law 
using user-submitted flat files and analyze the distribution of leading digits in a target column. 
It provides the d-statistic result, interpretation of this result, and a graph that compares the observed 
distribution with the expected distribution according to Benford's Law.

## Installation

To run the Benford's Law Validator locally, follow these steps:

1. Clone the repository:
```
git clone https://github.com/DevGlitch/benfords-law-flask-app.git
```
2. Change into the app directory:
```
cd benfords-law-flask-app
```
3. Install the dependencies:
```
pip install -r requirements.txt
```

## Usage

Change into the app directory:
```
cd app
```

To run the application, run the following command:
```
python views.py
```

Access the application in your web browser at http://localhost:5000.

## Docker Support

The repository includes a Dockerfile for easy containerization and deployment of the application.
To use Docker, follow these steps:
- Build the Docker image:
```
docker build -t benfords-law .
```

- Run the Docker container:
```
docker run -p 5000:5000 benfords-law
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
