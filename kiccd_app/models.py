# Utility function to get the username of the current Django user
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.contrib.auth.models import User 
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class Pool(models.Model):
    IC_STATUS = {
        "Established": "Established",
        "Invasion": "Invasion",
        "Presence": "Presence",
        "Not Present": "Not Present",
        "Extirpated": "Extirpated",
        "Unknown": "Unknown",
        "NA": "N/A",
    }
    pool_id = models.IntegerField("ID", primary_key=True, unique=True, blank=False, null=False, db_comment='ID number of a pool in the Ohio River.')
    name = models.CharField("Name", max_length=25, blank=False, null=False, db_comment='Full name of the OHR pool.')
    abbrev = models.CharField("Abbrev", max_length=5, blank=True, null=True, db_comment='Four letter abbreviation of the OHR pool.')
    lat = models.DecimalField("Mid-Pt LAT", max_digits=8, decimal_places=5, blank=True, null=True, db_comment='Latitude of the pool halfway point.')
    lon = models.DecimalField("Mid-Pt LON", max_digits=8, decimal_places=5, blank=True, null=True, db_comment='Longitude of the pool halfway point.')
    midpoint_rm = models.DecimalField("Midpoint RM", max_digits=4, decimal_places=1, blank=True, null=True, db_comment='River mile (RM) of the pool halfway point.')
    length_mi = models.DecimalField("Pool Length (mi)", max_digits=5, decimal_places=1, blank=True, null=True, db_comment='Total Length of the pool in miles.')
    dam_rm = models.DecimalField("Dam RM", max_digits=5, decimal_places=1, blank=True, null=True, db_comment='River mile (RM) of the dam creating the pool.')
    dam_lat = models.DecimalField("Dam LAT", max_digits=8, decimal_places=5, blank=True, null=True, db_comment='Latitude of the dam creating the pool')
    dam_lon = models.DecimalField("Dam LON", max_digits=8, decimal_places=5, blank=True, null=True, db_comment='Longitude of the dam creating the pool')
    bhc_status = models.CharField("Bighead Carp", max_length=25, blank=True, null=True, choices=IC_STATUS.items(), db_comment='Status of Bighead Carp in the pool.')
    blc_status = models.CharField("Black Carp", max_length=25, blank=True, null=True, choices=IC_STATUS.items(), db_comment='Status of Black Carp in the pool.')
    grc_status = models.CharField("Grass Carp", max_length=25, blank=True, null=True, choices=IC_STATUS.items(), db_comment='Status of Grass Carp in the pool.')
    svc_status = models.CharField("Silver Carp", max_length=25, blank=True, null=True, choices=IC_STATUS.items(), db_comment='Status of Silver Carp in the pool.')
    last_update= models.DateTimeField(auto_now=True, db_comment='Date-time of creation or update.')
    boundary = models.JSONField("Boundary", null=True, blank=True, db_comment='GeoJSON Polygon or MultiPolygon defining the pool boundary.')

    class Meta:
        db_table = 'pools'
        db_table_comment = 'Information on the pools that make up the mainstem Ohio River'
        verbose_name = '(Lookup) Pool'
        verbose_name_plural = '(Lookup) Pools'

    def __str__(self):
        return self.name


class Basin(models.Model):
    basin_id = models.AutoField("ID", primary_key=True, db_comment='ID for a river basin connected to an Invasive Carp Project.')
    name = models.CharField("Name", max_length=50, blank=False, null=False, db_comment='Full name of the river basin.')
    abbrev = models.CharField("Abbrev", max_length=10, blank=False, null=False, db_comment='Three letter abbreviation of the river basin.')
    last_update = models.DateTimeField(auto_now=True, db_comment='Date-time of creation or update.')
    boundary = models.JSONField("Boundary", null=True, blank=True, db_comment='GeoJSON Polygon or MultiPolygon defining the basin boundary.')

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.title()
        if self.abbrev:
            self.abbrev = self.abbrev.upper()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'basins'
        db_table_comment = 'River basins with ongoing Invasive Carp research projects.'
        verbose_name = '(Lookup) Basin'
        verbose_name_plural = '(Lookup) Basins'

    def __str__(self):
        return self.name


class Trib(models.Model):
    trib_id = models.AutoField("ID", primary_key=True, db_comment='ID representing a tributary or area where Invasive Carp Research is conducted.')
    basin = models.ForeignKey(Basin, on_delete=models.PROTECT, db_comment='ID of the higher-level river basin the tributary/area connected to.')
    pool = models.ForeignKey(Pool, on_delete=models.PROTECT, db_comment='ID of pool where the tributary/area is located.')
    name = models.CharField("Name", max_length=100, blank=False, null=False, db_comment='Name of the tributary or area.')
    lat = models.DecimalField("Latitude", max_digits=9, decimal_places=6, blank=True, null=True, db_comment='Latitude of the tributarys confluence.')
    lon = models.DecimalField("Longitude", max_digits=9, decimal_places=6, blank=True, null=True, db_comment='Longitude of the tributarys confluence.')
    rm = models.DecimalField("River Mile", max_digits=5, decimal_places=1, blank=True, null=True, db_comment='River mile (RM) of the tributarys confluence.')
    last_update = models.DateTimeField(auto_now_add=True, db_comment='Date-time of creation.')
    boundary = models.JSONField("Boundary", null=True, blank=True, db_comment='GeoJSON Polygon or MultiPolygon defining the tributary boundary.')

    class Meta:
        db_table = 'tributaries'
        db_table_comment = 'A Tributary list used for research site categorization.'
        verbose_name = '(Lookup) Tributary'
        verbose_name_plural = '(Lookup) Tribs'

    def save(self, *args, **kwargs):
        # if self.name:
        #     self.name = self.name.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Huc12(models.Model):
    huc_id = models.AutoField("ID", primary_key=True, db_comment='ID representing the USGS HUC12 record.')
    huc12 = models.CharField("HUC12", max_length=11, blank=False, null=False, db_comment='Official USGS ID number (11-digits) for the HUC12 location.')
    huc12_name = models.CharField("Name", max_length=100, blank=False, null=False, db_comment='Official name of the HUC12 location as designated by the USGS.')
    huc10 = models.CharField("HUC10", max_length=9, blank=False, null=False, db_comment='Official USGS ID number (9-digits) for the HUC10 location that the HUC12 belongs to.')
    huc10_name = models.CharField("HUC10 Name", max_length=100, blank=False, null=False, db_comment='Name of the HUC10 location that the HUC12 belongs to.')
    huc8 = models.CharField("HUC8", max_length=7, blank=False, null=False, db_comment='Official USGS ID number (7-digits) for the HUC8 location that the HUC12 belongs to.')
    huc8_name = models.CharField("HUC8 Name", max_length=100, blank=False, null=False, db_comment='Name of the HUC8 location that the HUC12 belongs to.')
    huc12_acres = models.DecimalField("Area_acres", max_digits=10, decimal_places=2, blank=True, null=True, db_comment='Area of the HUC12 in acres.')
    huc12_sqkm = models.DecimalField("Area_sqkm", max_digits=10, decimal_places=2, blank=True, null=True, db_comment='Area of the HUC12 in square kilometers.')
    boundary = models.JSONField("Boundary", null=True, blank=True, db_comment='GeoJSON Polygon or MultiPolygon defining the HUC12 boundary.')
    last_update = models.DateTimeField(auto_now_add=True, db_comment='Date-time of creation.')

    class Meta:
        db_table = 'huc12'
        db_table_comment = 'A list of the names and boundaries for all USGS HUC12 locations within Kentucky.'
        verbose_name = '(Lookup) HUC12_USGS'
        verbose_name_plural = '(Lookup) HUC12_USGS'

    def save(self, *args, **kwargs):
        # if self.huc12_name:
        #     self.huc12_name = self.huc12_name.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.huc12_name} ({self.huc12})"


class RiverMile(models.Model):
    rm_id = models.AutoField("ID", primary_key=True, db_comment='ID for a river mile location.')
    mile = models.DecimalField("River Mile", max_digits=6, decimal_places=1, blank=False, null=False, db_comment='River mile value for the location.')
    latitude = models.DecimalField("Latitude", max_digits=9, decimal_places=6, blank=False, null=False, db_comment='Latitude coordinate for the river mile location.')
    longitude = models.DecimalField("Longitude", max_digits=9, decimal_places=6, blank=False, null=False, db_comment='Longitude coordinate for the river mile location.')
    basin = models.ForeignKey("Basin", on_delete=models.PROTECT, blank=False, null=False, db_comment='Foreign key to the basin for the river mile location.')
    pool = models.ForeignKey("Pool", on_delete=models.PROTECT, blank=False, null=False, db_comment='Foreign key to the pool for the river mile location.')
    rm_point = models.JSONField("Point", blank=True, null=True, db_comment='GeoJSON point for the river mile location.')
    last_update = models.DateTimeField(auto_now=True, db_comment='Date-time of creation or update.')

    class Meta:
        db_table = 'river_mile'
        db_table_comment = 'River mile locations within the Ohio River and Mississippi Basins.'
        verbose_name = '(Lookup) River Mile'
        verbose_name_plural = '(Lookup) River Miles'

    def __str__(self):
        return f"RM #: {self.mile}"


class State(models.Model):
    state_id = models.IntegerField("ID", primary_key=True, unique=True, blank=False, null=False, db_comment='ID for a state within the OH River Basin.')
    name = models.CharField("Name", max_length=15, blank=False, null=False, db_comment='Full name of the ORB state.')
    abbrev = models.CharField("Abbrev", max_length=2, blank=True, null=True, db_comment='Two letter abbreviation of the ORB state.')
    last_update = models.DateTimeField(auto_now=True, db_comment='Date-time of creation or update.')

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.title()
        if self.abbrev:
            self.abbrev = self.abbrev.upper()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'states'
        db_table_comment = "Information on states located within Ohio River Basin (ORB)"
        verbose_name = '(Lookup) State'
        verbose_name_plural = '(Lookup) States'

    def __str__(self):
        return self.abbrev


