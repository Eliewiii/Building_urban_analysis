"""
Reference values for the KPIs for the different types of scenarios
NB: The values are given for a 50 (or 60, need to decide) years lifetime, some values are dependant on the lifetime
"""

"""
"kpis": {
        "eroi": self.eroi,
        "primary energy payback time [year]": self.primary_energy_payback_time,
        "ghg emissions intensity [kgCo2eq/kWh]": self.ghg_emissions_intensity,
        "ghg emissions payback time [year]": self.ghg_emissions_payback_time,
        "harvested energy density [Kwh/m2]": self.harvested_energy_density,
        "net energy compensation": self.net_energy_compensation,
        "economical payback time [year]": self.economical_payback_time,
        "economical roi": self.economical_roi,
        "net economical benefit [$]": self.net_economical_benefit,
        "net economical benefit density [$/m2]": self.net_economical_benefit_density
    }
"""

###############################
# Environmental scenarios
###############################

# Primary Energy related KPIs
EROI_REF_ENV = 2.5  # Energy Return on Investment
EROI_MIN_ENV = 2.0
PE_PBT_PT_REF_ENV = 10  # Primary energy payback time profitability threshold [year]
PE_PBT_PT_MAX_ENV = 20
PE_PBT_LI_REF_ENV = 18  # Primary energy payback time Lifetime Investment [year]
PE_PBT_LI_MAX_ENV = 30

# GHG emissions related KPIs
GHGI_REF_ENV = 0.1  # GHG emissions intensity [kgCO2eq/kWh]
GHGI_MAX_ENV = 0.150
GHG_PBT_PT_REF_ENV = 10  # GHG emissions payback time profitability threshold [year]
GHG_PBT_PT_MAX_ENV = 20
GHG_PBT_LI_REF_ENV = 10  # GHG emissions payback time Lifetime Investment [year]
GHG_PBT_LI_MAX_ENV = 30

# Economical KPIs
ECO_ROI_REF_ENV = 1.5  # Economical Return on Investment
ECO_ROI_MIN_ENV = 1.2
ECO_PBT_PT_REF_ENV = 10  # Economical payback time profitability threshold [year]
ECO_PBT_PT_REF_ENV = 30
ECO_PBT_LI_REF_ENV = 18  # Economical payback time Lifetime Investment [year]
ECO_PBT_LI_MAX_ENV = 40
NEBD_ZONE_REF_ENV = 80  # Net Economical Benefit Density Zone [$/m2]
NEBD_CA_REF_ENV = 50  # Net Economical Benefit Density Conditionned apartment [$/m2]

# Electricity Harvesting related KPIs
HED_ZONE_REF_ENV = 4000  # Harvested energy density Zone [Kwh/m2]   todo: check this value
HED_CA_REF_ENV = 4000  # Harvested energy density Conditionned apartment [Kwh/m2]
NEC_REF_ENV = 0.5  # Net Energy Compensation
