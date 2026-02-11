"""
MotherDuck database client
"""

import duckdb
import os
from typing import Optional
import pandas as pd

class MotherDuckClient:
    """Client for connecting to MotherDuck database"""
    
    def __init__(self):
        self.token = os.getenv('MOTHERDUCK_TOKEN')
        if not self.token:
            raise ValueError("MOTHERDUCK_TOKEN environment variable not set")
        self._conn = None
    
    def get_connection(self):
        """Get or create MotherDuck connection"""
        if self._conn is None:
            self._conn = duckdb.connect(f'md:?motherduck_token={self.token}')
        return self._conn
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a query and return results as DataFrame"""
        conn = self.get_connection()
        result = conn.execute(query).df()
        return result
    
    def get_fundamentals(self, tickers: list) -> Optional[pd.DataFrame]:
        """
        Fetch fundamental metrics from MotherDuck for given tickers.
        
        Args:
            tickers: List of stock ticker symbols
            
        Returns:
            DataFrame with fundamental metrics or None if no data found
        """
        if not tickers:
            return None
        
        # Filter and format tickers
        valid_tickers = [t.strip().upper() for t in tickers if t and t.strip()]
        if not valid_tickers:
            return None
        
        symbols_str = "', '".join(valid_tickers)
        
        query = f"""
        WITH latest_obq AS (
            SELECT *
            FROM my_db.main.OBQ_Scores
            QUALIFY ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY calculation_date DESC) = 1
        )
        SELECT 
            gf.*,
            obq.obq_growth_score,
            obq.OBQ_Quality_Rank,
            obq.obq_momentum_score,
            obq.obq_finstr_score,
            obq.obq_value_score,
            -- Compute OBQ GM
            CASE 
                WHEN obq.obq_growth_score IS NOT NULL AND obq.obq_momentum_score IS NOT NULL
                THEN (obq.obq_growth_score + obq.obq_momentum_score) / 2.0
                ELSE NULL
            END as computed_obq_gm,
            -- Compute OBQ GQM
            CASE 
                WHEN obq.obq_growth_score IS NOT NULL AND obq.OBQ_Quality_Rank IS NOT NULL AND obq.obq_momentum_score IS NOT NULL
                THEN (obq.obq_growth_score + obq.OBQ_Quality_Rank + obq.obq_momentum_score) / 3.0
                ELSE NULL
            END as computed_obq_gqm,
            -- Compute OBQ GQV
            CASE 
                WHEN obq.obq_value_score IS NOT NULL AND obq.obq_growth_score IS NOT NULL AND obq.OBQ_Quality_Rank IS NOT NULL
                THEN (obq.obq_growth_score + obq.OBQ_Quality_Rank + obq.obq_value_score) / 3.0
                ELSE NULL
            END as computed_obq_gqv,
            -- Compute OBQ VQF
            CASE 
                WHEN obq.obq_value_score IS NOT NULL AND obq.OBQ_Quality_Rank IS NOT NULL AND obq.obq_finstr_score IS NOT NULL
                THEN (obq.obq_value_score + obq.OBQ_Quality_Rank + obq.obq_finstr_score) / 3.0
                ELSE NULL
            END as computed_obq_vqf,
            -- Compute OBQ Composite
            CASE 
                WHEN obq.obq_value_score IS NOT NULL AND obq.obq_growth_score IS NOT NULL AND obq.obq_momentum_score IS NOT NULL AND obq.OBQ_Quality_Rank IS NOT NULL AND obq.obq_finstr_score IS NOT NULL
                THEN (obq.obq_growth_score + obq.obq_momentum_score + obq.OBQ_Quality_Rank + (0.5 * obq.obq_value_score) + (0.5 * obq.obq_finstr_score)) / 5.0
                ELSE NULL
            END as computed_obq_composite
        FROM my_db.main.gurufocus_with_momentum gf
        LEFT JOIN latest_obq obq ON gf.Symbol = obq.symbol
        WHERE gf.Symbol IN ('{symbols_str}')
        ORDER BY gf.Symbol
        """
        
        result = self.execute_query(query)
        
        if result.empty:
            return None
        
        return result
    
    def close(self):
        """Close the connection"""
        if self._conn:
            self._conn.close()
            self._conn = None

# Global client instance
motherduck_client = MotherDuckClient()
