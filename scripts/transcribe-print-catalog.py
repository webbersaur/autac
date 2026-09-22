"""Transcription of the Autac printed catalog (catalog/autac-catalog.pdf, pages
6-14) into catalog/data/products.json. Compact tuples per row so it can be
audited line by line against the PDF.

Row tuple: (catNo, conductors, awg, strand, tempC, voltage, amps, type, condOD, coilOD, lengths, weights)
"""
import json
from pathlib import Path

L4 = [12, 24, 36, 48]

CATEGORIES = [
    {
        "id": "tpe-power",
        "name": "TPE Power Cords",
        "conductor": "Soft bare copper",
        "insulation": "TPE",
        "jacket": "TPR",
        "shield": False,
        "listing": "UL/cUL Listed",
        "extension": "1:5",
        "catalogPage": 6,
        "notes": "TPE insulated, TPR black jacket. W suffix: white jacket.",
    },
    {
        "id": "tpr-power",
        "name": "TPR Power Cords",
        "conductor": "Soft bare copper",
        "insulation": "TPE",
        "jacket": "TPR",
        "shield": False,
        "listing": "UL/cUL Listed",
        "extension": "1:5",
        "catalogPage": 7,
        "notes": "TPE insulated, TPR black jacket.",
    },
    {
        "id": "pvc-power",
        "name": "PVC Power Cords",
        "conductor": "Soft bare copper",
        "insulation": "PVC",
        "jacket": "PVC",
        "shield": False,
        "listing": "UL/cUL Listed",
        "extension": "1:5",
        "catalogPage": 8,
        "notes": "PVC insulated, PVC black jacket. Numbers ending in W are the same cord in white.",
    },
    {
        "id": "tpe-power-bare",
        "name": "TPE Power Cords (TPE Jacket)",
        "conductor": "Soft bare copper",
        "insulation": "TPE",
        "jacket": "TPE",
        "shield": False,
        "listing": "UL/cUL Listed",
        "extension": "1:5",
        "catalogPage": 10,
        "notes": "TPE throughout, insulation and jacket. E suffix series.",
    },
    {
        "id": "comm-control",
        "name": "Communications & Electronic Control Cords",
        "conductor": "Soft tinned copper",
        "insulation": "Polypropylene",
        "jacket": "PVC or Auta-Prene TPE",
        "shield": False,
        "listing": "UL Recognized AWM (cUL available)",
        "extension": "1:5",
        "catalogPage": 11,
        "notes": "Number ending in 5P = PVC jacket, 7P = Auta-Prene TPE jacket. Colors on request.",
    },
    {
        "id": "test-leads",
        "name": "Auta-Prene Test Leads",
        "conductor": "Soft tinned copper",
        "insulation": "TPE",
        "jacket": "Auta-Prene TPE",
        "shield": False,
        "listing": "UL Recognized",
        "extension": "1:5",
        "catalogPage": 11,
        "notes": "Single-conductor 5000V test leads. Stocked in 12 and 24 inch retracted lengths.",
    },
    {
        "id": "shielded-comm",
        "name": "PVC or Auta-Prene Shielded Cords",
        "conductor": "Soft tinned copper",
        "insulation": "Polypropylene",
        "jacket": "PVC or Auta-Prene TPE",
        "shield": True,
        "listing": "UL Recognized AWM (cUL available)",
        "extension": "1:5",
        "catalogPage": 12,
        "notes": "Each conductor individually served shielded with 36 AWG soft tinned copper, average 90% coverage. Conductors white and/or black. Capacitance values on request.",
    },
    {
        "id": "pvc-shielded",
        "name": "PVC Shielded Cords",
        "conductor": "Soft tinned copper",
        "insulation": "Polypropylene",
        "jacket": "PVC",
        "shield": True,
        "listing": "UL Recognized AWM (CSA available)",
        "extension": "1:5",
        "catalogPage": 13,
        "notes": "Overall served shield, 36 AWG soft tinned copper, average 90% coverage. Black jacket, colors on request. Capacitance values on request.",
    },
    {
        "id": "pvc-miniature",
        "name": "PVC Miniature Cords",
        "conductor": "Soft tinned copper",
        "insulation": "Polypropylene",
        "jacket": "PVC",
        "shield": False,
        "listing": "UL Recognized AWM (cUL available)",
        "extension": "1:5",
        "catalogPage": 14,
        "notes": "28 AWG miniature cords, black jacket. Colors on request.",
    },
    {
        "id": "pvc-miniature-foil",
        "name": "PVC Miniature Cords with Foil Shield",
        "conductor": "Soft tinned copper",
        "insulation": "Polypropylene",
        "jacket": "PVC",
        "shield": True,
        "listing": "UL Recognized AWM (cUL available)",
        "extension": "1:5",
        "catalogPage": 14,
        "notes": "Overall foil shield, black jacket. Colors on request. Capacitance values on request.",
    },
]