class Gear(models.Model):
    gear_id = models.AutoField("ID", primary_key=True, db_comment='ID for a fish sampling gear type used in ORB Invasive Carp Projects.')
    name = models.CharField("Name", max_length=55, blank=False, null=False, db_comment='Name of the fish sampling gear.')
    code = models.SmallIntegerField("Agency Code", blank=True, null=True, db_comment='Official KDFWR code number for the gear type.')
    last_update = models.DateTimeField(auto_now=True, db_comment='Date-time of creation or update.')

    class Meta:
        db_table = 'gear'
        db_table_comment = 'Specific gear types used to sample fish in lakes, rivers and/or streams. Adapted from KFAS.'
        verbose_name = '(Lookup) Gear'
        verbose_name_plural = '(Lookup) Gear'

    def __str__(self):
        return self.name


class Partner(models.Model):
    PART_TYPE = {
        "Agency": "Agency",
        "University": "University",
        "Military": "Military",
        "Non-Profit": "Non-Profit",
        "Commercial": "Commercial",
        "Unknown": "Unknown",
    }
    
    PART_LEVEL = {
        "State": "State",
        "Federal": "Federal",
        "NA": "Not Applicable",
        "Unknown": "Unknown",
    }

    partner_id = models.AutoField("ID", primary_key=True, unique=True, blank=False, null=False, db_comment='ID for the agency or instituion that collaborates on ORB Invasive Carp research.')
    abbrev = models.CharField("Abbrev", max_length=5, blank=False, null=False, db_comment='Abbreviation of the agency or institution.')
    name = models.CharField("Name", max_length=75, blank=False, null=False, db_comment='Full name of the agency or institution.')
    type = models.CharField("Type", max_length=15, blank=True, null=True, choices=PART_TYPE.items(), db_comment='Type of the agency or institution.')
    level = models.CharField("Level", max_length=15, blank=True, null=True, choices=PART_LEVEL.items(), db_comment='Level of the agency or institution.')
    last_update = models.DateTimeField(auto_now=True, db_comment='Date-time of creation or update.')

    class Meta:
        db_table = 'partners'
        db_table_comment = 'Agencies, universities and other groups collaborating on OH River Invasive Carp research.'
        verbose_name = '(Lookup) Partner'
        verbose_name_plural = '(Lookup) Partners'

    def save(self, *args, **kwargs):
        if self.abbrev:
            self.abbrev = self.abbrev.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.abbrev


class Office(models.Model):
    office_id = models.AutoField("ID", primary_key=True, db_comment='ID for an office with staff working in Invasive Carp research.')
    name = models.CharField("Name", max_length=60, blank=False, null=False, db_comment='Full office name.')
    abbrev = models.CharField("Abbrev", max_length=12, blank=True, null=True, db_comment='Abbreviation for the office.')
    agency = models.ForeignKey(Partner, on_delete=models.PROTECT, db_comment="ID of the office's agency.")
    last_update = models.DateTimeField(auto_now=True, db_comment='Date-time of creation or update.')

    class Meta:
        db_table = 'offices'
        db_table_comment = "Offices with staff that work in IC research."
        ordering = ['name']
        verbose_name = '(Lookup) Office'
        verbose_name_plural = '(Lookup) Offices'

    def __str__(self):
        return self.name


class FishSex(models.Model):
    sx_id = models.IntegerField("ID", primary_key=True, unique=True, blank=False, null=False, db_comment='ID referencing the sex of fish sampled from the ORB.')
    name = models.CharField("Name", max_length=10, blank=False, null=False, db_comment='Full name for fish sex.')
    abbrev = models.CharField("Abbrev.", max_length=3, blank=False, null=False, db_comment='Abbreviation for the fish sex.')

    class Meta:
        db_table = 'fish_sex'
        db_table_comment = 'Sex of fish sampled for Invasive Carp research in the OH River Basin (ORB).'
        verbose_name = '(Lookup) Fish Sex'
        verbose_name_plural = '(Lookup) Fish Sex'

    def __str__(self):
        return self.abbrev


class Project(models.Model):
    project_id = models.IntegerField("ID", primary_key=True, unique=True, blank=False, null=False, db_comment='ID representing the Ohio River Basin (ORB) Invasive Carp Projects.')
    name = models.CharField("Name", max_length=64, blank=False, null=False, db_comment='Name of the ORB Invasive Carp Project.')
    description = models.TextField("Description", blank=True, null=True, db_comment='Additional info about the ORB Invasive Carp Project.')
    last_update = models.DateTimeField(auto_now=True, db_comment='Date-time of creation or update.')
    
    class Meta:
        db_table = 'projects'
        db_table_comment = 'Projects associated with field work being conducted in the Ohio River Basin (ORB) for Invasive Carp research .'
        ordering = ['project_id']
        verbose_name = '(Lookup) Project'
        verbose_name_plural = '(Lookup) Projects'
        
    def __str__(self):
        return self.name


class SiteType(models.Model):
    site_type_id = models.AutoField("ID", primary_key=True, unique=True, blank=False, null=False, db_comment='ID referencing site types used in ORB Invasive Carp research.')
    name = models.CharField("Name", max_length=64, blank=False, null=False, db_comment='Full name of the site type or habitat.')
    abbrev = models.CharField("Abbrev.", max_length=15, blank=False, null=False, db_comment='Abbreviation for the site type or habitat.')
    last_update = models.DateTimeField(auto_now=True, db_comment='Date-time of creation or update.')

    class Meta:
        db_table = 'site_type'
        db_table_comment = 'Site types and/or habitats in the OH River Basin (ORB) that are associated with Invasive Carp research.'
        verbose_name = '(Lookup) Site Type'
        verbose_name_plural = '(Lookup) Site Types'

    def __str__(self):
        return self.name


class SitePurpose(models.Model):
    site_purpose_id = models.AutoField("ID", primary_key=True, db_comment='ID number referencing the purpose of a site.')
    purpose = models.CharField("Site Purpose", max_length=75, blank=False, null=False, db_comment='The reason a site was selected for an Invasive Carp Project.')
    last_update = models.DateTimeField(auto_now=True, db_comment='Date-time of creation or update.')

    class Meta:
        db_table = 'site_purpose'
        db_table_comment = 'Purposes for any sites associated with the OHR Invasive Carp research efforts.'
        verbose_name = '(Lookup) Site Purpose'
        verbose_name_plural = '(Lookup) Site Purposes'

    def __str__(self):
        return self.purpose


class FishSpecies(models.Model):
    TROPHIC_LEVELS = {
        "Herbivore":"Herbivore",
        "Benthivore":"Benthivore",
        "Detritivore":"Detritivore",
        "Planktivore":"Planktivore",
        "Invertivore":"Invertivore",
        "Omnivore":"Omnivore",
        "Piscivore":"Piscivore",
        "Unknown": "Unknown",
    }

    spp_id = models.IntegerField("ID", primary_key=True, unique=True, blank=False, null=False, db_comment='ID number referencing a ORB fish species.')
    lookup = models.CharField("Lookup Name", max_length=100, blank=False, null=False, db_comment='Lookup name for the ORB fish species (CamelCase and no spaces).')
    name = models.CharField("Common Name", max_length=100, blank=False, null=False, db_comment='Full common name for the ORB fish species.')
    scientific_name = models.CharField("Scientific Name", max_length=100, blank=True, null=True, db_comment='Full scientific name for the ORB fish species')
    order_name = models.CharField("Order", max_length=55, blank=True, null=True, db_comment='Order name for the fish species.')
    family_name = models.CharField("Family", max_length=55, blank=True, null=True, db_comment='Family name for the fish species.')
    genus_name = models.CharField("Genus", max_length=55, blank=True, null=True, db_comment='Genus name for the fish species.')
    species_name = models.CharField("Species", max_length=55, blank=True, null=True, db_comment='Species name for the fish species.')
    abbrev = models.CharField("Abbrev.", max_length=6, blank=True, null=True, db_comment='Four letter abbreviation for the fish species.')
    trophic = models.CharField("Trophic Level", max_length=55, blank=True, null=True, choices=TROPHIC_LEVELS.items(), db_comment='Trophic level of the fish species.')
    ky_status = models.CharField("KY Status", max_length=20, blank=True, null=True, db_comment='Status (if any) of the fish species in Kentucky.')
    il_status = models.CharField("IL Status", max_length=20, blank=True, null=True, db_comment='Status (if any) of the fish species in Illinois.')
    in_status = models.CharField("IN Status", max_length=20, blank=True, null=True, db_comment='Status (if any) of the fish species in Indiana.')
    oh_status = models.CharField("OH Status", max_length=20, blank=True, null=True, db_comment='Status (if any) of the fish species in Ohio.')
    wv_status = models.CharField("WV Status", max_length=20, blank=True, null=True, db_comment='Status (if any) of the fish species in West Virginia.')
    pa_status = models.CharField("PA Status", max_length=20, blank=True, null=True, db_comment='Status (if any) of the fish species in Pennsylvania.')
    last_update = models.DateTimeField(auto_now=True, db_comment='Date-time of creation or update.')
    ranked = models.IntegerField("Rank", blank=True, null=True, default=0, db_default=0, db_comment='Numeric rank for sorting fish species.')
    targeted = models.BooleanField("Targeted", default=False, db_default=False, db_comment='Indicates if the species is targeted by invasive carp removal efforts.')

    class Meta:
        db_table = 'species'
        db_table_comment = 'Details on all freshwater fish species located within the OH River Basin (ORB). Adapted from KFAS.'
        verbose_name = '(Lookup) Fish Spp'
        verbose_name_plural = '(Lookup) Fish Spp'
        ordering = ['-ranked', 'name']

    def __str__(self):
        return f"{self.name}"


class County(models.Model):
    county_id = models.AutoField("County ID", primary_key=True, db_comment='ID number for a county located within the ORB.')
    state = models.ForeignKey(State, on_delete=models.PROTECT, db_comment='ID for the state that the county is located in.')
    name = models.CharField("County Name", max_length=30, blank=True, null=True, db_comment='Full name of the county.')
    last_update = models.DateTimeField(auto_now=True, db_comment='Date-time of creation or update.')

    class Meta:
        db_table = 'counties'
        db_table_comment = 'All counties located within the Ohio River Basin (ORB).'
        verbose_name = '(Lookup) County'
        verbose_name_plural = '(Lookup) Counties'

    def __str__(self):
        return f"{self.name} ({self.state.abbrev})"
    

