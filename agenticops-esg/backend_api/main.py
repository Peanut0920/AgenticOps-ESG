@app.get("/api/report/structured")
async def get_structured_report():
    """
    Returns the ESG report in a structured, sectioned format
    for easy frontend rendering.
    """
    if not current_state:
        return {}

    packet = current_state.get("esg_report_packet", {})
    
    # Extract data with fallbacks
    bursa = packet.get("bursa_malaysia", {})
    mcmc = packet.get("mcmc", {})
    gri = packet.get("gri_305", "")
    sasb = packet.get("sasb", {})

    # Build structured response
    return {
        "sections": [
            {
                "id": "bursa",
                "title": "Bursa Malaysia / TCFD",
                "icon": "fa-gavel",
                "color": "yellow",
                "fields": [
                    {"label": "Narrative", "value": bursa.get("narrative", "N/A"), "type": "text"},
                    {"label": "Transition Risk", "value": bursa.get("tcfd_metrics", {}).get("transition_risk", "N/A")},
                    {"label": "Physical Risk", "value": bursa.get("tcfd_metrics", {}).get("physical_risk", "N/A")},
                    {"label": "CAPEX Deferred", "value": bursa.get("tcfd_metrics", {}).get("capex_deferred", "N/A")},
                    {"label": "Emissions Reduction (tCO2e)", "value": bursa.get("tcfd_metrics", {}).get("emissions_reduction", 0)},
                ]
            },
            {
                "id": "mcmc",
                "title": "MCMC Technical Code",
                "icon": "fa-shield-halved",
                "color": "red",
                "fields": [
                    {"label": "PUE Certified", "value": mcmc.get("pue_certified", "N/A")},
                    {"label": "Resiliency Score", "value": mcmc.get("resiliency_score", "N/A")},
                    {"label": "Data Sovereignty", "value": mcmc.get("data_sovereignty_status", "N/A")},
                    {"label": "Energy Efficiency Rating", "value": mcmc.get("energy_efficiency_rating", "N/A")},
                ]
            },
            {
                "id": "gri",
                "title": "GRI 305 (Emissions)",
                "icon": "fa-leaf",
                "color": "white",
                "fields": [
                    {"label": "Scope 2 (Location‑based)", "value": gri.get("scope_2_location_based", "N/A") if isinstance(gri, dict) else gri},
                    {"label": "Scope 2 (Market‑based)", "value": gri.get("scope_2_market_based", "N/A") if isinstance(gri, dict) else "N/A"},
                    {"label": "Reduction Method", "value": gri.get("reduction_method", "N/A") if isinstance(gri, dict) else "N/A"},
                ]
            },
            {
                "id": "sasb",
                "title": "SASB TC‑HW / TC‑TL",
                "icon": "fa-microchip",
                "color": "yellow",
                "fields": [
                    {"label": "Total Energy (GWh)", "value": sasb.get("TC-HW-130a.1", {}).get("total_energy_consumed_gwh", "N/A")},
                    {"label": "Grid Electricity (%)", "value": sasb.get("TC-HW-130a.1", {}).get("grid_electricity_pct", "N/A")},
                    {"label": "Renewable (%)", "value": sasb.get("TC-HW-130a.1", {}).get("renewable_pct", "N/A")},
                    {"label": "PUE Weighted Avg", "value": sasb.get("TC-HW-130a.1", {}).get("pue_weighted_avg", "N/A")},
                    {"label": "E‑waste Recycled (kg)", "value": sasb.get("TC-TL-150a.1", {}).get("ewaste_recycled_kg", "N/A")},
                    {"label": "E‑waste Avoided (kg)", "value": sasb.get("TC-TL-150a.1", {}).get("ewaste_avoided_kg", "N/A")},
                    {"label": "Recycling Rate (%)", "value": sasb.get("TC-TL-150a.1", {}).get("recycling_rate_pct", "N/A")},
                ]
            }
        ],
        "audit_provenance": packet.get("audit_provenance", [])
    }