ROWS = {
    # ---- p6 TPE Power Cords (TPR jacket) ----
    "tpe-power": [
        ("72180", 2, "18", "41/34", 105, "300V", "7A", "SVEO/SVTO", ".242", "7/8", L4, [0.35, 0.48, 0.76, 0.90]),
        ("72180W", 2, "18", "41/34", 105, "300V", "7A", "SVEO/SVTO", ".242", "7/8", L4, [0.30, 0.35, 0.52, 0.68]),
        ("73180", 3, "18", "41/34", 105, "300V", "7A", "SVEO/SVTO", ".260", "7/8", L4, [0.35, 0.36, 0.51, 0.67]),
        ("72181", 2, "18", "41/34", 105, "300V", "7A", "SJEOW/SJTOW", ".300", "1", L4, [0.48, 0.50, 0.70, 0.93]),
        ("73181", 3, "18", "41/34", 105, "300V", "7A", "SJEOW/SJTOW", ".308", "1 3/8", L4, [0.55, 0.80, 1.1, 1.5]),
        ("74181", 4, "18", "41/34", 105, "300V", "7A", "SJEOW/SJTOW", ".340", "1 3/8", L4, [0.64, 0.84, 1.2, 1.6]),
        ("75181", 5, "18", "41/34", 105, "300V", "7A", "SJEOW/SJTOW", ".385", "1 3/8", L4, [0.82, 0.90, 1.3, 1.8]),
        ("77181", 7, "18", "41/34", 105, "300V", "7A", "SJEOW/SJTOW", ".430", "1 5/8", L4, [0.85, 1.5, 2.2, 3.0]),
        ("73182", 3, "18", "41/34", 105, "600V", "7A", "SJEOW/STOW", ".375", "1 3/8", L4, [0.61, 0.86, 1.2, 1.6]),
        ("77182", 7, "18", "41/34", 105, "600V", "7A", "SJEOW/STOW", ".500", "1 7/8", L4, [1.4, 1.7, 2.5, 3.2]),
        ("710182", 10, "18", "41/34", 105, "600V", "7A", "SJEOW/STOW", ".590", "2 3/8", L4, [2.2, 2.8, 4.1, 5.4]),
    ],
    # ---- p7 TPR Power Cords ----
    "tpr-power": [
        ("72161", 2, "16", "65/34", 105, "300V", "10A", "SJEOW/SJTOW", ".300", "7/8", L4, [0.49, 0.55, 0.81, 1.2]),
        ("73161", 3, "16", "65/34", 105, "300V", "10A", "SJEOW/SJTOW", ".340", "1 3/8", L4, [0.65, 0.88, 2.3, 1.7]),
        ("73162", 3, "16", "65/34", 105, "600V", "10A", "SEOW/STOW", ".385", "1 1/2", L4, [0.73, 0.90, 1.3, 1.8]),
        ("74161", 4, "16", "65/34", 105, "300V", "10A", "SEOW/STOW", ".365", "1 3/8", L4, [0.82, 0.96, 1.4, 1.9]),
        ("74162", 4, "16", "65/34", 105, "600V", "10A", "SEOW/STOW", ".425", "1 1/2", L4, [1.2, 1.3, 1.9, 2.3]),
        ("75162", 5, "16", "65/34", 105, "600V", "10A", "SEOW/STOW", ".495", "1 5/8", L4, [1.5, 1.7, 2.9, 3.9]),
        ("76162", 6, "16", "65/34", 105, "600V", "10A", "SEOW/STOW", ".530", "2", L4, [1.8, 2.4, 3.5, 4.6]),
        ("77162", 7, "16", "65/34", 105, "600V", "10A", "SEOW/STOW", ".535", "2", L4, [1.9, 2.6, 3.6, 4.7]),
        ("78162", 8, "16", "65/34", 105, "600V", "10A", "SEOW/STOW", ".570", "2 1/8", L4, [2.1, 2.7, 3.6, 4.8]),
        ("73141", 3, "14", "41/30", 105, "300V", "10A", "SEOW/STOW", ".390", "1 9/16", L4, [1.1, 2.2, 3.2, 4.2]),
        ("73142", 3, "14", "41/30", 105, "600V", "12A", "SEOW/STOW", ".540", "2 1/8", L4, [1.9, 2.4, 3.5, 4.8]),
        ("74142", 4, "14", "41/30", 105, "600V", "12A", "SEOW/STOW", ".570", "2 1/8", L4, [2.3, 2.7, 4.0, 5.3]),
        ("75141", 5, "14", "41/30", 105, "300V", "12A", "SEOW/STOW", ".465", "1 3/8", L4, [1.9, 1.9, 2.3, 3.0]),
        ("77142", 7, "14", "41/30", 105, "600V", "12A", "SEOW/STOW", ".700", "2 3/8", L4, [2.1, 2.3, 3.4, 4.5]),
        ("72121", 2, "12", "65/30", 105, "300V", "12A", "SEOW/STOW", ".420", "1 1/2", L4, [1.3, 1.4, 2.2, 2.8]),
        ("73122", 3, "12", "65/30", 105, "600V", "20A", "SEOW/STOW", ".580", "2 3/8", L4, [2.36, 3.13, 4.61, 6.11]),
        ("74122", 4, "12", "65/30", 105, "600V", "20A", "SEOW/STOW", ".660", "2 3/8", L4, [2.82, 3.43, 5.16, 6.70]),
    ],
    # ---- p8-9 PVC Power Cords ----
    "pvc-power": [
        ("92180", 2, "18", "41/34", 105, "300V", "10A", "SVT", ".250", "7/8", L4, [0.31, 0.33, 0.48, 0.63]),
        ("92180W", 2, "18", "41/34", 105, "300V", "10A", "SVT", ".250", "7/8", L4, [0.41, 0.44, 0.64, 0.85]),
        ("93180", 3, "18", "41/34", 105, "300V", "10A", "SVT", ".260", "7/8", L4, [0.35, 0.36, 0.51, 0.67]),
        ("93180W", 3, "18", "41/34", 105, "300V", "10A", "SVT", ".260", "7/8", L4, [0.38, 0.39, 0.56, 0.73]),
        ("92181", 2, "18", "41/34", 105, "300V", "10A", "SJT", ".295", "1", L4, [0.38, 0.40, 0.57, 0.75]),
        ("92181W", 2, "18", "41/34", 105, "300V", "10A", "SJT", ".295", "1", L4, [0.40, 0.42, 0.60, 0.79]),
        ("93181", 3, "18", "41/34", 105, "300V", "10A", "SJT", ".330", "1 3/8", L4, [0.52, 0.70, 1.0, 1.4]),
        ("93181W", 3, "18", "41/34", 105, "300V", "10A", "SJT", ".330", "1 3/8", L4, [0.56, 0.75, 1.1, 1.5]),
        ("94181", 4, "18", "41/34", 105, "300V", "7A", "SJT", ".360", "1 3/8", L4, [0.60, 0.73, 1.2, 1.5]),
        ("94181W", 4, "18", "41/34", 105, "300V", "7A", "SJT", ".360", "1 3/8", L4, [0.68, 0.82, 1.2, 1.6]),
        ("95181", 5, "18", "41/34", 105, "300V", "5.6A", "SJT", ".440", "1 1/2", L4, [1.2, 1.2, 1.7, 2.3]),
        ("95181W", 5, "18", "41/34", 105, "300V", "5.6A", "SJT", ".440", "1 1/2", L4, [1.1, 1.1, 1.5, 2.1]),
        ("92161", 2, "16", "65/34", 105, "300V", "13A", "SJT", ".315", "1 1/8", L4, [0.47, 0.52, 0.77, 1.0]),
        ("92161W", 2, "16", "65/34", 105, "300V", "13A", "SJT", ".315", "1 1/8", L4, [0.49, 0.54, 0.80, 1.1]),
        ("93161", 3, "16", "65/34", 105, "300V", "13A", "SJT", ".355", "1 3/8", L4, [0.68, 0.83, 1.2, 1.6]),
        ("93161W", 3, "16", "65/34", 105, "300V", "13A", "SJT", ".355", "1 3/8", L4, [0.67, 0.82, 1.2, 1.6]),
        ("94161", 4, "16", "65/34", 105, "300V", "10A", "SJT", ".410", "1 5/8", L4, [0.92, 1.4, 2.1, 2.8]),
        ("94161W", 4, "16", "65/34", 105, "300V", "10A", "SJT", ".410", "1 5/8", L4, [0.90, 1.4, 2.1, 2.8]),
        ("93141", 3, "14", "41/30", 105, "300V", "15A", "SJT", ".390", "1 9/16", L4, [1.1, 2.1, 3.1, 4.1]),
        ("93141W", 3, "14", "41/30", 105, "300V", "15A", "SJT", ".390", "1 9/16", L4, [1.1, 2.1, 3.2, 4.2]),
        ("93121", 3, "12", "65/30", 105, "300V", "20A", "SJT", ".435", "1 5/8", L4, [1.7, 1.8, 2.6, 3.5]),
        ("93121W", 3, "12", "65/30", 105, "300V", "20A", "SJT", ".435", "1 5/8", L4, [1.8, 1.9, 2.8, 3.6]),
    ],
    # ---- p10 TPE Power Cords, TPE jacket (E series) ----
    "tpe-power-bare": [
        ("92180E", 2, "18", "41/34", 105, "300V", "10A", "SVEO/SVT", ".250", "7/8", L4, [0.41, 0.44, 0.64, 0.85]),
        ("93180E", 3, "18", "41/34", 105, "300V", "10A", "SVEO/SVT", ".260", "7/8", L4, [0.34, 0.34, 0.50, 0.66]),
        ("92181E", 2, "18", "41/34", 105, "300V", "10A", "SJEOOW/SJTOOW", ".295", "1", L4, [0.41, 0.41, 0.60, 0.80]),
        ("93181E", 3, "18", "41/34", 105, "300V", "10A", "SJEOOW/SJTOOW", ".330", "1 3/8", L4, [0.55, 0.78, 1.1, 1.5]),
        ("94181E", 4, "18", "41/34", 105, "300V", "7A", "SJEOOW/SJTOOW", ".350", "1 3/8", L4, [0.61, 0.77, 1.1, 1.5]),
        ("92161E", 2, "16", "65/34", 105, "300V", "13A", "SJEOOW/SJTOOW", ".315", "1 1/8", L4, [0.52, 0.58, 0.85, 1.1]),
        ("93161E", 3, "16", "65/34", 105, "300V", "13A", "SJEOOW/SJTOOW", ".355", "1 3/8", L4, [0.65, 0.80, 1.2, 1.5]),
        ("94161E", 4, "16", "65/34", 105, "300V", "10A", "SJEOOW/SJTOOW", ".410", "1 5/8", L4, [0.90, 1.0, 1.5, 2.0]),
        ("93141E", 3, "14", "41/30", 105, "300V", "15A", "SJEOOW/SJTOOW", ".390", "1 1/2", L4, [1.1, 2.1, 3.1, 4.1]),
    ],
    # ---- p11 Communications & Electronic Control Cords (5P PVC / 7P TPE) ----
    "comm-control": [
        ("22235P", 2, "23", "21/36", 80, "300V", "1A", "AWM", ".180", "5/8", L4, [0.17, 0.18, 0.27, 0.35]),
        ("22237P", 2, "23", "21/36", 80, "300V", "1A", "AWM", ".180", "5/8", L4, [0.17, 0.18, 0.27, 0.35]),
        ("23235P", 3, "23", "21/36", 80, "300V", "1A", "AWM", ".190", "11/16", L4, [0.19, 0.22, 0.32, 0.43]),
        ("23237P", 3, "23", "21/36", 80, "300V", "1A", "AWM", ".190", "11/16", L4, [0.20, 0.23, 0.34, 0.45]),
        ("24235P", 4, "23", "21/36", 80, "300V", "1A", "AWM", ".200", "11/16", L4, [0.21, 0.22, 0.33, 0.44]),
        ("24237P", 4, "23", "21/36", 80, "300V", "1A", "AWM", ".200", "11/16", L4, [0.21, 0.22, 0.33, 0.44]),
        ("25235P", 5, "23", "21/36", 80, "300V", "1A", "AWM", ".215", "3/4", L4, [0.22, 0.24, 0.35, 0.46]),
        ("25237P", 5, "23", "21/36", 80, "300V", "1A", "AWM", ".215", "3/4", L4, [0.25, 0.26, 0.38, 0.50]),
        ("26235P", 6, "23", "21/36", 80, "300V", "1A", "AWM", ".230", "7/8", L4, [0.27, 0.33, 0.48, 0.64]),
        ("26237P", 6, "23", "21/36", 80, "300V", "1A", "AWM", ".230", "7/8", L4, [0.27, 0.33, 0.48, 0.64]),
        ("27235P", 7, "23", "21/36", 80, "300V", "1A", "AWM", ".230", "7/8", L4, [0.28, 0.33, 0.48, 0.64]),
        ("27237P", 7, "23", "21/36", 80, "300V", "1A", "AWM", ".230", "7/8", L4, [0.28, 0.33, 0.49, 0.65]),
        ("28235P", 8, "23", "21/36", 80, "300V", "1A", "AWM", ".245", "7/8", L4, [0.31, 0.34, 0.50, 0.67]),
        ("28237P", 8, "23", "21/36", 80, "300V", "1A", "AWM", ".245", "7/8", L4, [0.33, 0.37, 0.54, 0.71]),
        ("210235P", 10, "23", "21/36", 80, "300V", "1A", "AWM", ".280", "15/16", L4, [0.46, 0.46, 0.68, 0.89]),
        ("210237P", 10, "23", "21/36", 80, "300V", "1A", "AWM", ".280", "15/16", L4, [0.47, 0.47, 0.69, 0.92]),
        ("212235P", 12, "23", "21/36", 80, "300V", "1A", "AWM", ".285", "1", L4, [0.48, 0.52, 0.76, 1.1]),
        ("212237P", 12, "23", "21/36", 80, "300V", "1A", "AWM", ".285", "1", L4, [0.50, 0.54, 0.80, 1.1]),
        ("215235P", 15, "23", "21/36", 80, "300V", "1A", "AWM", ".310", "1 1/16", L4, [0.58, 0.62, 0.91, 1.2]),
        ("215237P", 15, "23", "21/36", 80, "300V", "1A", "AWM", ".310", "1 1/16", L4, [0.63, 0.67, 1.2, 1.3]),
    ],
    # ---- p11 Auta-Prene Test Leads ----
    "test-leads": [
        ("91207", 1, "20", "41/36", 105, "5000V", "4A", "Test lead", ".165", "5/8", [12, 24], [0.17, 0.19]),
        ("91208R", 1, "20", "41/36", 105, "5000V", "4A", "Test lead", ".165", "5/8", [12, 24], [0.17, 0.19]),
    ],
    # ---- p12 PVC or Auta-Prene Shielded Cords (individually served) ----
    "shielded-comm": [
        ("31235P", 1, "23", "21/36", 80, "300V", "1A", "AWM", ".165", "5/8", L4, [0.16, 0.19, 0.28, 0.37]),
        ("31237P", 1, "23", "21/36", 80, "300V", "1A", "AWM", ".165", "5/8", L4, [0.18, 0.20, 0.30, 0.40]),
        ("32235P", 2, "23", "21/36", 80, "300V", "1A", "AWM", ".210", "3/4", L4, [0.26, 0.29, 0.43, 0.57]),
        ("32237P", 2, "23", "21/36", 80, "300V", "1A", "AWM", ".210", "3/4", L4, [0.26, 0.29, 0.43, 0.57]),
        ("33235P", 3, "23", "21/36", 80, "300V", "1A", "AWM", ".205", "3/4", L4, [0.21, 0.24, 0.36, 0.48]),
        ("33237P", 3, "23", "21/36", 80, "300V", "1A", "AWM", ".205", "3/4", L4, [0.23, 0.25, 0.37, 0.49]),
        ("34235P", 4, "23", "21/36", 80, "300V", "1A", "AWM", ".230", "7/8", L4, [0.30, 0.37, 0.54, 0.71]),
        ("34237P", 4, "23", "21/36", 80, "300V", "1A", "AWM", ".230", "7/8", L4, [0.29, 0.35, 0.52, 0.68]),
    ],
    # ---- p13 PVC Shielded Cords (overall served) ----
    "pvc-shielded": [
        ("62235P", 2, "23", "21/36", 80, "300V", "1A", "AWM", ".180", "11/16", L4, [0.18, 0.22, 0.33, 0.43]),
        ("63235P", 3, "23", "21/36", 80, "300V", "1A", "AWM", ".190", "11/16", L4, [0.22, 0.24, 0.36, 0.47]),
        ("64235P", 4, "23", "21/36", 80, "300V", "1A", "AWM", ".205", "11/16", L4, [0.23, 0.24, 0.35, 0.47]),
        ("65235P", 5, "23", "21/36", 80, "300V", "1A", "AWM", ".215", "3/4", L4, [0.31, 0.32, 0.48, 0.63]),
        ("66235P", 6, "23", "21/36", 80, "300V", "1A", "AWM", ".230", "7/8", L4, [0.32, 0.38, 0.57, 0.75]),
        ("67235P", 7, "23", "21/36", 80, "300V", "1A", "AWM", ".235", "7/8", L4, [0.34, 0.40, 0.59, 0.78]),
        ("68235P", 8, "23", "21/36", 80, "300V", "1A", "AWM", ".245", "7/8", L4, [0.38, 0.42, 0.61, 0.81]),
    ],
    # ---- p14 PVC Miniature Cords ----
    "pvc-miniature": [
        ("22285P", 2, "28", "7/36", 80, "300V", "0.5A", "AWM", ".150", "1/2", L4, [0.09, 0.10, 0.14, 0.19]),
        ("23285P", 3, "28", "7/36", 80, "300V", "0.5A", "AWM", ".150", "1/2", L4, [0.09, 0.10, 0.14, 0.20]),
        ("24285P", 4, "28", "7/36", 80, "300V", "0.5A", "AWM", ".155", "1/2", L4, [0.09, 0.10, 0.14, 0.20]),
        ("25285P", 5, "28", "7/36", 80, "300V", "0.5A", "AWM", ".165", "9/16", L4, [0.10, 0.11, 0.16, 0.21]),
        ("26285P", 6, "28", "7/36", 80, "300V", "0.5A", "AWM", ".180", "5/8", L4, [0.15, 0.16, 0.23, 0.31]),
        ("27285P", 7, "28", "7/36", 80, "300V", "0.5A", "AWM", ".180", "5/8", L4, [0.17, 0.18, 0.26, 0.34]),
        ("28285P", 8, "28", "7/36", 80, "300V", "0.5A", "AWM", ".200", "5/8", L4, [0.18, 0.19, 0.24, 0.32]),
        ("210285P", 10, "28", "7/36", 80, "300V", "0.5A", "AWM", ".235", "7/8", L4, [0.23, 0.27, 0.39, 0.52]),
    ],
    # ---- p14 PVC Miniature Cords with Foil Shield ----
    "pvc-miniature-foil": [
        ("82285P", 2, "28", "7/36", 80, "300V", "0.5A", "AWM", ".155", "1/2", L4, [0.12, 0.15, 0.17, 0.22]),
        ("83285P", 3, "28", "7/36", 80, "300V", "0.5A", "AWM", ".160", "1/2", L4, [0.12, 0.15, 0.18, 0.23]),
        ("84285P", 4, "28", "7/36", 80, "300V", "0.5A", "AWM", ".180", "9/16", L4, [0.13, 0.15, 0.19, 0.24]),
        ("85285P", 5, "28", "7/36", 80, "300V", "0.5A", "AWM", ".180", "9/16", L4, [0.14, 0.15, 0.22, 0.25]),
        ("86285P", 6, "28", "7/36", 80, "300V", "0.5A", "AWM", ".190", "11/16", L4, [0.18, 0.20, 0.29, 0.39]),
        ("87285P", 7, "28", "7/36", 80, "300V", "0.5A", "AWM", ".195", "11/16", L4, [0.19, 0.21, 0.31, 0.41]),
        ("88285P", 8, "28", "7/36", 80, "300V", "0.5A", "AWM", ".205", "3/4", L4, [0.20, 0.22, 0.32, 0.42]),
        ("810285P", 10, "28", "7/36", 80, "300V", "0.5A", "AWM", ".235", "7/8", L4, [0.22, 0.26, 0.38, 0.51]),
    ],
}

products = []
seen = set()
for cat in CATEGORIES:
    for (cat_no, cond, awg, strand, temp, volt, amps, typ, cond_od, coil_od, lens, wts) in ROWS[cat["id"]]:
        assert cat_no not in seen, cat_no
        seen.add(cat_no)
        assert len(lens) == len(wts), cat_no
        products.append({
            "catNo": cat_no,
            "category": cat["id"],
            "awg": awg,
            "conductors": cond,
            "type": typ,
            "voltage": volt,
            "ampRating": amps,
            "retractedLengths": lens,
            "strand": strand,
            "tempC": temp,
            "conductorOD": cond_od,
            "coilOD": coil_od,
            "weightLbs": wts,
        })

out = {"categories": CATEGORIES, "products": products}
Path("catalog/data/products.json").write_text(json.dumps(out, indent=2) + "\n")
print(len(CATEGORIES), "categories,", len(products), "products")
for cat in CATEGORIES:
    print(f"  {cat['id']:20} {len(ROWS[cat['id']]):3}")
