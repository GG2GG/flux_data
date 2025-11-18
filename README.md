# Retail Product Placement Agent

This is a multi-agent system that suggests product placements based on various metrics mined from historical data.
The Person enquiring, is a Business Owner, he/she provides details of their product:
- Product
- Budget (for placement)
- Price
- Category
- Target Sale
- Target Customers
- Expected Return over Investment

## 📚 Documentation

For detailed setup and usage instructions, see the [docs](docs/) folder:
- [Production Ready Guide](docs/PRODUCTION_READY.md) - Complete audit and polish summary
- [Backend Servers Guide](docs/BACKEND_SERVERS_GUIDE.md) - Server setup and troubleshooting
- [Complete Setup Guide](docs/COMPLETE_SETUP_GUIDE.md) - Web demo installation
- [Unity Installation Guide](docs/UNITY_INSTALLATION_GUIDE.md) - Unity integration steps

## Rough Agent Flow

1. Get product details
2. Analyze ROI based on historical data of sale and region
3. Suggest ROI scores based on region. eg. 
```json
{
  "Main Entrance Isle": 0.7,
  "Beverage Isle": 1.4,
  ...
}
```
4. After the suggestions, the agent will be asked follow up questions where it should defend it's suggestions backed by data. It should be able to pull up competitor products and their metrics to show that the data is suggested is historically accurate.
