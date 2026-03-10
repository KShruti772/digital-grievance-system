def classify_priority(category, description):
    """
    Classify complaint priority based on category and description content.

    Args:
        category (str): The complaint category
        description (str): The complaint description

    Returns:
        str: Priority level ('High', 'Medium', or 'Low')
    """
    # Convert description to lowercase for case-insensitive matching
    desc_lower = description.lower()

    # Define priority keywords for each category
    priority_rules = {
        'Road': {
            'high': [
                'accident', 'accidents', 'fatal', 'injury', 'injuries',
                'deep pothole', 'huge pothole', 'large pothole', 'massive pothole',
                'road collapse', 'bridge collapse', 'sinkhole', 'cave-in',
                'emergency', 'urgent', 'dangerous', 'hazard', 'life-threatening'
            ],
            'medium': [
                'pothole', 'crack', 'cracks', 'damage', 'damaged',
                'broken', 'uneven', 'rough', 'bumpy', 'hole'
            ],
            'low': [
                'repaint', 'marking', 'markings', 'line', 'lines',
                'clean', 'maintenance', 'minor', 'small'
            ]
        },
        'Water': {
            'high': [
                'flooding', 'flood', 'flooded', 'major leakage', 'burst pipe',
                'water contamination', 'sewage', 'overflow', 'emergency',
                'no water', 'water shortage', 'crisis', 'urgent'
            ],
            'medium': [
                'leakage', 'leaking', 'pipe leak', 'dripping', 'slow flow',
                'pressure low', 'water quality', 'dirty water'
            ],
            'low': [
                'slow leakage', 'minor leak', 'maintenance', 'check',
                'routine', 'schedule', 'regular'
            ]
        },
        'Garbage': {
            'high': [
                'hospital', 'school', 'market', 'public place', 'large dump',
                'pile of garbage', 'garbage mountain', 'overflowing',
                'health hazard', 'disease', 'pest', 'rats', 'emergency'
            ],
            'medium': [
                'garbage pile', 'waste accumulation', 'dump', 'rubbish',
                'trash', 'litter', 'collection needed'
            ],
            'low': [
                'cleaning request', 'regular pickup', 'schedule',
                'maintenance', 'minor', 'small amount'
            ]
        },
        'Electricity': {
            'high': [
                'power outage', 'blackout', 'no electricity', 'emergency',
                'hospital', 'life support', 'fire hazard', 'short circuit',
                'exposed wires', 'dangerous', 'life-threatening'
            ],
            'medium': [
                'flickering', 'dim light', 'loose connection', 'faulty wiring',
                'street light', 'pole damaged', 'transformer issue'
            ],
            'low': [
                'bulb replacement', 'maintenance', 'check', 'routine',
                'minor issue', 'small problem'
            ]
        },
        'Streetlights': {
            'high': [
                'dark area', 'crime', 'safety', 'emergency', 'accident risk',
                'no light', 'completely dark', 'dangerous', 'high crime area'
            ],
            'medium': [
                'flickering', 'dim', 'broken bulb', 'not working',
                'intermittent', 'faulty'
            ],
            'low': [
                'maintenance', 'cleaning', 'bulb change', 'routine check',
                'minor issue'
            ]
        },
        'Drainage': {
            'high': [
                'flooding', 'water logging', 'standing water', 'mosquito',
                'disease', 'health hazard', 'emergency', 'overflow',
                'blocked completely', 'major blockage'
            ],
            'medium': [
                'slow drainage', 'clogged', 'partial blockage', 'smell',
                'sewage backup', 'water accumulation'
            ],
            'low': [
                'cleaning', 'maintenance', 'routine', 'check',
                'minor blockage', 'leaves'
            ]
        }
    }

    # Get rules for the category (default to generic if category not found)
    category_rules = priority_rules.get(category, {
        'high': ['emergency', 'urgent', 'danger', 'hazard', 'life-threatening', 'accident'],
        'medium': ['problem', 'issue', 'broken', 'faulty', 'repair needed'],
        'low': ['maintenance', 'cleaning', 'check', 'routine', 'minor']
    })

    # Check for high priority keywords
    for keyword in category_rules['high']:
        if keyword in desc_lower:
            return 'High'

    # Check for medium priority keywords
    for keyword in category_rules['medium']:
        if keyword in desc_lower:
            return 'Medium'

    # Check for low priority keywords
    for keyword in category_rules['low']:
        if keyword in desc_lower:
            return 'Low'

    # Default priority if no keywords match
    return 'Medium'