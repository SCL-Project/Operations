import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def read_sent_emails(file_path):
    with open(file_path, 'r') as file:
        sent_emails = json.load(file)
    return sent_emails


def generate_summary(sent_emails):
    df = pd.DataFrame(sent_emails)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Set up seaborn with custom colors
    green_color = (0, 0.407843137, 0.215686275)
    sns.set(style="whitegrid", context="notebook", palette=[green_color])

    # Create subplots
    fig, axes = plt.subplots(nrows=2, figsize=(10, 10))

    # Plotting by subject
    sns.countplot(data=df, x="subject", ax=axes[0], color=green_color)
    axes[0].set_title("Emails sent by subject")
    axes[0].set_xlabel("Subject")
    axes[0].set_ylabel("Count")

    # Plotting by week number
    df['week_number'] = df['timestamp'].dt.isocalendar().week
    sns.countplot(data=df, x="week_number", ax=axes[1], color=green_color)
    axes[1].set_title("Emails sent by week number")
    axes[1].set_xlabel("Week number")
    axes[1].set_ylabel("Count")

    # Rotate x-axis labels for better readability
    for ax in axes:
        for label in ax.get_xticklabels():
            label.set_rotation(45)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    sent_emails = read_sent_emails('sent_emails.json')
    generate_summary(sent_emails)
