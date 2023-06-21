from flask import Flask, render_template, request, flash, redirect, url_for
from io import BytesIO

import logging
import os
import pandas as pd
import math
import matplotlib.pyplot as plt
import base64


app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY")

# Configure logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
logger = logging.getLogger("Benford's Law Flask App")


@app.route("/")
def home():
    """Render the home page."""
    logger.info("Home page requested")
    return render_template("index.html")


# Allowed file extensions
ALLOWED_EXTENSIONS = {"csv"}


def allowed_file(filename):
    """Check if the file extension is allowed."""

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["GET", "POST"])
def upload():
    """Upload the CSV file and return the list of columns rendered in the column.html template."""
    logger.info("File upload requested")

    file = request.files["csvfile"]
    selected_delimiter = request.form.get('delimiter')

    # Check if the file is selected
    if file.filename == "":
        flash("Please select a file.", "error")
        logger.error("No file selected")
        return redirect(url_for("home"))

    # Check if the delimiter is selected
    if selected_delimiter == "Select...":
        flash("Please select a delimiter.", "error")
        logger.error("No delimiter selected")
        return redirect(url_for("home"))

    # Check if the file is allowed
    if file and allowed_file(file.filename):
        file.save("uploaded.csv")
        logger.info("File uploaded successfully")

        df = pd.read_csv("uploaded.csv", delimiter=selected_delimiter, engine="python")
        app.config["dataframe"] = df  # Store the dataframe in the app config
        columns = df.columns
        logger.info("Columns: %s", columns)

        logger.info("Column page requested")
        return render_template("column.html", columns=columns)

    flash("Invalid file format. Please select a CSV file.", "error")
    logger.error("Invalid file format")
    return redirect(url_for("home"))


def get_first_digit(number):
    """Return the first digit of the number."""
    return int(str(number)[0])


@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyze the selected column and return the result rendered in the result.html template."""
    logger.info("Analysis requested")

    selected_column = request.form.getlist("selected_column")[0]
    df = app.config.get("dataframe")[selected_column]

    counts = [0] * 9  # List to store the count of each first digit (from 1 to 9)
    total = 0  # Total count of numbers

    for num in df:
        first_digit = get_first_digit(num)  # TODO: Handle errors here
        counts[first_digit - 1] += 1
        total += 1

    # List of observed frequencies
    observed_frequencies = [count / total for count in counts]

    # Expected frequencies based on Benford's Law
    expected_frequencies = [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046]

    # Calculate the d-statistic
    d_statistic = math.sqrt(
        sum((observed - expected) ** 2 for observed, expected in zip(observed_frequencies, expected_frequencies)) / sum(
            expected_frequencies) ** 2)

    # Interpretation thresholds
    small_threshold = 0.01
    moderate_threshold = 0.2

    # Logging analysis details
    logger.info("Selected column: %s", selected_column)
    logger.info("Total numbers: %d", total)
    logger.info("Observed frequencies: %s", observed_frequencies)
    logger.info("D-statistic: %f", d_statistic)

    # Determine the interpretation
    if d_statistic < small_threshold:
        interpretation = "The observed frequencies closely match the expected frequencies based on Benford's Law. " \
                         "This indicates a high level of conformity to Benford's Law."
    elif d_statistic < moderate_threshold:
        interpretation = "The observed frequencies deviate slightly from Benford's Law but still within an " \
                         "acceptable range. It suggests a reasonable level of conformity to Benford's Law " \
                         "with minor discrepancies."
    else:
        interpretation = "The observed frequencies deviate significantly from Benford's Law. It indicates a " \
                         "notable deviation and divergence from the expected frequencies."

    # Calculate the range based on the d-statistic threshold
    range_low = [expected * (1 - moderate_threshold) for expected in expected_frequencies]
    range_high = [expected * (1 + moderate_threshold) for expected in expected_frequencies]

    # Plot the observed and expected frequencies
    digits = list(range(1, 10))
    plt.figure()
    plt.bar(digits, observed_frequencies, color="skyblue", label='Observed')
    plt.plot(digits, expected_frequencies, 'bo-', label='Benford')
    plt.fill_between(digits, range_low, range_high, color='lightcoral', alpha=0.3, label='Acceptable Range')
    plt.xlabel("First Digit")
    plt.ylabel("Frequency (%)")
    plt.title("Expected vs Observed Frequencies")
    plt.legend()
    plt.xlim(0.5, 9.5)  # Remove the 0 value and adjust x-axis limits
    plt.margins(0.05)  # Adjust plot margins

    # Logging interpretation and plot generation
    logger.info("Interpretation: %s", interpretation)
    logger.info("Plot generated.")

    # Convert the plot to bytes
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plot = base64.b64encode(buf.getvalue()).decode("utf-8")

    logger.info("Result page requested")
    return render_template("result.html", plot=plot, d_statistic=d_statistic, interpretation=interpretation)


@app.route("/restart", methods=["GET"])
def restart():
    """Restart the application by redirecting to the home page."""
    logger.info("Restarting the application.")
    return redirect(url_for("home"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