class Crew(models.Model):
    crew_id = models.AutoField("Crew ID", primary_key=True, db_comment='ID number referencing crews that conduct field work in the ORB.')
    agency = models.ForeignKey(Partner, on_delete=models.PROTECT, db_comment='ID for the agency or institution.')
    office = models.ForeignKey(Office, on_delete=models.PROTECT, db_comment='ID for the office where the crew leader is based.')
    leader = models.CharField("Crew Leader", max_length=100, blank=True, null=True, db_comment='Full name of the crew leader.')
    added_on = models.DateTimeField(auto_now=True, db_comment='Date-time of creation or update.')

    class Meta:
        db_table = 'crews'
        db_table_comment = 'Field crews that conduct activities within the OH River Basin (ORB) for Invasive Carp research efforts.'
        verbose_name = '(Lookup) Crew'
        verbose_name_plural = '(Lookup) Crews'

    def __str__(self):
        return f"{self.leader} ({self.agency.abbrev})"


class Fisher(models.Model):
    fisher_id = models.AutoField("ID", primary_key=True, db_comment='ID number referencing a fisher that participated in the Invasive Carp Contract Fishing Program.')
    first_name = models.CharField("First Name", max_length=50, blank=False, null=False, db_comment='First name of contract fisher.')
    last_name = models.CharField("Last Name", max_length=50, blank=False, null=False, db_comment='Last name of contract fisher.')
    name = models.CharField("Full Name", max_length=55, blank=True, null=True, db_comment='Full name of contract fisher.')
    lookup = models.CharField("Lookup Name", max_length=50, blank=True, null=True, db_comment='Lookup name of contract fisher (First initial + Last name).')
    contracted = models.BooleanField("Contracted", blank=False, null=False, default=False, db_default=False, db_comment='Identifies if participant of contract fishing program.)')
    commercial_license = models.BooleanField("Comm. License", blank=False, null=False, default=True, db_default=True, db_comment='Identifies if participant has valid commercial fishing license.')
    last_update = models.DateTimeField(auto_now=True, db_comment='Date-time of creation or update.')


    class Meta:
        db_table = 'fishers'
        db_table_comment = 'Information on commercial and/or contract fishers that participate in Invasive Carp removal efforts.'
        verbose_name = '(Lookup) Fisher'
        verbose_name_plural = '(Lookup) Fishers'
    
    def save(self, *args, **kwargs):
        self.first_name = self.first_name.capitalize()
        self.last_name = self.last_name.capitalize()
        if not self.name: self.name = f"{self.first_name} {self.last_name}"
        if not self.lookup: self.lookup = f"{self.first_name[0].upper()}{self.last_name.lower()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CommercialFisher(models.Model):
    fisher_id = models.AutoField("ID", primary_key=True, db_comment='ID number referencing a commercial fisher participating in the Invasive Carp Harvest Program.')
    first_name = models.CharField("First Name", max_length=50, blank=False, null=False, db_comment='First name of commercial fisher.')
    last_name = models.CharField("Last Name", max_length=50, blank=False, null=False, db_comment='Last name of commercial fisher.')
    name = models.CharField("Full Name", max_length=55, blank=True, null=True, db_comment='Full name of commercial fisher.')
    lookup = models.CharField("Lookup Name", max_length=50, blank=True, null=True, db_comment='Lookup name of commercial fisher (First initial + Last name).')
    last_update = models.DateTimeField(auto_now=True, db_comment='Date-time of creation or update.')


    class Meta:
        db_table = 'ichp_fishers'
        db_table_comment = 'Information on fishers that participate in the Ohio River Invasive Carp Harvest Program.'
        verbose_name = '(ICHP) Fisher'
        verbose_name_plural = '(ICHP) Fishers'
    
    def save(self, *args, **kwargs):
        self.first_name = self.first_name.capitalize()
        self.last_name = self.last_name.capitalize()
        if not self.name: self.name = f"{self.first_name} {self.last_name}"
        if not self.lookup: self.lookup = f"{self.first_name[0].upper()}{self.last_name.lower()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Observer(models.Model):
    observer_id = models.AutoField("ID", primary_key=True, db_comment='ID number for an agency observer associated with the Invasive Carp Contract Fishing Program.')
    agency = models.ForeignKey(Partner, on_delete=models.PROTECT, db_comment='ID of the agency that employed the observer.')
    first_name = models.CharField("First Name", max_length=20, blank=False, null=False, db_comment='First name of the agency observer.')
    last_name = models.CharField("Last Name", max_length=20, blank=False, null=False, db_comment='Last name of the agency observer.')
    name = models.CharField("Full Name", max_length=30, blank=True, null=True, db_comment='Full name of the agency observer.')
    last_update = models.DateTimeField(auto_now=True, db_comment='Date-time of creation or update.')

    class Meta:
        db_table = 'observers'
        db_table_comment = 'Information on agency staff that monitor the fishing conducted for the Invasive Carp Contract Fishing Program.'
        verbose_name = '(CF) Observer'
        verbose_name_plural = '(CF) Observers'

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.capitalize()
        self.last_name = self.last_name.capitalize()
        if not self.name: self.name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Dates(models.Model):
    dates_id = models.AutoField("ID", primary_key=True, db_comment='ID number referencing a specific date.')
    ic_date = models.DateField("Date", blank=False, null=False, db_comment='Potential date for an ORB Invasive Carp field event.')
    cal_year = models.IntegerField("Calendar Year", blank=False, null=False, db_comment='Calendar year of the date.')
    fis_year = models.IntegerField("Fiscal Year", blank=False, null=False, db_comment='Fiscal year of the date.')
    ic_proj_year = models.IntegerField("Project Year", blank=False, null=False, db_comment='Year count for ORB Invasive Carp research.')
    cf_peak_season = models.IntegerField("CF Season", blank=False, null=False, db_comment='Contract fishing season that the date belongs to.')
    ic_season = models.CharField("Season", max_length=10, blank=False, null=False, db_comment='Season that the date belongs to.')
    cf_season = models.CharField("Season_2", max_length=10, blank=True, null=True, db_comment='Season breakdown for contract fishing only.')
    ic_month1 = models.IntegerField("Month No", blank=False, null=False, db_comment='Number of the month.')
    ic_month2 = models.CharField("Month", max_length=15, blank=False, null=False, db_comment='Full Name of the month.')
    ic_mon = models.CharField("Month Abbrev", max_length=5, blank=False, null=False, db_comment='Abbreviation of the month.')
    ic_weeknum = models.IntegerField("Week No", blank=False, null=False, db_comment='Week number the date belong to.')

    class Meta:
        db_table = 'ic_dates'
        db_table_comment = 'Date table covering the time periods that Invasive Carp Research was underway in the OH River Basin (ORB).'
        verbose_name = '(Lookup) Date Table'
        verbose_name_plural = '(Lookup) Date Table'

    def __str__(self):
        return str(self.ic_date)


class SampleSite(models.Model):
    site_id = models.AutoField("ID", primary_key=True, db_comment='ID number of the Invasive Carp sampling site.')
    site_code = models.CharField("Site Code", max_length=8, blank=True, null=True, db_comment='Lookup code (max 8 chars) for the sampling site.')
    name = models.CharField("Site Name", max_length=48, blank=False, null=False, db_comment='Full name (max 48 chars) for the sampling site.')
    latitude = models.DecimalField("Site LAT", max_digits=8, decimal_places=5, blank=True, null=True, db_comment='Latitude of the sampling site location.')
    longitude = models.DecimalField("Site LON", max_digits=8, decimal_places=5, blank=True, null=True, db_comment='Longitude of the sampling site location.')
    river_mi = models.DecimalField("Site RM", max_digits=5, decimal_places=1, blank=True, null=True, db_comment='River mile (RM) of the of the sampling site.')
    type = models.ForeignKey(SiteType, on_delete=models.PROTECT, db_comment='ID of the sampling locations site type.')
    pool = models.ForeignKey(Pool, on_delete=models.PROTECT, db_comment='ID of OHR pool where the site is located.')
    state = models.ForeignKey(State, on_delete=models.PROTECT, db_comment='ID of state where the site is located.')
    county = models.ForeignKey(County, on_delete=models.PROTECT, db_comment='ID of county where the site is located.')
    woody_debris = models.BooleanField("Woody Debris Present", db_comment='True if woody debris is at the site.')
    submersed_av = models.BooleanField("Aquatic Veg Present", db_comment='True if aquatic vegetation is at the site.')
    basin = models.ForeignKey(Basin, on_delete=models.PROTECT, db_comment='ID of basin where the site is located.')
    added_on = models.DateTimeField(auto_now_add=True, db_comment='Date-time of site creation.')
    trib = models.ForeignKey(Trib, on_delete=models.PROTECT, db_comment='ID of tributary or area where the site is located.')
    
    class Meta:
        db_table = 'ic_sites'
        db_table_comment = 'General locations within the OH River basin (ORB) where agency sampling was conducted for Invasive Carp research efforts.'
        verbose_name = '(Agency) Sample Site'
        verbose_name_plural = '(Agency) Sample Sites'
        
    def __str__(self):
        return f"{self.name} ({self.pool.abbrev})"


class FishingSite_CF(models.Model):
    site_id = models.AutoField("Site ID", primary_key=True, db_comment='ID number of the contract fishing location.')
    site_code = models.CharField("Site Code", max_length=8, blank=True, null=True, db_comment='Shorthand code (max 8 chars) for the contract fishing location.')
    name = models.CharField("Site Name", max_length=48, blank=False, null=False, db_comment='Full name (max 48 chars) for the contract fishing location.')
    latitude = models.DecimalField("Site LAT", max_digits=8, decimal_places=5, blank=False, null=False, db_comment='Latitude of the contract fishing location.')
    longitude = models.DecimalField("Site LON", max_digits=8, decimal_places=5, blank=False, null=False, db_comment='Longitude of the contract fishing location.')
    river_mi = models.DecimalField("Site RM", max_digits=5, decimal_places=1, blank=True, null=True, db_comment='River mile (RM) of the of the fishing site.')
    type = models.ForeignKey(SiteType, on_delete=models.PROTECT, db_comment='ID of the contract fishing locations site type.')
    pool = models.ForeignKey(Pool, on_delete=models.PROTECT, db_comment='ID of OHR pool where the site is located.')
    state = models.ForeignKey(State, on_delete=models.PROTECT, db_comment='ID of state where the site is located.')
    county = models.ForeignKey(County, on_delete=models.PROTECT, db_comment='ID of county where the site is located.')
    basin = models.ForeignKey(Basin, on_delete=models.PROTECT, db_comment='ID of river basin where the site is located.')
    added_on = models.DateTimeField(auto_now_add=True, db_comment='Date-time of site creation.')
    trib = models.ForeignKey(Trib, on_delete=models.PROTECT, db_comment='ID of tributary or area where the site is located.')
    
    class Meta:
        db_table = 'cf_sites'
        db_table_comment = 'General locations within the OH River basin (ORB) where daily fishing efforts was conducted for the Invasive Carp Contract Fishing Program.'
        verbose_name = '(CF) Fishing Site'
        verbose_name_plural = '(CF) Fishing Sites'

    def __str__(self):
        return self.name


