# Model Router / Cost Optimizer

An intelligent routing layer that dynamically selects the cheapest Fireworks AI model capable of answering each query accurately, optimizing token costs while maintaining quality.

## 🎯 Key Features

- **Dynamic Model Selection** - Routes queries to optimal model based on complexity
- **Cost Optimization** - Achieve 40-70% cost reduction vs. single-model approaches
- **Accuracy Monitoring** - Continuous feedback loop maintains quality thresholds
- **Real-time Analytics** - Live dashboards for cost, accuracy, and routing distribution

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/model-router-cost-optimizer.git
cd model-router-cost-optimizer

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config.example.yaml config.yaml
# Edit config.yaml with your Fireworks API keys

# Run locally
python -m api.main
