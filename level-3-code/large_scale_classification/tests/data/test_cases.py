"""Test cases for the large-scale classification system.

This file contains comprehensive test cases covering different categories
from the current category set. These test cases include realistic product
descriptions and expected category classifications.
"""

from typing import TypedDict


class TestCase(TypedDict):
    """Test case."""

    text: str
    category: str
    predicted_categories: list[str]


tests: list[TestCase] = [
    {
        "text": "Samsung Counter-Depth 17.5-cu ft 3-Door Smart Compatible French Door Refrigerator with Ice Maker (Fingerprint Resistant Matte Black Steel) ENERGY STAR Certified",
        "category": "/Appliances/Refrigerators/French Door Refrigerators",
        "predicted_categories": [
            "/Appliances/Refrigerators/French Door Refrigerators",
            "/Appliances/Refrigerators",
            "/Appliances/Dishwashers",
            "/Appliances/Garbage Disposals",
            "/Appliances",
        ],
    },
    {
        "text": 'Bosch 800 Series 24" Stainless Steel Built-In Dishwasher with Third Rack and CrystalDry Technology',
        "category": "/Appliances/Dishwashers/Built-In Dishwashers",
        "predicted_categories": [
            "/Appliances/Dishwashers/Built-In Dishwashers",
            "/Appliances/Dishwashers/Countertop Dishwashers",
            "/Appliances/Dishwashers/Portable Dishwashers",
            "/Appliances/Dishwashers",
            "/Appliances",
        ],
    },
    {
        "text": "BLACK+DECKER 6-Place Setting Compact Countertop Dishwasher in White",
        "category": "/Appliances/Dishwashers/Countertop Dishwashers",
        "predicted_categories": [
            "/Appliances/Dishwashers/Countertop Dishwashers",
            "/Appliances/Dishwashers/Portable Dishwashers",
            "/Appliances/Dishwashers",
        ],
    },
    {
        "text": "GE Portable Dishwasher with Stainless Steel Interior and Wheels",
        "category": "/Appliances/Dishwashers/Portable Dishwashers",
        "predicted_categories": [
            "/Appliances/Dishwashers/Portable Dishwashers",
            "/Appliances/Dishwashers/Countertop Dishwashers",
            "/Appliances/Dishwashers/Built-In Dishwashers",
            "/Appliances/Dishwashers",
            "/Appliances",
        ],
    },
    {
        "text": "Hobart LXER-2 Undercounter Commercial Dishwasher with Built-in Booster Heater",
        "category": "/Appliances/Dishwashers/Commercial Dishwashers",
        "predicted_categories": [
            "/Appliances/Dishwashers/Commercial Dishwashers",
            "/Appliances/Dishwashers",
            "/Appliances",
        ],
    },
    {
        "text": "InSinkErator Evolution Compact 3/4 HP Garbage Disposal with SoundSeal Technology",
        "category": "/Appliances/Garbage Disposals",
        "predicted_categories": [
            "/Appliances/Garbage Disposals",
            "/Appliances/Appliance Parts/Garbage Disposal Parts",
            "/Appliances",
        ],
    },
    {
        "text": "Whirlpool Dishwasher Upper Dish Rack Assembly W10350375",
        "category": "/Appliances/Appliance Parts/Dishwasher Parts",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Dishwasher Parts",
            "/Appliances/Appliance Parts/Small Appliance Parts",
            "/Appliances/Appliance Parts/Refrigerator Parts",
            "/Appliances/Appliance Parts",
            "/Appliances",
        ],
    },
    {
        "text": "KitchenAid Stand Mixer Bowl Lift Lever and Spring Assembly",
        "category": "/Appliances/Appliance Parts/Small Appliance Parts",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Small Appliance Parts",
            "/Appliances/Appliance Parts/Dishwasher Parts",
            "/Appliances/Appliance Parts/Microwave Parts",
            "/Appliances/Appliance Parts",
            "/Appliances",
        ],
    },
    {
        "text": "Samsung DA29-00020B HAF-CIN/EXP Refrigerator Water Filter",
        "category": "/Appliances/Appliance Parts/Refrigerator Water Filters",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Refrigerator Water Filters",
            "/Appliances/Appliance Parts/Refrigerator Air Filters",
            "/Appliances/Appliance Parts/Refrigerator Parts",
        ],
    },
    {
        "text": "LG ADQ36006101 Refrigerator Air Filter for French Door Models",
        "category": "/Appliances/Appliance Parts/Refrigerator Air Filters",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Refrigerator Air Filters",
            "/Appliances/Appliance Parts/Refrigerator Water Filters",
            "/Appliances/Appliance Parts/Refrigerator Parts",
            "/Appliances/Appliance Parts",
            "/Appliances",
        ],
    },
    {
        "text": "GE WR17X12633 Refrigerator Ice Maker Assembly",
        "category": "/Appliances/Appliance Parts/Refrigerator Parts",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Refrigerator Parts",
            "/Appliances/Appliance Parts/Ice Maker Kits",
            "/Appliances/Appliance Parts",
        ],
    },
    {
        "text": 'Broan-NuTone Range Hood Grease Filter 11-3/4" x 14-1/4" Aluminum',
        "category": "/Appliances/Appliance Parts/Range Hood Parts",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Range Hood Parts",
            "/Appliances/Appliance Parts/Oven Parts",
            "/Appliances/Appliance Parts/Cooktop Parts",
            "/Appliances/Appliance Parts",
            "/Appliances",
        ],
    },
    {
        "text": "Frigidaire 316075103 Oven Bake Element 2500 Watts",
        "category": "/Appliances/Appliance Parts/Oven Parts",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Oven Parts",
            "/Appliances/Appliance Parts/Range Hood Parts",
            "/Appliances/Appliance Parts/Stove Parts",
        ],
    },
    {
        "text": "InSinkErator Garbage Disposal Splash Guard and Stopper",
        "category": "/Appliances/Appliance Parts/Garbage Disposal Parts",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Garbage Disposal Parts",
            "/Appliances/Garbage Disposals",
            "/Appliances/Appliance Parts/Small Appliance Parts",
            "/Appliances/Appliance Parts",
            "/Appliances",
        ],
    },
    {
        "text": "Sharp Carousel Microwave Glass Turntable Plate 12.5 Inch",
        "category": "/Appliances/Appliance Parts/Microwave Parts",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Microwave Parts",
            "/Appliances/Appliance Parts/Small Appliance Parts",
            "/Appliances/Appliance Parts/Oven Parts",
        ],
    },
    {
        "text": "Whirlpool W10715708 Ice Maker Kit for Top-Freezer Refrigerators",
        "category": "/Appliances/Appliance Parts/Ice Maker Kits",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Ice Maker Kits",
            "/Appliances/Appliance Parts/Refrigerator Parts",
            "/Appliances/Appliance Parts",
        ],
    },
    {
        "text": "GE WB31T10013 Cooktop Burner Drip Pan Set Chrome",
        "category": "/Appliances/Appliance Parts/Cooktop Parts",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Cooktop Parts",
            "/Appliances/Appliance Parts/Stove Parts",
            "/Appliances/Appliance Parts",
        ],
    },
    {
        "text": "Whirlpool W10116794 Stove Burner Control Knob Black",
        "category": "/Appliances/Appliance Parts/Stove Parts",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Stove Parts",
            "/Appliances/Appliance Parts/Cooktop Parts",
            "/Appliances/Appliance Parts",
        ],
    },
    {
        "text": "Frigidaire 5304505209 Freezer Door Gasket Seal",
        "category": "/Appliances/Appliance Parts/Freezer Parts",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Freezer Parts",
            "/Appliances/Appliance Parts/Refrigerator Parts",
            "/Appliances/Appliance Parts",
        ],
    },
    {
        "text": "NewAir Wine Cooler Replacement Shelves AWR-460DB Set of 6",
        "category": "/Appliances/Appliance Parts/Wine Cooler Parts",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Wine Cooler Parts",
            "/Appliances/Appliance Parts/Refrigerator Parts",
            "/Appliances/Appliance Parts/Freezer Parts",
            "/Appliances/Appliance Parts",
            "/Appliances",
        ],
    },
    {
        "text": "Whirlpool W10837240 Dryer Lint Screen Filter",
        "category": "/Appliances/Appliance Parts/Dryer Parts",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Dryer Parts",
            "/Appliances/Appliance Parts/Washer and Dryer Stacking Kits",
            "/Appliances/Appliance Parts/Small Appliance Parts",
        ],
    },
    {
        "text": "GE WC22X10047 Trash Compactor Bags 15-Pack",
        "category": "/Appliances/Appliance Parts/Trash Compactor Parts",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Trash Compactor Parts",
            "/Appliances/Appliance Parts/Garbage Disposal Parts",
            "/Appliances/Appliance Parts/Small Appliance Parts",
            "/Appliances/Appliance Parts",
            "/Appliances",
        ],
    },
    {
        "text": "Frigidaire 5304505209 Dehumidifier Water Collection Bucket",
        "category": "/Appliances/Appliance Parts/Dehumidifier Parts",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Dehumidifier Parts",
            "/Appliances/Appliance Parts/Small Appliance Parts",
            "/Appliances/Appliance Parts/Refrigerator Parts",
        ],
    },
    {
        "text": "Samsung SKK-DD Washer Dryer Stacking Kit with Pull-Out Shelf",
        "category": "/Appliances/Appliance Parts/Washer and Dryer Stacking Kits",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Washer and Dryer Stacking Kits",
            "/Appliances/Appliance Parts/Dryer Parts",
            "/Appliances/Appliance Parts/Small Appliance Parts",
            "/Appliances/Appliance Parts",
            "/Appliances",
        ],
    },
    {
        "text": "Shark Navigator Vacuum Belt 2-Pack XB2950",
        "category": "/Appliances/Appliance Parts/Vacuum Parts/Vacuum Belts",
        "predicted_categories": [
            "/Appliances/Appliance Parts/Vacuum Parts/Vacuum Belts",
            "/Appliances/Appliance Parts/Vacuum Parts",
            "/Appliances/Appliance Parts/Small Appliance Parts",
            "/Appliances/Appliance Parts",
            "/Appliances",
        ],
    },
]