class FishingSite_HP(models.Model):
    site_id = models.AutoField("ID", primary_key=True, db_comment='ID number of the commercial fishing location.')
    name = models.CharField("Name", max_length=48, blank=False, null=False, db_comment='Full name (max 48 chars) for the commercial fishing location.')
    latitude = models.DecimalField("Latitude", max_digits=8, decimal_places=5, blank=False, null=False, db_comment='Latitude of the commercial fishing location.')
    longitude = models.DecimalField("Longitude", max_digits=8, decimal_places=5, blank=False, null=False, db_comment='Longitude of the commercial fishing location.')
    river_mi = models.DecimalField("River Mile", max_digits=5, decimal_places=1, blank=True, null=True, db_comment='River mile (RM) of the of the fishing site.')
    type = models.ForeignKey(SiteType, on_delete=models.PROTECT, db_comment='ID of the commercial fishing locations site type.')
    pool = models.ForeignKey(Pool, on_delete=models.PROTECT, db_comment='ID of pool where the site is located.')
    state = models.ForeignKey(State, on_delete=models.PROTECT, db_comment='ID of state where the site is located.')
    county = models.ForeignKey(County, on_delete=models.PROTECT, db_comment='ID of county where the site is located.')
    basin = models.ForeignKey(Basin, on_delete=models.PROTECT, db_comment='ID of river basin where the site is located.')
    added_on = models.DateTimeField(auto_now_add=True, db_comment='Date-time of site creation.')
    trib = models.ForeignKey(Trib, on_delete=models.PROTECT, db_comment='ID of tributary, area or embayment where the site is located.')
    
    class Meta:
        db_table = 'ichp_sites'
        db_table_comment = 'General locations within the TN, Cumberland and lower OH River basins where daily fishing efforts are conducted for the Invasive Carp Harvest Program.'
        verbose_name = '(ICHP) Fishing Site'
        verbose_name_plural = '(ICHP) Fishing Sites'

    def __str__(self):
        return self.name


class IcAgeGrowth(models.Model):
    age_id = models.AutoField("Age ID", primary_key=True, db_comment='ID representing the aged carp.')
    project = models.ForeignKey(Project, on_delete=models.PROTECT, db_comment='ID of the project that the aged carp was captured for.')
    catch_date = models.DateField("Capture Date", blank=True, null=True, db_comment='Date of Capture.')
    pool = models.ForeignKey(Pool, on_delete=models.PROTECT, db_comment='ID of the OHR pool where the aged fish was captured.')
    agency = models.ForeignKey(Partner, on_delete=models.PROTECT, db_comment='ID of the agency/partner that aged the fish.')
    site = models.ForeignKey(SampleSite, on_delete=models.PROTECT, db_comment='ID of the general location where the aged fish was captured.')
    latitude = models.DecimalField("Latitude", max_digits=8, decimal_places=5, blank=True, null=True, db_comment='Latitude of the specific capture site.')
    longitude = models.DecimalField("Longitude", max_digits=8, decimal_places=5, blank=True, null=True, db_comment='Longitude of the specific capture site.')
    spp = models.ForeignKey(FishSpecies, on_delete=models.PROTECT, db_comment='ID of fish species that was captured and aged.')
    sex = models.ForeignKey(FishSex, on_delete=models.PROTECT, db_comment='ID for the sex of the fish that was captured and aged.')
    length_mm = models.DecimalField("Length (mm)", max_digits=5, decimal_places=1, blank=True, null=True, db_comment='Total length in millimeters of aged fish.')
    weight_g = models.DecimalField("Weight (g)", max_digits=6, decimal_places=1, blank=True, null=True, db_comment='Total weight in grams of aged fish.')
    ic_age = models.SmallIntegerField("Otilith Age", blank=True, null=True, db_comment='Fish age in years that was determined via otolith examination.')
    basin = models.ForeignKey(Basin, on_delete=models.PROTECT, db_comment='ID of the river basin where the aged fish was captured.')
    added_on = models.DateTimeField(auto_now_add=True, db_comment='Date-time of data input.')
    added_by = models.CharField(max_length=150, blank=True, null=True, db_comment='Initials of person inputting the data.')
    datez = models.ForeignKey(Dates, on_delete=models.PROTECT, db_comment='ID referencing the date table for the catch date.')

    class Meta:
        db_table = 'ic_age_growth'
        db_table_comment = 'Age & Growth Data for fish captured from the OH River Basin (ORB) during Invasive Carp Research efforts.'
        verbose_name = '(Agency) IC Age Data'
        verbose_name_plural = '(Agency) IC Age Data'

    def save(self, *args, user=None, **kwargs):
        if not self.added_by: 
            if user is not None:
                self.added_by = user.username
            else:
                self.added_by = 'app_user'
        
        if self.site:
            if not self.latitude:
                self.latitude = self.site.latitude
            if not self.longitude:
                self.longitude = self.site.longitude

        try:
            date_record = Dates.objects.get(ic_date=self.catch_date)
            self.datez = date_record
        except Dates.DoesNotExist:
            raise ValidationError({'catch_date': f"No matching date record found for catch date {self.catch_date}."})
        super().save(*args, **kwargs)


class Subsample(models.Model):
    ss_id = models.AutoField("ID", primary_key=True, db_comment='ID number of a subsampled invasive carp.')
    cf_date = models.DateField("Catch Date", blank=False, null=False, db_comment='Date that subsample was collected.')
    fisher = models.ForeignKey(Fisher, on_delete=models.PROTECT, db_comment='ID of fisher that captured the fish.')
    observer = models.ForeignKey(Observer, on_delete=models.PROTECT, db_comment='ID of agency observer that recorded the data.')
    basin = models.ForeignKey(Basin, on_delete=models.PROTECT, db_default=1, db_comment='ID of river basin where fishing was conducted.')
    pool = models.ForeignKey(Pool, on_delete=models.PROTECT, db_comment='ID of pool where fishing was conducted.')
    spp = models.ForeignKey(FishSpecies, on_delete=models.PROTECT, db_comment='ID of carp species that was measured and weighed.')
    sex = models.ForeignKey(FishSex, on_delete=models.PROTECT, db_comment='ID for the sex of the carp that was measured and weighed.')
    length_mm = models.DecimalField("Length (mm)", max_digits=5, decimal_places=1, blank=False, null=False, db_comment='Total length in millimeters of subsampled carp.')
    weight_g = models.DecimalField("Weight (g)", max_digits=8, decimal_places=1, blank=True, null=True, db_comment='Total weight in grams of subsampled carp.')
    ss_code = models.CharField("Subsample Code", max_length=15, blank=True, null=True, db_comment='Subsample identifier compiled from the date, fisher_id and species_id (as YYYYMMDD.fid.sppid).')
    added_on = models.DateTimeField(auto_now_add=True, db_comment='Date-time of data input.')
    datez = models.ForeignKey(Dates, on_delete=models.PROTECT, db_comment='ID referencing the date table for the catch date.')

    class Meta:
        db_table = 'subsamples'
        db_table_comment = 'Data from daily subsamples of invasive carp that agency observers collected from assigned contract fishers.'
        verbose_name = '(CF) Subsample'
        verbose_name_plural = '(CF) Subsamples'
        ordering = ['-cf_date', 'fisher', 'spp']

    def save(self, *args, **kwargs):
        if not self.ss_code:
            self.ss_code = f"{self.cf_date.strftime('%Y%m%d')}.{self.fisher.fisher_id}.{self.spp.spp_id}"

        if not self.sex:
            self.sex = FishSex.objects.get(sx_id=0)  # represents 'Unknown' and 'NA'

       # match cf_date with dates.ic_date to determine the value of date as dates.dates_id
        try:
            date_record = Dates.objects.get(ic_date=self.cf_date)
            self.datez = date_record
        except Dates.DoesNotExist:
            raise ValidationError({'cf_date': f"No matching date record found for catch date {self.cf_date}."})
        
        super().save(*args, **kwargs)


    def __str__(self):
        return self.ss_code

    @classmethod
    def mean_length_by_ss_code(cls, ss_code):
        """Return the average length_mm for every Subsample matching the provided ss_code."""
        if not ss_code:
            return None
        avg_length = cls.objects.filter(ss_code=ss_code).aggregate(models.Avg('length_mm'))['length_mm__avg']
        return f"{avg_length:.1f}" if avg_length is not None else None

    @classmethod
    def mean_weight_by_ss_code(cls, ss_code):
        """Return the average weight_g for every Subsample matching the provided ss_code."""
        if not ss_code:
            return None
        avg_weight = cls.objects.filter(ss_code=ss_code).aggregate(models.Avg('weight_g'))['weight_g__avg']
        return f"{avg_weight:.1f}" if avg_weight is not None else None
    
    @classmethod
    def sample_size_by_ss_code(cls, ss_code):
        """Return the count of Subsample records matching the provided ss_code."""
        if not ss_code:
            return 0
        count = cls.objects.filter(ss_code=ss_code).count()
        return count

    @classmethod
    def mean_weight_lb(cls, year, basin, pool, spp):
        """Return the mean weight in pounds for Subsamples matching year, basin, pool, and species (spp).

        Args:
            year: Calendar year (int) matched against cf_date.
            basin: Basin primary key.
            pool: Pool primary key.
            spp: FishSpecies primary key.

        Returns:
            Mean weight in pounds rounded to 2 decimal places, or None if no matching records exist.
        """
        avg_g = cls.objects.filter(
            cf_date__year=year,
            basin_id=basin,
            pool_id=pool,
            spp_id=spp,
            weight_g__isnull=False,
        ).aggregate(models.Avg('weight_g'))['weight_g__avg']
        if avg_g is None:
            return None
        return round(float(avg_g) / 453.592, 2)


