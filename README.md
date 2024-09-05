# DraftKings Contest Finder Agent

This project is an autonomous system designed to identify and notify users of potentially advantageous contest opportunities on the DraftKings platform.

## Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd draftkings_agent
   ```

2. Create and activate a Conda environment:
   ```
   conda create -n draftkings_agent python=3.11
   conda activate draftkings_agent
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install Playwright browsers:
   ```
   playwright install
   ```

5. Set up environment variables:
   Create a `.env.local` file in the root directory and add the following variables:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   SLACK_BOT_TOKEN=your_slack_bot_token
   ```

## Usage

To run the DraftKings Contest Finder Agent:

1. Ensure you're in the project root directory and your Conda environment is activated.

2. Run the scheduler:
   ```
   python -m src.scheduler
   ```

The agent will start running, fetching contests every 5 minutes, processing them, and sending notifications for eligible contests.

## Features

- Contest Filtering: The system filters contests based on the number of entrants and contest title keywords.
- Entrant Analysis: Analyzes the experience level of contest participants.
- Real-time Processing: Continuously updates and analyzes contest data.
- Slack Notifications: Delivers contest recommendations via Slack.
- Database Integration: Stores and manages contest and participant data using Supabase.

## Project Structure

```
draftkings_agent/
├── src/
│   ├── __init__.py
│   ├── data_fetcher.py
│   ├── data_processor.py
│   ├── database_manager.py
│   ├── slack_notifier.py
│   └── scheduler.py
├── tests/
│   ├── __init__.py
│   ├── test_data_fetcher.py
│   ├── test_data_processor.py
│   ├── test_database_manager.py
│   ├── test_scheduler.py
│   └── test_slack_notifier.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Running Tests

To run the test suite:

```
python -m unittest discover tests
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
