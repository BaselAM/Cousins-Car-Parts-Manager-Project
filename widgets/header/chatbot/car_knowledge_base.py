"""
Domain-specific knowledge base for car parts information.
"""


class CarPartsKnowledgeBase:
    """Knowledge base with multilingual information about car parts"""

    def __init__(self):
        """Initialize with structured car parts information"""
        self.parts_info = {
            "engine": {
                "description": "The power unit of a vehicle that converts fuel into motion through combustion.",
                "common_issues": "Overheating, oil leaks, timing belt failures, misfiring, rough idling.",
                "maintenance": "Regular oil changes, timing belt replacement, air filter changes, cooling system checks."
            },
            "transmission": {
                "description": "Transfers power from the engine to the wheels with different gear ratios.",
                "common_issues": "Fluid leaks, gear slipping, hard shifting, delayed engagement, unusual noises.",
                "maintenance": "Fluid changes, filter replacement, checking for leaks, clutch adjustment (manual)."
            },
            "brakes": {
                "description": "System that slows or stops the vehicle using friction against rotating wheels.",
                "common_issues": "Squeaking/grinding noises, soft pedal feel, vibration when braking, longer stopping distance.",
                "maintenance": "Pad replacement, rotor resurfacing or replacement, fluid flush, caliper maintenance."
            },
            "suspension": {
                "description": "System of springs, shock absorbers and linkages connecting a vehicle to its wheels.",
                "common_issues": "Rough ride, uneven tire wear, vehicle pulling to one side, knocking noises, excessive bouncing.",
                "maintenance": "Shock/strut replacement, alignment checks, bushing inspection, spring assessment."
            },
            "alternator": {
                "description": "Generates electrical power to charge the battery and power electrical systems while the engine runs.",
                "common_issues": "Battery warning light, dim headlights, electrical failures, strange noises, battery not charging.",
                "maintenance": "Belt inspection, terminal cleaning, voltage output testing."
            },
            "battery": {
                "description": "Provides electrical current for starting the engine and powering electrical components when the engine is off.",
                "common_issues": "Difficulty starting, electrical component failures, corrosion on terminals, short battery life.",
                "maintenance": "Terminal cleaning, water level checks (non-sealed types), load testing, replacement every 3-5 years."
            },
            "radiator": {
                "description": "Heat exchanger that prevents the engine from overheating by cooling the circulating coolant.",
                "common_issues": "Leaks, overheating, clogged passages, damaged fins, corrosion.",
                "maintenance": "Coolant flush/replacement, pressure testing, cleaning exterior fins, checking for leaks."
            },
            "starter": {
                "description": "Electric motor that initiates engine operation by turning the flywheel.",
                "common_issues": "Clicking sound without engine turnover, intermittent starting problems, grinding noises.",
                "maintenance": "Connection checking, testing current draw, replacement when worn."
            },
            "fuel pump": {
                "description": "Delivers fuel from the tank to the engine under pressure.",
                "common_issues": "Engine sputtering at high speeds, loss of power during acceleration, engine not starting, whining noise.",
                "maintenance": "Fuel filter replacement, keeping fuel level above 1/4 tank, pressure testing."
            },
            "spark plugs": {
                "description": "Create electric spark to ignite the air-fuel mixture in the engine's combustion chamber.",
                "common_issues": "Misfiring, rough idling, trouble starting, increased fuel consumption, lack of acceleration.",
                "maintenance": "Regular replacement (30,000-100,000 miles depending on type), proper gap adjustment, torque to spec."
            },
            "oil": {
                "description": "Lubricates engine components to reduce friction and wear while helping cool the engine.",
                "common_issues": "Low level, contamination, incorrect viscosity, sludge buildup, leaks.",
                "maintenance": "Regular changes (every 3,000-10,000 miles depending on type), level checks, filter replacement."
            },
            "timing belt": {
                "description": "Synchronizes the rotation of the crankshaft and camshaft to ensure proper engine valve operation.",
                "common_issues": "Cracking, fraying, breaking (catastrophic engine damage in interference engines), noise.",
                "maintenance": "Replacement every 60,000-100,000 miles (as specified by manufacturer), tension checking."
            },
            "air filter": {
                "description": "Prevents dust, dirt and debris from entering the engine while allowing sufficient airflow.",
                "common_issues": "Clogging, reduced engine performance, increased fuel consumption, strange engine sounds.",
                "maintenance": "Regular inspection and replacement (every 15,000-30,000 miles), cleaning (if reusable type)."
            },
            "power steering": {
                "description": "System that assists driver in steering the vehicle by using hydraulic or electric pressure.",
                "common_issues": "Fluid leaks, whining noise, difficulty steering, steering wheel jerking, fluid contamination.",
                "maintenance": "Fluid level checks, fluid replacement, belt inspection, system flushing."
            },
            "exhaust": {
                "description": "System that guides exhaust gases away from the engine and reduces noise and pollution.",
                "common_issues": "Loud noise, exhaust leaks, rust/corrosion, reduced fuel efficiency, hanging pipes.",
                "maintenance": "Regular inspection, rust treatment, hanger replacement, catalytic converter checking."
            },
            "tires": {
                "description": "Rubber components that provide traction, absorb shock, and support the vehicle's weight.",
                "common_issues": "Uneven wear, low pressure, sidewall damage, excessive noise, vibration while driving.",
                "maintenance": "Regular rotation, pressure checks, alignment, balance, replacement when tread is worn."
            },
            "injectors": {
                "description": "Electronically controlled valves that spray fuel into the engine's intake manifold or combustion chamber.",
                "common_issues": "Clogging, leaking, improper spray pattern, engine misfires, rough idle, poor performance.",
                "maintenance": "Fuel system cleaning, occasional professional cleaning, keeping fuel filter changed."
            },
            # Hebrew translations
            "מנוע": {  # Engine in Hebrew
                "description": "יחידת הכוח של הרכב, הממירה דלק לתנועה באמצעות בעירה.",
                "common_issues": "התחממות יתר, דליפות שמן, כשלי רצועת תזמון, החטאות, סרק גס.",
                "maintenance": "החלפות שמן סדירות, החלפת רצועת תזמון, החלפות מסנן אוויר, בדיקות מערכת קירור."
            },
            "בלמים": {  # Brakes in Hebrew
                "description": "מערכת המאטה או עוצרת את הרכב באמצעות חיכוך נגד גלגלים מסתובבים.",
                "common_issues": "רעשי חריקה/שיוף, תחושת דוושה רכה, רעידות בזמן בלימה, מרחק עצירה ארוך יותר.",
                "maintenance": "החלפת רפידות, השחזת דיסקיות או החלפתן, שטיפת נוזל, תחזוקת קליפרים."
            }
        }

        # Car-related terms for query detection
        self.car_terms = [
            # English
            'car', 'vehicle', 'auto', 'automobile', 'part', 'repair', 'fix',
            'issue', 'problem', 'maintenance', 'service', 'engine', 'transmission',
            'brake', 'wheel', 'tire', 'oil', 'filter', 'battery', 'cooling',
            # Hebrew
            'רכב', 'מכונית', 'חלק', 'תיקון', 'בעיה', 'טיפול', 'שירות', 'מנוע',
            'תמסורת', 'בלם', 'גלגל', 'צמיג', 'שמן', 'מסנן', 'מצבר', 'קירור'
        ]

    def search(self, query):
        """Search for information about a car part"""
        query = query.lower()

        # Exact match
        if query in self.parts_info:
            part = self.parts_info[query]
            return f"{query.title()}: {part['description']}\n\nCommon issues: {part['common_issues']}\n\nMaintenance: {part['maintenance']}"

        # Partial match
        for part_name, info in self.parts_info.items():
            if part_name in query or query in part_name:
                return f"{part_name.title()}: {info['description']}\n\nCommon issues: {info['common_issues']}\n\nMaintenance: {info['maintenance']}"

        # No match
        return None

    def is_car_parts_query(self, query):
        """Check if the query is related to car parts"""
        query = query.lower()

        # Check if any car part is mentioned
        for part_name in self.parts_info:
            if part_name in query:
                return True

        # Check for general car terms
        for term in self.car_terms:
            if term in query:
                return True

        return False

    def get_all_part_names(self):
        """Return a list of all part names for auto-completion"""
        return list(self.parts_info.keys())