class CfEvent(models.Model):
    event_id = models.AutoField("ID", primary_key=True, db_comment='ID representing the contract fishing effort.')
    cf_date = models.DateField("Fishing Date", blank=False, null=False, db_comment='Date at which the contract fishing occurred.')
    fisher = models.ForeignKey(Fisher, on_delete=models.PROTECT, db_comment='ID of contract fisher that conducted the fishing effort.')
    observer = models.ForeignKey(Observer, on_delete=models.PROTECT, db_comment='ID of agency staff that observed the contract fishing event.')
    site = models.ForeignKey(FishingSite_CF, on_delete=models.PROTECT, db_comment='ID of the general site where the contract fishing occured.')
    latitude = models.DecimalField("Net LAT", max_digits=8, decimal_places=5, blank=True, null=True, db_comment='Latitude of specific location where fishing gear was deployed.')
    longitude = models.DecimalField("Net LON", max_digits=8, decimal_places=5, blank=True, null=True, db_comment='Longitude of specific location where fishing gear was deployed.')
    gear = models.ForeignKey(Gear, on_delete=models.PROTECT, db_comment='ID of the gear type used to conduct the contract fishing.')
    set_num = models.SmallIntegerField("Net Set No.", blank=False, null=False,db_comment='Net or net-set number.')
    start_time = models.TimeField("Set Time", blank=True, null=True, db_comment='Time of day when the net was deployed.')
    end_time = models.TimeField("Pull Time", blank=True, null=True, db_comment='Time of day when the net was pulled up.')
    gear_length = models.IntegerField("Net Length (ft)", blank=True, null=True, db_comment='Total length in feet of the net used for this contract fishing effort.')
    gear_depth = models.IntegerField("Net Height (ft) ", blank=True, null=True, db_comment='Total Height in feet of the net used for this contract fishing effort.')
    mesh_size = models.DecimalField("Mesh Size (in)", max_digits=5, decimal_places=2, blank=True, null=True, db_comment='Mesh size in inches of the net used for this contract fishing effort.')
    water_temp_f = models.DecimalField("Water Temp (F)", max_digits=4, decimal_places=1, blank=True, null=True, db_comment='Water temperature (F) recorded during the contract fishing event.')
    added_on = models.DateTimeField(auto_now_add=True, db_comment='Date-time of data input.')
    added_by = models.CharField(max_length=150, blank=True, null=True, db_comment='Initials of person inputting the data.')
    datez = models.ForeignKey(Dates, on_delete=models.PROTECT, db_comment='ID referencing the date table for the catch date.')

    class Meta:
        db_table = 'events'
        db_table_comment = 'Information about the fishing efforts conducted in the Ohio River basin (ORB) by participants of the Invasive Carp Contract Fishing Program.'
        verbose_name = '(CF) Fishing Event'
        verbose_name_plural = '(CF) Fishing Events'
        ordering = ['-cf_date', 'fisher', 'set_num']

    def save(self, *args, user=None, **kwargs):
        if not self.added_by: 
            if user is not None:
                self.added_by = user.username
            else:
                self.added_by = 'app_user'

        if self.site:
            if not self.latitude:
                self.latitude = self.site.latitude
            if not self.longitude:
                self.longitude = self.site.longitude

        try:
            date_record = Dates.objects.get(ic_date=self.cf_date)
            self.datez = date_record
        except Dates.DoesNotExist:
            raise ValidationError({'cf_date': f"No matching date record found for catch date {self.cf_date}."})
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.cf_date} ({self.fisher.lookup} - Net {self.set_num})"


class RaEvent(models.Model):
    event_id = models.AutoField("ID", primary_key=True, db_comment='ID representing the ICHP ride-along effort.')
    ra_date = models.DateField("RA Date", blank=False, null=False, db_comment='Date at which the commercial fisher Ride-Along occurred.')
    fisher = models.ForeignKey(Fisher, on_delete=models.PROTECT, db_comment='ID of commercial fisher that completed the fishing efforts.')
    observer = models.ForeignKey(Observer, on_delete=models.PROTECT, db_comment='ID of agency staff that conducted the commercial ride-along.')
    site = models.ForeignKey(FishingSite_HP, on_delete=models.PROTECT, db_comment='ID of the primary site where the ICHP fishing occured.')
    gear = models.ForeignKey(Gear, on_delete=models.PROTECT, db_comment='ID of the gear type used to conduct the commercial fishing.')
    net_set = models.SmallIntegerField("Set #.", blank=False, null=False,db_comment='Net or net-set number.')
    latitude = models.DecimalField("Net LAT", max_digits=8, decimal_places=5, blank=True, null=True, db_comment='Latitude of specific location where fishing gear was deployed.')
    longitude = models.DecimalField("Net LON", max_digits=8, decimal_places=5, blank=True, null=True, db_comment='Longitude of specific location where fishing gear was deployed.')
    start_time = models.DateTimeField("Set Time", blank=True, null=True, db_comment='Date and Time of when the net was deployed.')
    end_time = models.DateTimeField("Pull Time", blank=True, null=True, db_comment='Date and Time of when the net was retrieved.')
    net_num = models.SmallIntegerField("Net #.", blank=False, null=False, db_comment='Net or net-set number.')
    gear_length = models.IntegerField("Net Length (ft)", blank=True, null=True, db_comment='Total length in feet of the net used for this ride-Along event.')
    gear_depth = models.IntegerField("Net Depth (ft) ", blank=True, null=True, db_comment='Total Depth in feet of the net used for this ride-Along event.')
    mesh_size = models.DecimalField("Mesh Size (in)", max_digits=5, decimal_places=2, blank=True, null=True, db_comment='Mesh size in inches of the net used for this ride-Along event.')
    water_temp_f = models.DecimalField("Water Temp (F)", max_digits=4, decimal_places=1, blank=True, null=True, db_comment='Water temperature (F) recorded during the ride-along event.')
    water_depth_ft = models.DecimalField("Water Depth (ft)", max_digits=3, decimal_places=1, blank=True, null=True, db_comment='Water depth (in feet) recorded during the ride-along event.')
    datez = models.ForeignKey(Dates, on_delete=models.PROTECT, db_comment='ID referencing the date table for the ride-along date.')
    added_on = models.DateTimeField(auto_now_add=True, db_comment='Date-time of data input.')
    added_by = models.CharField(max_length=150, blank=True, null=True, db_comment='name of person inputting the data.')

    class Meta:
        db_table = 'ra_events'
        db_table_comment = 'Information about the field events when agency staff accompanied ICHP fishers in order to obtain additional details about their efforts.'
        verbose_name = '(ICHP) RA Fishing Event'
        verbose_name_plural = '(ICHP) RA Fishing Events'
        ordering = ['-ra_date', 'fisher', 'net_set', 'net_num']

    def save(self, *args, user=None, **kwargs):
        if not self.added_by: 
            if user is not None:
                self.added_by = user.username
            else:
                self.added_by = 'app_user'
        
        if self.site:
            if not self.latitude:
                self.latitude = self.site.latitude
            if not self.longitude:
                self.longitude = self.site.longitude

        try:
            date_record = Dates.objects.get(ic_date=self.ra_date)
            self.datez = date_record
        except Dates.DoesNotExist:
            raise ValidationError({'ra_date': f"No matching date record found for ride-along date {self.ra_date}."})
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.ra_date} ({self.fisher.lookup} - Set {self.net_set}| Net {self.net_num})"
 

class CfCatch(models.Model):
    catch_id = models.AutoField("ID", primary_key=True, db_comment='ID representing the result of a contract fishing effort.')
    event = models.ForeignKey(CfEvent, on_delete=models.PROTECT, db_comment='ID representing a contract fishing event.')
    species = models.ForeignKey(FishSpecies, on_delete=models.PROTECT, db_comment='ID of fish species captured by contract fishers.')
    healthy_cnt = models.IntegerField("Healthy Count", blank=True, null=True, db_comment='Number of heathy bycatch caught and released during the contract fishing event.')
    moribund_cnt = models.IntegerField("Moribund Count", blank=True, null=True, db_comment='Number of moribund bycatch and/or harvested Invasive Carp caught during the contract fishing event.')
    total_cnt = models.IntegerField("Total Catch", blank=True, null=True, db_comment='Total count of bycatch and Invasive carp caught during the contract fishing event.')
    mean_length_mm = models.DecimalField("Est Mean Length (mm)", max_digits=5, decimal_places=1, blank=True, null=True, db_comment='Estimated mean length (in millimeters) of Invasive Carp species. Calculated from CF subsamples.')
    mean_weight_g = models.DecimalField("Est Mean Weight (g)", max_digits=7, decimal_places=1, blank=True, null=True, db_comment='Estimated mean weight (in grams) of Invasive Carp species. Calculated from CF subsamples.')
    predicted_weight_g = models.DecimalField("Predicted Mean Weight (g)", max_digits=7, decimal_places=1, blank=True, null=True, db_comment='Predicted mean weight (in grams). Calculated via the estimated mean length of the sample and a length-weight regression for the population.')
    ss_code = models.CharField("Subsample Code", max_length=15, blank=True, null=True, db_comment='Subsample identifier compiled from date, fisher_id and species_id (as YYYYMMDD.fid.sppid).')
    mean_length = models.DecimalField("Est Mean Length", max_digits=5, decimal_places=1, blank=True, null=True, db_comment='Estimated mean length of Invasive Carp species. Calculated from CF subsamples.')
    added_on = models.DateTimeField(auto_now_add=True, db_comment='Date-time of data input.')
    added_by = models.CharField(max_length=150, blank=True, null=True, db_comment='Initials of person inputting the data.')

    class Meta:
        db_table = 'cf_catch'
        db_table_comment = 'Catch Results of the contract fishing efforts conducted in the Ohio River Basin (ORB).'
        verbose_name = '(CF) Catch Data'
        verbose_name_plural = '(CF) Catch Data'
        ordering = ['-event__cf_date', 'event__fisher', 'event__set_num']

    def save(self, *args, user=None, **kwargs):
        if not self.added_by: 
            if user is not None:
                self.added_by = user.username
            else:
                self.added_by = 'app_user'
        
        if not self.ss_code and self.event and self.species:
            self.ss_code = f"{self.event.cf_date.strftime('%Y%m%d')}.{self.event.fisher.fisher_id}.{self.species.spp_id}"
        
        if self.mean_length_mm and not self.mean_length:
            self.mean_length = self.mean_length_mm

        if self.ss_code and Subsample.objects.filter(ss_code=self.ss_code).exists():
            ss_cnt = Subsample.sample_size_by_ss_code(self.ss_code)
            ss_tl = Subsample.mean_length_by_ss_code(self.ss_code)
            ss_tw = Subsample.mean_weight_by_ss_code(self.ss_code)
            
            if ss_cnt and ss_cnt > 0:
                print(f"Located {self.species.abbrev} subsample (n = {ss_cnt}).")
                if ss_tl:
                    print(f"SS Mean Length (mm): {ss_tl}")
                    if not self.mean_length_mm:
                        self.mean_length_mm = Decimal(ss_tl)
                        self.mean_length = Decimal(ss_tl)
                else:
                    print("SS Mean Length (mm): None")
                if ss_tw:
                    print(f"SS Mean Weight (g): {ss_tw}")
                    if not self.mean_weight_g:
                        self.mean_weight_g = Decimal(ss_tw)
                else:
                    print("SS Mean Weight (g): None")
        else:
            print(f"No subsample located for SS Code: {self.ss_code}")

        if not self.healthy_cnt: self.healthy_cnt = 0

        if not self.moribund_cnt: self.moribund_cnt = 0

        if not self.total_cnt: self.total_cnt = self.healthy_cnt + self.moribund_cnt

        super().save(*args, **kwargs)


