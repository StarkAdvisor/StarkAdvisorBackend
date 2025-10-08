from starkadvisorbackend.utils.django_setup import ensure_django

# Initialize Django and require the 'stocks' app to be present
ensure_django(require_apps=["stocks"])

from stocks.services.market.market_data_pipeline import MarketDataPipeline
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Run MarketDataPipeline commands from the console."
    )

    # Subcomando (qué función ejecutar)
    parser.add_argument(
        "command",
        choices=[
            "update_stock_time_series",
            "update_etf_time_series",
            "update_currency_time_series",
            "update_stock_metrics",
            "update_etf_metrics",
            "update_currency_metrics",
            "run_all"
        ],
        help="Command to execute in the MarketDataPipeline."
    )

    # Argumentos opcionales comunes
    parser.add_argument("--period", default="5y", help="Historical period (default: 5y)")
    parser.add_argument("--interval", default="1d", help="Data interval (default: 1d)")

    args = parser.parse_args()

    # Llamar la función correspondiente dinámicamente
    try:
        if args.command == "run_all":
            MarketDataPipeline.run_all(period=args.period, interval=args.interval)
        else:
            func = getattr(MarketDataPipeline, args.command)
            if "time_series" in args.command:
                func(period=args.period, interval=args.interval)
            else:
                func()
        print(f"✅ Command '{args.command}' executed successfully!")
    except AttributeError:
        print(f"❌ Error: Method '{args.command}' not found in MarketDataPipeline.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
