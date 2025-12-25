
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backend.models import FactSales, FactForecasts, DimProducts

class ForecastingEngine:
    def __init__(self, db: Session):
        self.db = db

    def calculate_forecast(self, sku_id: str, model_type: str = 'SMA', periods: int = 30):
        """
        Calculates forecast for a specific SKU.
        :param model_type: 'SMA' (Simple Moving Average) or 'EMA' (Exponential Moving Average)
        :param periods: Number of days to forecast into the future
        """
        # 1. Fetch Sales History
        sales = self.db.query(FactSales.order_date, FactSales.quantity).filter(
            FactSales.sku_id == sku_id
        ).order_by(FactSales.order_date.asc()).all()

        if not sales:
            return {"status": "error", "message": "No sales data found for this product"}

        # 2. Convert to DataFrame
        df = pd.DataFrame(sales, columns=['date', 'quantity'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # Resample to Daily and Fill Missing with 0
        df_daily = df.resample('D').sum().fillna(0)
        
        # 3. Apply Forecasting Logic
        forecast_values = []
        last_date = df_daily.index[-1]
        
        if model_type == 'SMA':
            # Simple Moving Average (Window = 7 days for weekly seasonality smoothing)
            window = 7
            # Calculate rolling mean for historical context
            df_daily['forecast'] = df_daily['quantity'].rolling(window=window).mean()
            
            # Predict future
            # Naive approach for SMA continuation: use the last calculated average as the base
            # Better approach: Iterative SMA? 
            # For simplicity in MVP: Take the average of the last 'window' days and project it flat (Naïve)
            # OR Trend? Let's use last 30 days avg for simple projection
            last_avg = df_daily['quantity'].tail(30).mean()
            if np.isnan(last_avg): last_avg = 0
            
            forecast_values = [last_avg] * periods
            
        elif model_type == 'EMA':
            # Exponential Moving Average (Span = 30)
            span = 30
            df_daily['forecast'] = df_daily['quantity'].ewm(span=span, adjust=False).mean()
            
            # Project using last EMA value
            last_ema = df_daily['forecast'].iloc[-1]
            if np.isnan(last_ema): last_ema = 0
            
            forecast_values = [last_ema] * periods

        # 4. Save Forecast to DB
        # First, clear old forecasts for this SKU and run date? Or keep history?
        # Let's overwrite for same run_date (today)
        today = datetime.now().date()
        self.db.query(FactForecasts).filter(
            FactForecasts.sku_id == sku_id,
            FactForecasts.run_date == today
        ).delete()
        
        new_records = []
        for i, val in enumerate(forecast_values):
            target_date = last_date + timedelta(days=i+1)
            new_records.append(FactForecasts(
                run_date=today,
                sku_id=sku_id,
                forecast_date=target_date,
                quantity_predicted=round(float(val), 2),
                model_used=model_type
            ))
        
        self.db.add_all(new_records)
        self.db.commit()
        
        return {
            "status": "success", 
            "sku_id": sku_id,
            "model": model_type,
            "forecasted_days": periods,
            "avg_predicted_qty": round(sum(forecast_values)/len(forecast_values), 2)
        }

    def get_forecast_vs_actual(self, sku_id: str):
        """
        Returns merged actual sales and forecast data for visualization.
        """
        # Actuals
        sales = self.db.query(FactSales.order_date, FactSales.quantity).filter(
            FactSales.sku_id == sku_id
        ).order_by(FactSales.order_date.asc()).all()
        
        data = {}
        for s in sales:
            d_str = s.order_date.strftime("%Y-%m-%d")
            if d_str not in data: data[d_str] = {"date": d_str, "actual": 0, "forecast": None}
            data[d_str]["actual"] += s.quantity

        # Forecasts (Latest Run)
        latest_run = self.db.query(func.max(FactForecasts.run_date)).filter(
            FactForecasts.sku_id == sku_id
        ).scalar()
        
        if latest_run:
            forecasts = self.db.query(FactForecasts).filter(
                FactForecasts.sku_id == sku_id,
                FactForecasts.run_date == latest_run
            ).all()
            
            for f in forecasts:
                d_str = f.forecast_date.strftime("%Y-%m-%d")
                if d_str not in data: data[d_str] = {"date": d_str, "actual": None, "forecast": 0}
                data[d_str]["forecast"] = f.quantity_predicted

        # Sort list
        sorted_data = sorted(data.values(), key=lambda x: x['date'])
        return sorted_data