class RaCatch(models.Model):
    catch_id = models.AutoField("ID", primary_key=True, db_comment='ID representing the results gathered during a Ride-Along event.')
    event = models.ForeignKey(RaEvent, on_delete=models.PROTECT, db_comment='ID representing a ICHP Ride-Along event.')
    species = models.ForeignKey(FishSpecies, on_delete=models.PROTECT, db_comment='ID of fish species captured by ICHP fishers.')
    rel_healthy_cnt = models.IntegerField("Healthy Count", blank=True, null=True, db_comment='Number of heathy bycatch caught and released during a ICHP ride-along effort.')
    rel_moribund_cnt = models.IntegerField("Moribund Count", blank=True, null=True, db_comment='Number of moribund bycatch caught and released during a ICHP ride-along effort.')
    harvest_cnt = models.IntegerField("Harvested Count", blank=True, null=True, db_comment='Number of Invasive Carp or other commercial species harvested during a ICHP ride-along effort.')
    total_cnt = models.IntegerField("Total Catch", blank=True, null=True, db_comment='Total count of bycatch and Invasive carp caught during the ICHP ride-along effort.')
    mean_length_mm = models.DecimalField("Est Mean Length (mm)", max_digits=5, decimal_places=1, blank=True, null=True, db_comment='Estimated mean length (in millimeters) of Invasive Carp species. Calculated from RA subsamples.')
    mean_weight_g = models.DecimalField("Est Mean Weight (g)", max_digits=7, decimal_places=1, blank=True, null=True, db_comment='Estimated mean weight (in grams) of Invasive Carp species. Calculated from RA subsamples.')
    predicted_weight_g = models.DecimalField("Predicted Mean Weight (g)", max_digits=7, decimal_places=1, blank=True, null=True, db_comment='Predicted mean weight (in grams). Calculated via the a sample mean length and a length-weight regression for the population.')
    ss_code = models.CharField("Subsample Code", max_length=15, blank=True, null=True, db_comment='Subsample identifier compiled from date, fisher_id and species_id (as YYYYMMDD.fid.sppid).')
    added_on = models.DateTimeField(auto_now_add=True, db_comment='Date-time of data input.')
    added_by = models.CharField(max_length=150, blank=True, null=True, db_comment='username of person inputting the data.')

    class Meta:
        db_table = 'ra_catch'
        db_table_comment = 'Catch Results of the Ride-Along events conducted with ICHP participants.'
        verbose_name = '(ICHP) RA Catch Data'
        verbose_name_plural = '(ICHP) RA Catch Data'
        ordering = ['-event__ra_date', 'event__fisher', 'event__net_set', 'event__net_num']


    def save(self, *args, user=None, **kwargs):
        if not self.added_by: 
            if user is not None:
                self.added_by = user.username
            else:
                self.added_by = 'app_user'
        
        if not self.ss_code and self.event and self.species:
            self.ss_code = f"{self.event.ra_date.strftime('%Y%m%d')}.{self.event.fisher.fisher_id}.{self.species.spp_id}"
        
        if self.ss_code and Subsample.objects.filter(ss_code=self.ss_code).exists():
            ss_cnt = Subsample.sample_size_by_ss_code(self.ss_code)
            ss_tl = Subsample.mean_length_by_ss_code(self.ss_code)
            ss_tw = Subsample.mean_weight_by_ss_code(self.ss_code)
            
            if ss_cnt and ss_cnt > 0:
                print(f"Located {self.species.abbrev} subsample (n = {ss_cnt}).")
                if ss_tl:
                    print(f"SS Mean Length (mm): {ss_tl}")
                    if not self.mean_length_mm:
                        self.mean_length_mm = Decimal(ss_tl)
                else:
                    print("SS Mean Length (mm): None")
                if ss_tw:
                    print(f"SS Mean Weight (g): {ss_tw}")
                    if not self.mean_weight_g:
                        self.mean_weight_g = Decimal(ss_tw)
                else:
                    print("SS Mean Weight (g): None")
        else:
            print(f"No subsample located for SS Code: {self.ss_code}")
        
        if not self.rel_healthy_cnt: self.rel_healthy_cnt = 0

        if not self.rel_moribund_cnt: self.rel_moribund_cnt = 0

        if not self.harvest_cnt: self.harvest_cnt = 0

        if not self.total_cnt: self.total_cnt = self.rel_healthy_cnt + self.rel_moribund_cnt + self.harvest_cnt

        super().save(*args, **kwargs)


