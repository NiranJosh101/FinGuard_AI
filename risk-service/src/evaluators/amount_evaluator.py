from src.config import settings

def is_amount_anomalous(amount: float, average_transfer_amount: float) -> bool:
    """
    Flags true if the amount requested is over the configured threshold multiplier 
    (e.g., 3x typical average transfer amount).
    """
    if average_transfer_amount <= 0:
        return True # Flag anomaly if history is non-existent/corrupted
        
    threshold = average_transfer_amount * settings.AMOUNT_ANOMALY_MULTIPLIER
    return amount > threshold