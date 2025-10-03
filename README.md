# buzzline-06-webb

This project implements real-time monitoring using both JSON and CSV data streaming through Apache Kafka.


## Prerequisites

- Python 3.11
- Apache Kafka (local installation)

## Setup

### 1. Environment Setup

```bash
# Create virtual environment
py -3.11 -m venv .venv

# Activate virtual environment
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# Install dependencies
py -m pip install --upgrade pip wheel setuptools
py -m pip install -r requirements.txt
```

### 2. Start Kafka

```bash
# Prepare Kafka (first time only)
chmod +x scripts/prepare_kafka.sh
scripts/prepare_kafka.sh

# Start Kafka server
cd ~/kafka
bin/kafka-server-start.sh config/kraft/server.properties
```


## License

MIT License - See [LICENSE.txt](LICENSE.txt)