class IcEvent(models.Model):
    SET_TYPES = {
        "bottom": "Bottom Set",
        "top": "Top Set",
        "sinking": "Sinking Set",
        "floating": "Floating Set",
    }
    LOC_TYPES = {
        "embayment": "Embayment",
        "main_lake": "Main Lake Channel",
        "tributary": "Tributary",
        "main_river": "Main River Channel",
    }
    WEATHER_CONDITIONS = {
        "sunny": "Sunny",
        "partly sunny": "Partly Sunny",
        "overcast": "Overcast",
        "rain": "Rain",
        "fog": "Fog",
        "snow": "Snow",
    }
    BANKS = {
        "left descending": "LDB/RAB",
        "right descending": "RDB/LAB",
    }
    event_id = models.AutoField("ID", primary_key=True, db_comment='ID representing the agency sampling effort.')
    event_date = models.DateField("Sample Date", blank=False, null=False, db_comment='Date at which the agency sampling effort occurred.')
    site = models.ForeignKey(SampleSite, on_delete=models.PROTECT, db_comment='ID of the general location where the agency sampling effort occurred.')
    project = models.ForeignKey(Project, on_delete=models.PROTECT, blank=False, null=False, db_comment='ID of the project that the sampling effort was conducted for.')
    agency = models.ForeignKey(Partner, on_delete=models.PROTECT, blank=False, null=False, db_comment='ID of agency or partner that conducted the sampling effort.')
    crew_lead = models.ForeignKey(Crew, on_delete=models.PROTECT, blank=False, null=False, db_comment='ID of field crew that conducted the sampling effort.')
    gear = models.ForeignKey(Gear, on_delete=models.PROTECT, blank=True, null=True, db_comment='ID of gear type used during the sampling effort.')
    effort_num = models.SmallIntegerField("Transect/Net No.", blank=False, null=False, db_comment='Daily transect or net number associated with the sampling effort.')
    latitude = models.DecimalField("Sample LAT", max_digits=8, decimal_places=5, blank=True, null=True, db_comment='Latitude of specific location where sampling effort was conducted.')
    longitude = models.DecimalField("Sample LON", max_digits=8, decimal_places=5, blank=True, null=True, db_comment='Longitude of specific location where sampling effort was conducted.')
    effort_min = models.DecimalField("Effort (min)", max_digits=8, decimal_places=2, blank=True, null=True, db_comment='Length of time in minutes that the sampling effort occured for.')
    ef_duty_cycle = models.IntegerField("EF Duty Cycle", blank=True, null=True, db_comment='Duty cycle setting that was used during an electrofishing effort.')
    ef_pps_hertz = models.IntegerField("EF Hertz (pps)", blank=True, null=True, db_comment='Hertz or pulse rate in seconds that was used during an electrofishing effort.')
    ef_voltage = models.IntegerField("EF Voltage", blank=True, null=True, db_comment='Voltage setting that was used during an electrofishing effort.')
    ef_amps = models.DecimalField("EF Amperage", max_digits=4, decimal_places=1, blank=True, null=True, db_comment='Amperage measurement that was recording during an electrofishing effort.')
    ef_watts = models.IntegerField("EF Wattage", blank=True, null=True, db_comment='Wattage measurement that was recording during an electrofishing effort.')
    net_length_ft = models.IntegerField("Net Length (ft)", blank=True, null=True, db_comment='Total length in feet of the net used for this sampling effort.')
    net_depth_ft = models.IntegerField("Net Depth (ft)", blank=True, null=True, db_comment='Total height in feet of the net used for this sampling effort.')
    mesh_size_in = models.DecimalField("Mesh Size (in)", max_digits=5, decimal_places=2, blank=True, null=True, db_comment='Mesh size in inches of the net used for this sampling effort.')
    start_time = models.TimeField("Start Time", blank=True, null=True, db_comment='Time of day when the sampling effort began.')
    carp_sighted = models.BooleanField("IC Present", db_comment='True if Invasive Carp were observed during the agency sampling effort.' )
    yoy_sighted = models.BooleanField("YOY IC Present", db_comment='True if YOY Invasive Carp were observed during the agency sampling effort.' )
    water_temp_f = models.DecimalField("Water Temp (F)", max_digits=4, decimal_places=1, blank=True, null=True, db_comment='Water temperature (F) recorded during the sampling effort.')
    secchi_depth_in = models.IntegerField("Secchi Depth (in)", blank=True, null=True, db_comment='Secchi Depth in inches that was measured near the sampling event.')
    net_set_type = models.CharField("Net Set Type", max_length=15, blank=True, null=True, choices=SET_TYPES.items(), db_comment='Type of net set used during the sampling effort.')
    ef_cond = models.DecimalField("Conductivity", max_digits=6, decimal_places=1, blank=True, null=True, db_comment='Conductivity of the water measured near the sampling site.')
    water_ph = models.DecimalField("Water pH", max_digits=5, decimal_places=2, blank=True, null=True, db_comment='pH of the water measured near the sampling site.')
    egn_panel_num = models.SmallIntegerField("Experimental GN Panel", blank=True, null=True, db_comment='Panel number of experimental gill net used during the sampling effort.')
    added_on = models.DateTimeField(auto_now_add=True, db_comment='Date-time of data input.')
    added_by = models.CharField(max_length=150, blank=True, null=True, db_comment='Name of person inputting the data.')
    end_time = models.TimeField("End Time", blank=True, null=True, db_comment='Time of day when the sampling effort ended.')
    datez = models.ForeignKey(Dates, on_delete=models.PROTECT, db_comment='ID referencing the date table for the catch date.')
    event_loc_type = models.CharField("Event Site Type", max_length=20, blank=True, null=True, choices=LOC_TYPES.items(), db_comment='Specific type of site where the sampling event occurred.')
    weather = models.CharField("Weather Cond.", max_length=20, blank=True, null=True, choices=WEATHER_CONDITIONS.items(), db_comment='General weather conditions observed during the sampling effort.')
    bankside = models.CharField("Bank Side", max_length=20, blank=True, null=True, choices=BANKS.items(), db_comment='Side of a river/stream/creek bank where a sampling effort was conducted.')
    run_distance = models.DecimalField("Bank Distance (mi)", max_digits=6, decimal_places=3, blank=True, null=True, db_comment='Estimated bank distance of an electrofishing transect.')
    dipper_cnt = models.IntegerField("Dipper Count", blank=True, null=True, db_comment='Number of dippers used during an electrofishing effort.')
    air_temp_f = models.DecimalField("Air Temp (F)", max_digits=4, decimal_places=1, blank=True, null=True, db_comment='Air temperature (F) during the sampling effort.')
    wind_speed_mph = models.DecimalField("Wind Speed (mph)", max_digits=5, decimal_places=2, blank=True, null=True, db_comment='Wind speed (mph) during the sampling effort.')

    
    class Meta:
        db_table = 'ic_events'
        db_table_comment = 'Details from agency sampling events completed for Invasive Carp research efforts in the Ohio River Basin (ORB).'
        verbose_name = '(Agency) Sampling Effort'
        verbose_name_plural = '(Agency) Sampling Efforts'


    def save(self, *args, user=None, **kwargs):
        #check if self.added_by is empty and if it is assign the current user's username to added_by
        if not self.added_by: 
            if user is not None:
                self.added_by = user.username
            else:
                self.added_by = 'app_user'
        if not self.latitude and self.site:
            self.latitude = self.site.latitude
        if not self.longitude and self.site:
            self.longitude = self.site.longitude
        try:
            date_record = Dates.objects.get(ic_date=self.event_date)
            self.datez = date_record
        except Dates.DoesNotExist:
            raise ValidationError({'event_date': f"No matching date record found for catch date {self.event_date}."})
        super().save(*args, **kwargs)


    def __str__(self):
        if self.gear.gear_id in [6, 17, 18]:  # assuming gear_id 6, 17, and 18 are electrofishing gears
            return f"{self.event_date.strftime('%Y-%m-%d')} ({self.site.trib} - Transect #{self.effort_num})"
        elif self.gear.gear_id in [15, 22]:  
            return f"{self.event_date.strftime('%Y-%m-%d')} ({self.site.trib} - Trawl #{self.effort_num})"
        else:
            return f"{self.event_date.strftime('%Y-%m-%d')} ({self.site.trib} - Net #{self.effort_num})"


class IcCatch(models.Model):
    GONAD_STAGES = {
        "STW": "STW",
        "PNK": "PNK",
        "PWE": "PWE",
        "EGG": "EGG",
        "ORG": "ORG",
        "LAW": "LAW",
    }
    
    catch_id = models.AutoField("ID", primary_key=True, db_comment='ID representing the result of an agency sampling effort.')
    event = models.ForeignKey(IcEvent, on_delete=models.PROTECT, db_comment='ID representing the details of an agency sampling effort.')
    pool = models.IntegerField("Pool_ID", blank=True, null=True, db_comment='ID representing the pool where agency sampling results were gathered.')
    species = models.ForeignKey(FishSpecies, on_delete=models.PROTECT, db_comment='ID of fish species captured via the sampling efforts.')
    fish_sex = models.ForeignKey(FishSex, on_delete=models.PROTECT, db_comment='ID representing the sex of the sampled fish.')
    length_mm = models.DecimalField("Length (mm)", max_digits=5, decimal_places=1, blank=True, null=True, db_comment='The total length (in millimeters) of sampled fish.')
    weight_g = models.DecimalField("Weight (g)", max_digits=6, decimal_places=1, blank=True, null=True, db_comment='The total weight (in grams) of the sampled fish.')
    fish_count = models.SmallIntegerField("Count", blank=True, null=True, db_comment='Total number of sampled fish.')
    spawn_patch = models.BooleanField("Spawning Patch Present", db_comment='True if a spawning patch was present.')
    collected4ag = models.BooleanField("Collected for Age", db_comment='True if the fish was collected for aging structures.')
    gonad_stage = models.CharField("Obs Gonad Stage", max_length=3, blank=True, null=True, choices=GONAD_STAGES, db_comment='Observed gonad stage of the sampled fish.')
    gonad_wt_g = models.IntegerField("Gonad Wt (g)", blank=True, null=True, db_comment='Individual gonadal weight (in grams) of the sampled fish.')
    added_on = models.DateTimeField(auto_now_add=True, db_comment='Date-time of data input.')
    added_by = models.CharField(max_length=150, blank=True, null=True, db_comment='Name of person inputting the data.')
    
    class Meta:
        db_table = 'ic_catch'
        db_table_comment = 'Results of sampling efforts conducted in the OH River Basin (ORB) by agencies participating in Invasive Carp research efforts.'
        verbose_name = '(Agency) Sampling Data'
        verbose_name_plural = '(Agency) Sampling Data'
        

    def save(self, *args, user=None, **kwargs):
        if not self.added_by: 
            if user is not None:
                self.added_by = user.username
            else:
                self.added_by = 'app_user'
        
        try:
            pool_record = self.event.site.pool.pool_id
            self.pool = pool_record
        except Dates.DoesNotExist:
            raise ValidationError({'pool': f"No matching pool record found for this site: {self.event.site.name}."})
        
        if not self.fish_sex:
            self.fish_sex = FishSex.objects.get(sx_id=0)  # represents 'Unknown' and 'NA'

        if self.species:
            if self.species.spp_id == 0:
                self.length_mm = None
                self.weight_g = None
                self.fish_count = 0
            else:
                if not self.fish_count or self.fish_count < 1:
                    self.fish_count = 1

        super().save(*args, **kwargs)


