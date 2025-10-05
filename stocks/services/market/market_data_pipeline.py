from stocks.services.market.market_data_repository.market_data_repository import MarketDataRepository
from stocks.services.market.market_data_fetcher.market_data_fetcher import MarketDataFetcher

from stocks.dataclasses import AssetType
from stocks.services.market.market_data_provider.market_ticket_provider import MarketTickerProvider


class MarketDataPipeline:
    """
    Orchestrates the full data pipeline for financial market assets.
    """
    # --- MÉTODO GENÉRICO PARA REDUCIR DUPLICIDAD ---
    @staticmethod
    def _update_time_series_for_asset_type(
        asset_type: AssetType,
        get_tickers_func,
        period: str,
        interval: str
    ):
        """
        Generic handler for updating time series data for a given asset type.
        :param asset_type: AssetType (STOCK, ETF, CURRENCY)
        :param get_tickers_func: Function to fetch list of tickers for that asset type.
        :param period: Time period for historical data.
        :param interval: Data interval (1d, 1wk, etc.)
        """
        print(f"🚀 Starting {asset_type.value.lower()} time series update | Period={period}, Interval={interval}")

        tickers = get_tickers_func()
        print(f"📊 Found {len(tickers)} {asset_type.value}s to process.")

        processed, failed = 0, 0

        for ticker in tickers:
            try:
                print(f"🔹 Fetching time series for {ticker.symbol} ...")

                time_series = MarketDataFetcher.get_time_series(
                    ticker=ticker.symbol,
                    asset_type=asset_type,
                    period=period,
                    interval=interval
                )

                if not time_series:
                    print(f"⚠️ No data returned for {ticker.symbol}")
                    failed += 1
                    continue

                MarketDataRepository.save_time_series(time_series)
                print(f"✅ Stored {len(time_series)} entries for {ticker.symbol}")
                processed += 1

            except Exception as e:
                print(f"❌ Error processing {ticker.symbol}: {e}")
                failed += 1

        print(f"📈 {asset_type.value} time series update completed: {processed} succeeded, {failed} failed.")


    # --- ESPECÍFICOS DE CADA TIPO DE ACTIVO ---
    @staticmethod
    def update_stock_time_series(period: str = "5y", interval: str = "1d"):
        MarketDataPipeline._update_time_series_for_asset_type(
            asset_type=AssetType.STOCK,
            get_tickers_func=MarketTickerProvider.get_sp500_tickers,
            period=period,
            interval=interval
        )

    @staticmethod
    def update_etf_time_series(period: str = "5y", interval: str = "1d"):
        MarketDataPipeline._update_time_series_for_asset_type(
            asset_type=AssetType.ETF,
            get_tickers_func=MarketTickerProvider.get_etf_tickers,
            period=period,
            interval=interval
        )

    @staticmethod
    def update_currency_time_series(period: str = "5y", interval: str = "1d"):
        MarketDataPipeline._update_time_series_for_asset_type(
            asset_type=AssetType.FOREX,
            get_tickers_func=MarketTickerProvider.get_currency_tickers,
            period=period,
            interval=interval
        )


    @staticmethod
    def update_stock_metrics():
        """
        Fetch and store the latest metrics for all S&P 500 stocks.
        """
        print("🚀 Starting stock metrics update for S&P 500...")

        tickers = MarketTickerProvider.get_sp500_tickers()
        print(f"📊 Found {len(tickers)} tickers to process.")

        processed, failed = 0, 0

        # 2️⃣ Recorrer cada ticker
        for ticker in tickers:
            try:
                print(f"🔹 Fetching metrics for {ticker.symbol} ...")

                # Obtener métricas del ticker
                metrics = MarketDataFetcher.get_stock_metrics(ticker.symbol)

                if not metrics:
                    print(f"⚠️ No metrics returned for {ticker.symbol}")
                    failed += 1
                    continue

                # Guardar métricas en la base de datos
                MarketDataRepository.save_stock_metrics(metrics)

                print(f"✅ Stored metrics for {ticker.symbol}")
                processed += 1

            except Exception as e:
                print(f"❌ Error processing {ticker.symbol}: {e}")
                failed += 1

        print(f"📈 Stock metrics update completed: {processed} succeeded, {failed} failed.")

    @staticmethod
    def update_etf_metrics():
        """
        Fetch and store the latest metrics for all predefined ETFs.
        """
        print("🚀 Starting ETF metrics update...")

        # 1️⃣ Obtener los tickers de ETFs predefinidos
        tickers = MarketTickerProvider.get_etf_tickers()
        print(f"📊 Found {len(tickers)} ETF tickers to process.")

        processed, failed = 0, 0

        # 2️⃣ Recorrer cada ETF
        for ticker in tickers:
            try:
                print(f"🔹 Fetching metrics for ETF {ticker.symbol} ...")

                # Obtener métricas del ETF
                metrics = MarketDataFetcher.get_etf_metrics(ticker.symbol)

                if not metrics:
                    print(f"⚠️ No metrics returned for {ticker.symbol}")
                    failed += 1
                    continue

                # Guardar métricas del ETF
                MarketDataRepository.save_etf_metrics(metrics)

                print(f"✅ Stored metrics for ETF {ticker.symbol}")
                processed += 1

            except Exception as e:
                print(f"❌ Error processing ETF {ticker.symbol}: {e}")
                failed += 1

        print(f"📈 ETF metrics update completed: {processed} succeeded, {failed} failed.")

    
    @staticmethod
    def update_currency_metrics():
        """
        Fetch and store the latest metrics for all predefined currency pairs.
        """
        print("🚀 Starting currency metrics update...")

        # 1️⃣ Obtener tickers de pares de divisas (Forex)
        tickers = MarketTickerProvider.get_currency_tickers()
        print(f"📊 Found {len(tickers)} currency tickers to process.")

        processed, failed = 0, 0

        # 2️⃣ Recorrer cada par de divisas
        for ticker in tickers:
            try:
                print(f"🔹 Fetching metrics for currency pair {ticker.symbol} ...")

                # Obtener métricas de la divisa
                metrics = MarketDataFetcher.get_currency_metrics(ticker.symbol)

                if not metrics:
                    print(f"⚠️ No metrics returned for {ticker.symbol}")
                    failed += 1
                    continue

                # Guardar métricas de la divisa
                MarketDataRepository.save_currency_metrics(metrics)

                print(f"✅ Stored metrics for currency pair {ticker.symbol}")
                processed += 1

            except Exception as e:
                print(f"❌ Error processing currency pair {ticker.symbol}: {e}")
                failed += 1

        print(f"📈 Currency metrics update completed: {processed} succeeded, {failed} failed.")
        

    @staticmethod
    def run_all(period: str = "5y", interval: str = "1d"):
        """
        Execute the full market data pipeline for all asset types:
        updates both time series and metrics data for stocks, ETFs, and currencies.
        """
        print("🚀 Starting full Market Data Pipeline execution...")
        print(f"🕒 Configuration: Period={period}, Interval={interval}")
        print("-" * 80)

        try:
            # --- SERIES TEMPORALES ---
            print("\n📘 Updating STOCK time series...")
            MarketDataPipeline.update_stock_time_series(period, interval)

            print("\n📗 Updating ETF time series...")
            MarketDataPipeline.update_etf_time_series(period, interval)

            print("\n📙 Updating CURRENCY time series...")
            MarketDataPipeline.update_currency_time_series(period, interval)

            # --- MÉTRICAS ---
            print("\n📈 Updating STOCK metrics...")
            MarketDataPipeline.update_stock_metrics()

            print("\n💹 Updating ETF metrics...")
            MarketDataPipeline.update_etf_metrics()

            print("\n💱 Updating CURRENCY metrics...")
            MarketDataPipeline.update_currency_metrics()

            print("\n✅ All market data successfully updated!")

        except Exception as e:
            print(f"\n❌ Pipeline failed due to unexpected error: {e}")

        print("-" * 80)
        print("🏁 Market Data Pipeline completed.")
