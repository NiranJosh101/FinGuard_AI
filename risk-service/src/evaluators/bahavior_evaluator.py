from typing import List

def is_behavior_unusual(
    target_network: str, 
    common_networks: List[str], 
    category: str, 
    common_categories: List[str]
) -> bool:
    """
    Flags true if the underlying rails or category mapping do not align with 
    historical behaviors on record.
    """
    network_mismatch = target_network not in common_networks
    category_mismatch = category not in common_categories
    
    return network_mismatch or category_mismatch