class IchpEvent(models.Model):
    event_id = models.AutoField("ID", primary_key=True, db_comment='ID representing the ICHP fishing effort.')
    ichp_date = models.DateField("RA Date", blank=False, null=False, db_comment='Date at which the commercial fishing occurred.')
    fisher = models.ForeignKey(Fisher, on_delete=models.PROTECT, db_comment='ID of commercial fisher that completed the fishing efforts.')
    basin = models.ForeignKey(Basin, on_delete=models.PROTECT, db_comment='ID of river basin or waterbody where commercial fishing effort was conducted.')
    gear = models.ForeignKey(Gear, on_delete=models.PROTECT, db_comment='ID of the gear type used to conduct the commercial fishing.')
    net_haul = models.SmallIntegerField("Net Haul", blank=False, null=False,db_comment='Net or net-set number.')
    gear_length = models.IntegerField("Net Length (ft)", blank=True, null=True, db_comment='Total length in feet of the net used for this fishing effort.')
    gear_depth = models.IntegerField("Net Depth (ft) ", blank=True, null=True, db_comment='Total Depth in feet of the net used for this fishing effort.')
    mesh_size = models.DecimalField("Mesh Size (in)", max_digits=5, decimal_places=2, blank=True, null=True, db_comment='Mesh size in inches of the net used for this fishing effort.')
    observed = models.BooleanField("Observed", db_comment='Identifies if an angency observer was present during ichp fishing effort.)')
    site = models.ForeignKey(FishingSite_HP, on_delete=models.PROTECT, db_comment='ID of the specific location where the commercial fishing effort occured.')
    latitude = models.DecimalField("Net LAT", max_digits=8, decimal_places=5, blank=True, null=True, db_comment='Latitude of specific location where fishing gear was deployed.')
    longitude = models.DecimalField("Net LON", max_digits=8, decimal_places=5, blank=True, null=True, db_comment='Longitude of specific location where fishing gear was deployed.')
    start_time = models.TimeField("Set Time", blank=True, null=True, db_comment='Time of when the net was deployed.')
    end_time = models.TimeField("Pull Time", blank=True, null=True, db_comment='Time of when the net was retrieved.')
    datez = models.ForeignKey(Dates, on_delete=models.PROTECT, db_comment='ID referencing the date table for the ride-along date.')
    added_on = models.DateTimeField(auto_now_add=True, db_comment='Date-time of data input.')
    added_by = models.CharField(max_length=150, blank=True, null=True, db_comment='name of person inputting the data.')

    class Meta:
        db_table = 'ichp_events'
        db_table_comment = 'Information about the efforts that commercial fishers submitted to the KDFWR Invasive Carp Harvested Program.'
        verbose_name = '(ICHP) Fisher Effort'
        verbose_name_plural = '(ICHP) Fisher Efforts'
        ordering = ['-ichp_date', 'fisher', 'net_haul']
	

    def save(self, *args, user=None, **kwargs):
        if not self.added_by: 
            if user is not None:
                self.added_by = user.username
            else:
                self.added_by = 'app_user'
        
        if not self.observed:
            self.observed = False
        
        if self.site:
            if not self.latitude:
                self.latitude = self.site.latitude
            if not self.longitude:
                self.longitude = self.site.longitude
        else:
            try:
                site_record = FishingSite_HP.objects.get(name="Unreported")
                self.site = site_record
                self.latitude = 0.0
                self.longitude = 0.0
            except FishingSite_HP.DoesNotExist:
                raise ValidationError({'site_error': "No record found for this Unreported Site."})

        try:
            date_record = Dates.objects.get(ic_date=self.ichp_date)
            self.datez = date_record
        except Dates.DoesNotExist:
            raise ValidationError({'ichp_date': f"No matching date record found for ride-along date {self.ichp_date}."})
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.ichp_date} | {self.fisher.lookup} - Net {self.net_haul} ({self.gear_length}x{self.gear_depth}x{self.mesh_size})"
 
 
class IchpCatch(models.Model):
    catch_id = models.AutoField("ID", primary_key=True, db_comment='ID representing the catch results provided by commercial fishers ICHP Daily Harvest Report.')
    event = models.ForeignKey(IchpEvent, on_delete=models.PROTECT, db_comment='ID representing a commercial fishing effort that was reported to the Invasive Carp Harvest Program.')
    species = models.ForeignKey(FishSpecies, on_delete=models.PROTECT, db_comment='ID of a fish species included in the ICHP Daily Report.')
    rel_healthy_cnt = models.IntegerField("Healthy C&R", blank=True, null=True, db_comment='Total healthy caught and released bycatch that was reported by the commercial fisher.')
    rel_moribund_cnt = models.IntegerField("Moribund C&R", blank=True, null=True, db_comment='Total moribund caught and released bycatch that was reported by the commercial fisher.')
    harvest_cnt = models.IntegerField("Total Harvested", blank=True, null=True, db_comment='Total Invasive Carp (or other fish species) reported as harvested by the commercial fisher.')
    total_cnt = models.IntegerField("Total Caught", blank=True, null=True, db_comment='Total overall count of a fish species that was reported by the commercial fisher.')
    reported_weight_lb = models.DecimalField("Reported TW (lb)", max_digits=10, decimal_places=1, blank=True, null=True, db_comment='Total weight (lbs) of the harvested target species as reported by the commercial fisher.')
    reported_mean_length_in = models.DecimalField("Reported Mean Len (in)", max_digits=5, decimal_places=1, blank=True, null=True, db_comment='Mean Length (in) of an Invasive Carp species that was subsampled and reported by the commercial fisher.')
    calc_mean_weight_g = models.DecimalField("Calculated Mean Wgt (g)", max_digits=7, decimal_places=1, blank=True, null=True, db_comment='Mean weight (g) of the harvested IC that was calculated from the harvest counts and Total weights reported by the commercial fisher.')
    ss_code = models.CharField("Subsample Code", max_length=25, blank=True, null=True, db_comment='Subsample identifier compiled from date, fisher_id and species_id (as YYYYMMDD.fid.sppid).')
    ss_mean_length_mm = models.DecimalField("Est Mean Len (mm)", max_digits=5, decimal_places=1, blank=True, null=True, db_comment='Mean length (mm) of the harvested IC that was estimated from a subsample collected during an ICHP Ride-Along event.')
    ss_mean_weight_g = models.DecimalField("Est Mean Wgt (g)", max_digits=7, decimal_places=1, blank=True, null=True, db_comment='Mean weight (g) of the harvested IC that was estimated from a subsample collected during an ICHP Ride-Along event.')
    predicted_mean_weight_g = models.DecimalField("Predicted Mean Wgt (g)", max_digits=7, decimal_places=1, blank=True, null=True, db_comment='Predicted mean weight (g) of the harvested carp calculated using a LxW regression equation that was generated from subsampled fish.')
    added_on = models.DateTimeField(auto_now_add=True, db_comment='Date-time of data input.')
    added_by = models.CharField(max_length=150, blank=True, null=True, db_comment='username of person inputting the data.')


    class Meta:
        db_table = 'ichp_catch'
        db_table_comment = 'Catch Results from ICHP Daily Harvest reports provided by a participating commercial fisher.'
        verbose_name = '(ICHP) Harvest Data'
        verbose_name_plural = '(ICHP) Harvest Data'
        ordering = ['-event__ichp_date', 'event__fisher', 'event__net_haul']


    def save(self, *args, user=None, **kwargs):
        if not self.added_by: 
            if user is not None:
                self.added_by = user.username
            else:
                self.added_by = 'app_user'
        
        if not self.ss_code and self.event and self.species:
            self.ss_code = f"{self.event.ichp_date.strftime('%Y%m%d')}.{self.event.fisher.fisher_id}.{self.species.spp_id}"
        
        if self.ss_code and Subsample.objects.filter(ss_code=self.ss_code).exists():
            ss_cnt = Subsample.sample_size_by_ss_code(self.ss_code)
            ss_tl = Subsample.mean_length_by_ss_code(self.ss_code)
            ss_tw = Subsample.mean_weight_by_ss_code(self.ss_code)
            
            if ss_cnt and ss_cnt > 0:
                print(f"Located {self.species.abbrev} subsample (n = {ss_cnt}).")
                if ss_tl:
                    print(f"SS Mean Length (mm): {ss_tl}")
                    if not self.ss_mean_length_mm:
                        self.ss_mean_length_mm = Decimal(ss_tl)
                else:
                    print("SS Mean Length (mm): None")
                if ss_tw:
                    print(f"SS Mean Weight (g): {ss_tw}")
                    if not self.ss_mean_weight_g:
                        self.ss_mean_weight_g = Decimal(ss_tw)
                else:
                    print("SS Mean Weight (g): None")
        else:
            print(f"No subsample located for SS Code: {self.ss_code}")

        if not self.rel_healthy_cnt: self.rel_healthy_cnt = 0

        if not self.rel_moribund_cnt: self.rel_moribund_cnt = 0

        if not self.harvest_cnt:
            if self.reported_weight_lb and self.reported_weight_lb > 0:
                ss_mean_wgt = Subsample.mean_weight_lb(self.event.datez.cal_year, self.event.basin.basin_id, self.event.site.pool.pool_id, self.species.spp_id)
                if ss_mean_wgt is None:
                    ss_mean_wgt = Subsample.mean_weight_lb(self.event.datez.cal_year - 1, self.event.basin.basin_id, self.event.site.pool.pool_id, self.species.spp_id)

                if ss_mean_wgt is not None and ss_mean_wgt > 0:
                    est_harvest_cnt = Decimal(self.reported_weight_lb) / Decimal(ss_mean_wgt)
                    self.harvest_cnt = int(est_harvest_cnt.to_integral_value(rounding='ROUND_HALF_UP'))
                else:
                    print(f"No {self.species.abbrev} subsamples from {self.event.basin.name} in {self.event.datez.cal_year} or {self.event.datez.cal_year - 1}. Using default weights to estimate harvest count.")
                    if self.species.name == "Silver Carp":  # Silver Carp
                        if self.event.basin.name == "Lake Barkley_CMB":
                            def_wgt = '12.0'  # default weight (lbs) for Silver Carp in Lake Barkley
                        elif self.event.basin.name == "Kentucky Lake_TNR":
                            def_wgt = '11.5'  # default weight (lbs) for Silver Carp in Kentucky Lake
                        else:
                            def_wgt = '10.0'  # default weight (lbs) for Silver Carp in other basins
                        est_harvest_cnt = Decimal(self.reported_weight_lb) / Decimal(def_wgt)
                        self.harvest_cnt = int(est_harvest_cnt.to_integral_value(rounding='ROUND_HALF_UP'))
                    elif self.species.name == "Bighead Carp":  # Bighead Carp
                        est_harvest_cnt = Decimal(self.reported_weight_lb) / Decimal('21.0')
                        self.harvest_cnt = int(est_harvest_cnt.to_integral_value(rounding='ROUND_HALF_UP'))
                    elif self.species.name in ["Grass Carp", "Black Carp"]:  # Grass Carp
                        est_harvest_cnt = Decimal(self.reported_weight_lb) / Decimal('16.0')
                        self.harvest_cnt = int(est_harvest_cnt.to_integral_value(rounding='ROUND_HALF_UP'))
                    elif self.species.name in ["Buffalo Family", "Smallmouth Buffalo", "Bigmouth Buffalo"]:  # Buffalo
                        est_harvest_cnt = Decimal(self.reported_weight_lb) / Decimal('12.5')
                        self.harvest_cnt = int(est_harvest_cnt.to_integral_value(rounding='ROUND_HALF_UP'))
                    elif self.species.name in ["Catfish Family", "Channel Catfish", "Blue Catfish"]:  # Catfish
                        est_harvest_cnt = Decimal(self.reported_weight_lb) / Decimal('8.0')
                        self.harvest_cnt = int(est_harvest_cnt.to_integral_value(rounding='ROUND_HALF_UP'))
                    else:
                        print(f"No default weight for {self.species.name}. Unable to estimate harvest count.")
                        self.harvest_cnt = 0
            else:
                self.harvest_cnt = 0

        if not self.total_cnt: self.total_cnt = self.rel_healthy_cnt + self.rel_moribund_cnt + self.harvest_cnt

        # convert reported weight in pounds to grams for calculated mean weight
        if self.reported_weight_lb and self.harvest_cnt and self.harvest_cnt > 0:
            rep_wgt = Decimal(self.reported_weight_lb) 
            tw_g = rep_wgt * Decimal('453.59') # pounds to grams conversion
            self.calc_mean_weight_g = tw_g / self.harvest_cnt
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.event} | Catch: {self.total_cnt} weighing {self.reported_weight_lb} lbs."
    
