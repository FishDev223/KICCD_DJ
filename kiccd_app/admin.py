from django.contrib import admin
from django.http import HttpResponse
from django.utils.encoding import smart_str
import csv
import pyperclip
from .models import *

class MyAdminSite(admin.AdminSite):
    class Media:
        css = {
            'all': ('static/kiccd_app/css/admin-custom.css',)
        }



class PoolAdmin(admin.ModelAdmin):
    list_display = ("pool_id", "name", "abbrev", "lat", 
                    "lon", "midpoint_rm", "length_mi", "dam_rm", 
                    "dam_lat", "dam_lon", "bhc_status", "blc_status", 
                    "grc_status", "svc_status", 
                    )

    search_fields = ('name', 'abbrev')
    readonly_fields = ('pool_id', 'last_update')
    ordering = ('pool_id',)
    fieldsets = (
        (None, {
            'fields': ('name', 'abbrev', 'lat', 'lon', 'midpoint_rm', 'length_mi', 'dam_rm', 'dam_lat', 'dam_lon', 'boundary', 'bhc_status', 'blc_status', 'grc_status', 'svc_status',)
        }),
        ('Timestamps', {
            'fields': ('last_update',),
            'classes': ('collapse',),
        }),
    )

class BasinAdmin(admin.ModelAdmin):
    list_display = ("basin_id", "name", "abbrev",)
    search_fields = ('name', 'abbrev')
    readonly_fields = ('basin_id', 'last_update')
    ordering = ('basin_id',)
    fieldsets = (
        (None, {
            'fields': ('name', 'abbrev', 'boundary',)
        }),
        ('Timestamps', {
            'fields': ('last_update',),
            'classes': ('collapse',),
        }),
    )

class TribAdmin(admin.ModelAdmin):
    list_display = ("trib_id", "name", "pool__abbrev", "rm",  
                    "lat", "lon", "basin", 'boundary', )
    search_fields = ('name',)
    readonly_fields = ('trib_id', 'last_update')
    ordering = ('-rm',) 
    list_editable = ['rm', 'lat', 'lon', 'boundary', ]
    list_filter = ('basin', 'pool',)
    fieldsets = (
        (None, {
            'fields': ('name', 'pool', 'basin', 'lat', 'lon', 'rm', 'boundary',)
        }),
        ('Timestamps', {
            'fields': ('last_update', 'trib_id'),
            'classes': ('collapse',),
        }),
    )

class Huc12Admin(admin.ModelAdmin):
    list_display = ("huc12", "huc12_name", "huc10", "huc10_name", "huc8", "huc8_name", "huc12_acres", "huc12_sqkm", 'boundary',)
    search_fields = ('huc12', 'huc12_name', 'huc10', 'huc10_name', 'huc8', 'huc8_name',)
    readonly_fields = ('huc_id', 'last_update')
    list_editable = ['huc12_acres', 'huc12_sqkm', 'boundary', ]
    list_filter = ("huc8_name", "huc10_name", 'huc8', 'huc10',)
    ordering = ('huc12',)
    fieldsets = (
        (None, {
            'fields': ('huc12', 'huc12_name', 'huc10', 'huc10_name', 'huc8', 'huc8_name', 'boundary',)
        }),
        ('Area Details', {
            'fields': ('huc12_acres', 'huc12_sqkm',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('last_update',),
            'classes': ('collapse',),
        }),
    )

class StateAdmin(admin.ModelAdmin):
    list_display = ("state_id", "name", "abbrev",)
    search_fields = ('name', 'abbrev')
    readonly_fields = ('state_id', 'last_update')
    ordering = ('state_id',)
    fieldsets = (
        (None, {
            'fields': ('name', 'abbrev',)
        }),
        ('Timestamps', {
            'fields': ('last_update',),
            'classes': ('collapse',),
        }),
    )

class GearAdmin(admin.ModelAdmin):
    list_display = ("gear_id", "name", "priority", "code",)
    search_fields = ('name',)
    readonly_fields = ('gear_id', 'last_update')
    list_editable = ['priority', ]
    ordering = ('priority', 'gear_id',)
    fieldsets = (
        (None, {
            'fields': ('name', 'priority', 'code',)
        }),
        ('Timestamps', {
            'fields': ('last_update',),
            'classes': ('collapse',),
        }),
    )

class PartnerAdmin(admin.ModelAdmin):
    list_display = ("partner_id", "name", "abbrev", "type", "level",)
    search_fields = ('name', 'abbrev')
    readonly_fields = ('partner_id', 'last_update')
    ordering = ('partner_id',)
    list_filter = ('type', 'level',)
    fieldsets = (
        (None, {
            'fields': ('name', 'abbrev', 'type', 'level',)
        }),
        ('Timestamps', {
            'fields': ('last_update',),
            'classes': ('collapse',),
        }),
    )

class FishSexAdmin(admin.ModelAdmin):
    list_display = ("sx_id", 'name', 'abbrev',)
    search_fields = ('name', 'abbrev',)
    ordering = ('sx_id',)
    fieldsets = (
        (None, {
            'fields': ('sx_id', 'name', 'abbrev',)
        }),
    )

class ProjectAdmin(admin.ModelAdmin):
    list_display = ("project_id", "name", "description",)
    search_fields = ('name', 'description',)
    ordering = ('project_id',)
    readonly_fields = ('last_update',)
    fieldsets = (
        (None, {
            'fields': ('project_id', 'name', 'description',)
        }),
        ('Timestamps', {
            'fields': ('last_update',),
            'classes': ('collapse',),
        }),
    )

class SiteTypeAdmin(admin.ModelAdmin):
    list_display = ("site_type_id", "name", "abbrev",)
    search_fields = ('name',)
    ordering = ('site_type_id',)
    readonly_fields = ('site_type_id', 'last_update',)
    fieldsets = (
        (None, {
            'fields': ('name', 'abbrev',)
        }),
        ('Timestamps', {
            'fields': ('last_update',),
            'classes': ('collapse',),
        }),
    )

class SitePurposeAdmin(admin.ModelAdmin):
    list_display = ("site_purpose_id", "purpose",)
    search_fields = ('purpose',)
    ordering = ('site_purpose_id',)
    readonly_fields = ('site_purpose_id', 'last_update',)
    fieldsets = (
        (None, {
            'fields': ('purpose',)
        }),
        ('Timestamps', {
            'fields': ('last_update',),
            'classes': ('collapse',),
        }),
    )

class FishSpeciesAdmin(admin.ModelAdmin):
    list_display = ("spp_id", "name", "abbrev", "scientific_name", "order_name", "family_name", "genus_name", "trophic", "ranked", "targeted" )
    search_fields = ('name', 'scientific_name', "abbrev", )
    list_editable = ['abbrev', 'trophic', 'ranked', 'targeted']
    ordering = ('-ranked',)
    readonly_fields = ('last_update',)
    fieldsets = (
        (None, {
            'fields': ('name', 'lookup', 'abbrev', 'scientific_name', 'trophic',)
        }),
        ('Taxonomy', {
            'fields': ('order_name', 'family_name', 'genus_name', 'species_name',),
            'classes': ('collapse',),
        }),
        ('Optional Fields', {
            'fields': ('ranked', 'targeted', 'spp_id', 'last_update',),
            'classes': ('collapse',),
        }),
    )

class CountyAdmin(admin.ModelAdmin):
    list_display = ("county_id", "name", "state",)
    search_fields = ('name',)
    ordering = ('county_id',)
    readonly_fields = ('county_id', 'last_update',)
    list_filter = ('state',)
    fieldsets = (
        (None, {
            'fields': ('name', 'state',)
        }),
        ('Timestamps', {
            'fields': ('last_update',),
            'classes': ('collapse',),
        }),
    )

class CrewAdmin(admin.ModelAdmin):
    list_display = ("crew_id", "leader",'office', "agency", "active",)
    list_editable = ['active',]
    search_fields = ('leader', )
    ordering = ('leader',)
    readonly_fields = ('crew_id', 'added_on', )
    list_filter = ('office', "agency",)
    fieldsets = (
        (None, {
            'fields': ('leader', 'office', 'agency', 'active', )
        }),
        ('Read-Only Fields', {
            'fields': ('crew_id', 'added_on',),
            'classes': ('collapse',),
        }),
    )

class FisherAdmin(admin.ModelAdmin):
    list_display = ("fisher_id",     
                    "name", 
                    'contracted',
                    'active',
                    'commercial_license',
                    )

    search_fields = (
                    "lookup", 
                    "name", 
                    )

    ordering = ("last_name",)
    
    readonly_fields = ('fisher_id', 'last_update',)
    list_editable = ['contracted', 'active', 'commercial_license', ]
    list_filter = ('contracted', 'active', 'commercial_license',)
    list_per_page = 50
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'contracted', 'active', 'commercial_license', )
        }),
        ('Optional', {
            'fields': ('lookup', 'name',),
            'classes': ('collapse',),
        }),
        ('Read-Only Fields', {
            'fields': ('fisher_id', 'last_update',),
            'classes': ('collapse',),
        }),
    )

class OfficeAdmin(admin.ModelAdmin):
    list_display = ("office_id", 
                    'agency',
                    "name", 
                    "abbrev", 
                    )

    search_fields = (
                    "abbrev", 
                    "name", 
                    "agency__name",
                    )

    ordering = ('office_id',)
    
    readonly_fields = ('office_id', 'last_update',)
    
    fieldsets = (
        (None, {
            'fields': ('agency', 'name', 'abbrev', )
        }),
        ('Read-Only Fields', {
            'fields': ('office_id', 'last_update',),
            'classes': ('collapse',),
        }),
    )

class ObserverAdmin(admin.ModelAdmin):
    list_display = ("observer_id",     
                    "name", 
                    "agency", 
                    "active",
                    )
    search_fields = ("name", )
    ordering = ("name",)
    list_filter = ("agency", "active",)
    list_editable = ['active', ]
    list_per_page = 10
    readonly_fields = ('observer_id', 'last_update',)
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'agency', 'active', )
        }),
        ('Timestamps', {
            'fields': ('last_update',),
            'classes': ('collapse',),
        }),
    )

class DatesAdmin(admin.ModelAdmin):
    list_display = ("idate",     
                    "cal_year", 
                    "fis_year", 
                    "ic_proj_year", 
                    "cf_peak_season", 
                    "ic_season", 
                    "ic_month1", 
                    "ic_month2", 
                    "ic_mon", 
                    "ic_weeknum", 
                    )

    search_fields = ("ic_date",     
                    "ic_season", 
                    "ic_month2", 
                    "ic_mon", 
                    )
    list_filter = ("cal_year", 'fis_year',)
    ordering = ('ic_date',)
    readonly_fields = ('dates_id',)

    def idate(self, obj):
        return obj.ic_date.strftime('%Y-%m-%d')
    idate.admin_order_field = 'ic_date'
    idate.short_description = 'Date'

class SampleSiteAdmin(admin.ModelAdmin):
    list_display = ('site_id', 
                    'name', 
                    'latitude', 
                    'longitude', 
                    'river_mi', 
                    'pool', 
                    'county', 
                    'trib', 
                    'type', 
                    'basin', )
    search_fields = ('site_code', 'name', 'trib__name',)
    list_filter = ('type', 'pool', 'trib', 'basin', 'state',)
    ordering = ('pool', 'river_mi',)
    readonly_fields = ('site_id', 'added_on',)
    fieldsets = (
        ('Site Specific', {
            'fields': ('name', 
                       'latitude', 
                       'longitude',
                       'river_mi',
                       'type',
                       'woody_debris', 
                       'submersed_av',)
        }),
        ('General Location Info', {
            'fields': ('pool',
                       'basin',
                       'trib',
                       'county',
                       'state',),
            'classes': ('collapse',),
        }),
        ('Other Details', {
            'fields': ('site_code','added_on',),
            'classes': ('collapse',),
        }),
    )

class FishingSiteCFAdmin(admin.ModelAdmin):
    list_display = ('site_id', 
                'name', 
                'latitude', 
                'longitude', 
                'river_mi', 
                'pool__abbrev', 
                'trib', 
                'type', )
    search_fields = ('site_code', 'name', 'trib__name',)
    ordering = ('pool', 'river_mi',)
    list_filter = ('pool', 'type', )
    list_editable = ['river_mi', ]
    readonly_fields = ('site_id', 'added_on',)
    fieldsets = (
        ('Site Specific', {
            'fields': ('name', 
                       'latitude', 
                       'longitude',
                       'river_mi',
                       'type', )
        }),
        ('General Location Info', {
            'fields': ('pool',
                       'basin',
                       'trib',
                       'county',
                       'state',),
            'classes': ('collapse',),
        }),
        ('Other Details', {
            'fields': ('site_id', 'site_code', 'added_on',),
            'classes': ('collapse',),
        }),
    )

class FishingSiteHPAdmin(admin.ModelAdmin):
    list_display = ('site_id', 
                'name', 
                'latitude', 
                'longitude', 
                'river_mi', 
                'pool__abbrev', 
                'county',
                'trib', 
                'type', 
                'basin__abbrev', )
    search_fields = ('name',)
    ordering = ('site_id',)
    list_filter = ('basin', 'trib', 'type',  )
    list_editable = ['river_mi', ]
    readonly_fields = ('site_id', 'added_on',)
    fieldsets = (
        ('Site Specific', {
            'fields': ('name', 
                       'latitude', 
                       'longitude',
                       'river_mi',
                       'type', )
        }),
        ('General Location Info', {
            'fields': ('pool',
                       'basin',
                       'trib',
                       'county',
                       'state',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('site_id','added_on',),
            'classes': ('collapse',),
        }),
    )

class IcAgeGrowthAdmin(admin.ModelAdmin):
    list_display = ('agdate', 'pool', 'site', 'spp__name', 'sex', 'length_mm', 'weight_g', 'ic_age', )
    search_fields = ('pool__name', 'site__name', 'spp__name', )
    ordering = ('-catch_date', 'site', 'spp',)
    list_filter = ('pool', 'sex', 'datez__cal_year', 'datez__ic_month2', 'datez__ic_season', )
    readonly_fields = ('age_id', 'added_on', 'added_by', )
    fieldsets = (
        ('Fish Details', {
            'fields': ('catch_date', 'spp', 'sex', 'length_mm', 'weight_g', 'ic_age', )
        }),
        ('Location Details', {
            'fields': ('agency', 
                       'project', 
                       'site',
                       'latitude',
                       'longitude',
                       'pool',
                       'basin', ),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('added_on', 'added_by',),
            'classes': ('collapse',),
        }),
    )

    def agdate(self, obj):
        return obj.catch_date.strftime('%Y-%m-%d')
    agdate.admin_order_field = 'catch_date'
    agdate.short_description = 'Date'

    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)

class CfEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'cfdate', 'fisher', 'observer__last_name', 'site', 'gear', 'set_num', 'latitude', 'longitude', 'stime', 'etime', 'gear_length', 'gear_depth', 'mesh_size', )
    search_fields = ('fisher__name', 'site__name', )
    ordering = ('-cf_date', 'fisher', 'set_num', )
    list_filter = ('site__pool', 'fisher__name',  'datez__cal_year', 'datez__cf_peak_season', 'datez__ic_month2', 'datez__ic_season',)
    readonly_fields = ('event_id', 'added_on', 'added_by', )
    fieldsets = (
        (None, {
            'fields': ('cf_date', 'fisher', 'observer', 'site', )
        }), 
        ('Gear Details', {
            'fields': ('gear', 'latitude', 'longitude', 'set_num', 'start_time', 'end_time', 'gear_length', 'gear_depth', 'mesh_size', 'water_temp_f', ), 
            'classes': ('collapse',),
        }), 
        ('Read-Only Info', {
            'fields': ('event_id', 'added_on', 'added_by', ),
            'classes': ('collapse',),
        }),
    )

    def cfdate(self, obj):
        return obj.cf_date.strftime('%Y-%m-%d')
    
    def stime(self, obj):
        return obj.start_time.strftime('%H:%M') if obj.start_time else '-'

    def etime(self, obj):
        return obj.end_time.strftime('%H:%M') if obj.end_time else '-'
	
    cfdate.admin_order_field = 'cf_date'
    stime.admin_order_field = 'start_time'
    etime.admin_order_field = 'end_time'

    cfdate.short_description = 'Date'
    stime.short_description = 'Set Time'
    etime.short_description = 'Pull Time'

    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)

class CfCatchAdmin(admin.ModelAdmin):
    list_display = ('catch_id', 'event', 'ev_pool', 'ev_site', 'spp', 'healthy_cnt', 'moribund_cnt', 'total_cnt', 'mean_length_mm', 'mean_weight_g', 'predicted_weight_g', 'ss_code', )
    search_fields = ('event__fisher__name', 'species__name', 'event__site__name', 'event__cf_date', )
    ordering = ('-event__cf_date', 'event__fisher', 'event__site', 'event__set_num', )
    list_editable = ['healthy_cnt', 'moribund_cnt', 'total_cnt', 'mean_length_mm', 'mean_weight_g', 'predicted_weight_g', 'ss_code', ]
    list_filter = ('species', 'event__site__pool', 'event__fisher__name', )
    readonly_fields = ('catch_id', 'added_on', 'added_by', )
    fieldsets = (
        (None, {
            'fields': ('event', )
        }),
        ('Catch Details', {
            'fields': ('species', 'healthy_cnt', 'moribund_cnt', 'total_cnt','mean_length_mm', 'mean_weight_g', 'predicted_weight_g', ),
            'classes': ('collapse',),
        }),
        ('Optional', {
            'fields': ('ss_code',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('catch_id', 'added_on', 'added_by',),
            'classes': ('collapse',),
        }),
    )

    def spp(self, obj):
        return obj.species.name if obj.species else '-'

    spp.admin_order_field = 'species__name'
    spp.short_description = 'Species'

    def ev_pool(self, obj):
        return obj.event.site.pool.abbrev if obj.event and obj.event.site and obj.event.site.pool else '-'

    ev_pool.admin_order_field = 'event__site__pool__abbrev'
    ev_pool.short_description = 'Pool'

    def ev_site(self, obj):
        return obj.event.site.name if obj.event and obj.event.site else '-'

    ev_site.admin_order_field = 'event__site__name'
    ev_site.short_description = 'Site'

    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)

class RaEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'radate', 'fisher', 'site', 'gear', 'net_set', 'latitude', 'longitude', 'stime', 'etime', 'net_num', 'gear_length', 'gear_depth', 'mesh_size', )
    search_fields = ('fisher__name', 'site__name', )
    ordering = ('-ra_date', 'fisher', 'net_set', 'net_num', )
    list_filter = ('site__basin', 'fisher__name',  'datez__cal_year', 'datez__ic_month2', 'datez__ic_season',)
    readonly_fields = ('event_id', 'added_on', 'added_by', )
    fieldsets = (
        (None, {
            'fields': ('ra_date', 'fisher', 'observer', 'site', )
        }), 
        ('Gear Details', {
            'fields': ('gear', 'net_set', 'latitude', 'longitude', 'start_time', 'end_time', 'net_num', 'gear_length', 'gear_depth', 'mesh_size', ), 
            'classes': ('collapse',),
        }), 
        ('Read-Only Info', {
            'fields': ('event_id', 'added_on', 'added_by', ),
            'classes': ('collapse',),
        }),
    )

    def radate(self, obj):
        return obj.ra_date.strftime('%Y-%m-%d')
    
    def stime(self, obj):
        return obj.start_time.strftime('%Y-%m-%d %H:%M')

    def etime(self, obj):
        return obj.end_time.strftime('%Y-%m-%d %H:%M')
	
    radate.admin_order_field = 'ra_date'
    stime.admin_order_field = 'start_time'
    etime.admin_order_field = 'end_time'

    radate.short_description = 'Date'
    stime.short_description = 'Set Time'
    etime.short_description = 'Pull Time'

    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)

class RaCatchAdmin(admin.ModelAdmin):
    list_display = ('catch_id', 'event', 'species__name', 'rel_healthy_cnt', 'rel_moribund_cnt', 'harvest_cnt', 'total_cnt', 'mean_length_mm', 'mean_weight_g', 'predicted_weight_g', )
    search_fields = ('event__fisher__name', 'species__name', 'event__site__name')
    ordering = ('-event__ra_date', 'event__fisher', 'species', )
    list_filter = ('species', 'event__site__basin', 'event__fisher__name', )
    readonly_fields = ('catch_id', 'added_on', 'added_by', )
    fieldsets = (
        (None, {
            'fields': ('event', )
        }),
        ('Catch Details', {
            'fields': ('species', 'rel_healthy_cnt', 'rel_moribund_cnt', 'harvest_cnt', 'total_cnt','mean_length_mm', 'mean_weight_g', 'predicted_weight_g', ),
            'classes': ('collapse',),
        }),
        ('Optional', {
            'fields': ('ss_code',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('catch_id', 'added_on', 'added_by',),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)

class IcEventAdmin(admin.ModelAdmin):
    list_display = ('edate', 'project', 'agency__abbrev', 'crew_lead', 'site__name', 'gear', 'effort_num', 'effort_min', 'carp_sighted', 'net_length_ft', )
    list_editable = ('effort_num', 'effort_min', 'carp_sighted', 'project', )
    search_fields = ('project__name', 'site__name', 'event_date' )
    ordering = ('-event_date', 'effort_num', )
    list_filter = ('project', 'agency', 'gear', 'site__pool', 'datez__cal_year', 'datez__ic_month2', 'datez__ic_season', )
    readonly_fields = ('event_id', 'added_on', 'added_by', )
    fieldsets = (
        (None, {
            'fields': ('event_date', 'project', 'agency', 'crew_lead', 'site', )
        }), 
        ('Gear Info', {
            'fields': ('gear', 'latitude', 'longitude', 'effort_num', 'effort_min', 'start_time', 'end_time', 'bankside', ), 
            'classes': ('collapse',),
        }),         
        ('Electrofishing Details', {
            'fields': ('ef_duty_cycle', 'ef_pps_hertz', 'ef_voltage', 'ef_amps', 'ef_watts', 'dipper_cnt', 'run_distance', ), 
            'classes': ('collapse',),
        }),         
        ('Gill Netting Details', {
            'fields': ('net_length_ft', 'net_depth_ft', 'mesh_size_in', 'egn_panel_num', 'net_set_type', 'event_loc_type', ), 
            'classes': ('collapse',),
        }),         
        ('Environmental Measurements', {
            'fields': ('weather', 'water_temp_f', 'air_temp_f', 'secchi_depth_in', 'ef_cond', 'water_ph','wind_speed_mph', ), 
            'classes': ('collapse',),
        }), 
        ('Presence/Absence', {
            'fields': ('carp_sighted', 'yoy_sighted', )
        }),  
        ('Read-Only Info', {
            'fields': ('event_id', 'added_on', 'added_by', ),
            'classes': ('collapse',),
        }),
    )
    
    def edate(self, obj):
        return obj.event_date.strftime('%Y-%m-%d')
    edate.admin_order_field = 'event_date'
    edate.short_description = 'Date'

    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)

class IcCatchAdmin(admin.ModelAdmin):
    list_display = ('event', 'event__agency', 'event__crew_lead', 'event__gear', 'event__effort_num', 'event__effort_min', 'species__abbrev', 'fish_sex__abbrev', 'length_mm', 'weight_g', 'fish_count', )
    search_fields = ('event__site__name', 'species__name', 'event__event_date', )
    ordering = ('-catch_id', )
    list_editable = ['length_mm', 'weight_g', 'fish_count', ]
    list_filter = ('event__project', 'event__agency', 'event__crew_lead', 'event__gear', 'event__site__pool', 'event__site__basin', )
    readonly_fields = ('catch_id', 'added_on', 'added_by', )
    fieldsets = (
        (None, { 'fields': ('event', 'species', 'fish_sex', 'length_mm', 'weight_g', 'fish_count', 'collected4ag', 'gonad_stage', 'gonad_wt_g', )}),
        ('Timestamps', {
            'fields': ('catch_id', 'added_on', 'added_by',),
            'classes': ('collapse',),
        }),
    )

 
    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)

class SubsampleAdmin(admin.ModelAdmin):
    list_display = ('ssdate', 'basin', 'fisher', 'spp', 'sex', 'length_mm', 'weight_g', 'ss_code', )
    search_fields = ('ss_code', 'cf_date', 'fisher__name', 'spp__name', 'basin__name', )
    ordering = ('cf_date', 'fisher', 'spp',)
    list_editable = ['length_mm', 'weight_g', 'ss_code', ]
    # ordering = ('-ss_id', )
    list_filter = ('pool', 'basin', 'spp', 'datez__cal_year', 'datez__cf_peak_season', "datez__ic_month2", "datez__ic_season",)
    readonly_fields = ('ss_id', 'added_on',)
    fieldsets = (
        ('Event Details', {
            'fields': ('cf_date', 'fisher', 'observer', 'pool', 'basin', )
        }),
        ('Fish Info', {
            'fields': ('spp', 'sex', 'length_mm', 'weight_g',),
            # 'classes': ('collapse',),
        }),
        ('Optional', {
            'fields': ('ss_code',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('ss_id', 'added_on',),
            'classes': ('collapse',),
        }),
    )

    def ssdate(self, obj):
        return obj.cf_date.strftime('%Y-%m-%d')
    ssdate.admin_order_field = 'cf_date'
    ssdate.short_description = 'Date'

    def basinz(self, obj):
        return obj.basin.abbrev
    basinz.admin_order_field = 'basin__abbrev'
    basinz.short_description = 'Basins'

    #def save_model(self, request, obj, form, change):
    #    obj.save(user=request.user)

class IchpEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'ichpdate', 'fisher', 'basin', 'gear', 'net_haul', 'gear_length', 'gear_depth', 'mesh_size', 'site', 'latitude', 'longitude', 'stime', 'etime', 'observed',)
    search_fields = ('fisher__name', 'basin__name', )
    ordering = ('-ichp_date', 'fisher', 'net_haul', )
    list_filter = ('site__basin', 'fisher__name',  'datez__cal_year', 'datez__ic_month2', 'datez__ic_season',)
    readonly_fields = ('event_id', 'added_on', 'added_by', )
    fieldsets = (
        (None, {
            'fields': ('ichp_date', 'fisher', 'basin', 'observed', )
        }), 
        ('Gear Details', {
            'fields': ('gear', 'net_haul', 'gear_length', 'gear_depth', 'mesh_size', 'start_time', 'end_time', ), 
            'classes': ('collapse',),
        }),  
        ('Location Specifics', {
            'fields': ('site', 'latitude', 'longitude', ), 
            'classes': ('collapse',),
        }), 
        ('Read-Only Info', {
            'fields': ('event_id', 'added_on', 'added_by', ),
            'classes': ('collapse',),
        }),
    )

    def ichpdate(self, obj):
        return obj.ichp_date.strftime('%Y-%m-%d')
    
    def stime(self, obj):
        if obj.start_time:
            return obj.start_time.strftime('%H:%M')
        return 'NA'

    def etime(self, obj):
        if obj.end_time:
            return obj.end_time.strftime('%H:%M')
        return 'NA'
	
    ichpdate.admin_order_field = 'ichp_date'
    stime.admin_order_field = 'start_time'
    etime.admin_order_field = 'end_time'

    ichpdate.short_description = 'Date'
    stime.short_description = 'Time Set'
    etime.short_description = 'Time Pulled'

    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)

class IchpCatchAdmin(admin.ModelAdmin):
    list_display = ('catch_id', 'event', 'event__basin__name', 'species__name', 'rel_healthy_cnt', 'rel_moribund_cnt', 'harvest_cnt', 'total_cnt', 'reported_weight_lb', 'reported_mean_length_in', 'calc_mean_weight_g', )
    search_fields = ('event__fisher__name', 'species__name', 'event__basin__name')
    ordering = ('-event__ichp_date', 'event__fisher', 'event__net_haul', 'species', )
    list_filter = ('species', 'event__basin', 'event__fisher__name', )
    list_editable = ['rel_healthy_cnt', 'rel_moribund_cnt', 'harvest_cnt', 'total_cnt',  'calc_mean_weight_g', ]
    readonly_fields = ('catch_id', 'added_on', 'added_by', 'ss_code', )
    fieldsets = (
        (None, {
            'fields': ('event', )
        }),
        ('Catch Details', {
            'fields': ('species', 'rel_healthy_cnt', 'rel_moribund_cnt', 'harvest_cnt', 'total_cnt', 'reported_weight_lb', 'reported_mean_length_in', 'calc_mean_weight_g', ),
            'classes': ('collapse',),
        }),
        ('Optional Measurements', {
            'fields': ('ss_mean_length_mm', 'ss_mean_weight_g', 'predicted_mean_weight_g', ),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('catch_id', 'ss_code', 'added_on', 'added_by',),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)



admin.site.register(Subsample, SubsampleAdmin)
admin.site.register(Pool, PoolAdmin)
admin.site.register(Basin, BasinAdmin)  
admin.site.register(Trib, TribAdmin)
admin.site.register(Gear, GearAdmin)
admin.site.register(Partner, PartnerAdmin)
# admin.site.register(State, StateAdmin)
# admin.site.register(FishSex, FishSexAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(SiteType, SiteTypeAdmin)
# admin.site.register(SitePurpose, SitePurposeAdmin)
admin.site.register(FishSpecies, FishSpeciesAdmin)
admin.site.register(County, CountyAdmin)
admin.site.register(Crew, CrewAdmin)
admin.site.register(Fisher, FisherAdmin)
admin.site.register(Office, OfficeAdmin)
admin.site.register(Observer, ObserverAdmin)
admin.site.register(Dates, DatesAdmin)
admin.site.register(SampleSite, SampleSiteAdmin)
admin.site.register(FishingSite_CF, FishingSiteCFAdmin)
admin.site.register(FishingSite_HP, FishingSiteHPAdmin)
admin.site.register(IcAgeGrowth, IcAgeGrowthAdmin)
admin.site.register(CfEvent, CfEventAdmin)
admin.site.register(CfCatch, CfCatchAdmin)
admin.site.register(RaEvent, RaEventAdmin)
admin.site.register(RaCatch, RaCatchAdmin)
admin.site.register(IcEvent, IcEventAdmin)
admin.site.register(IcCatch, IcCatchAdmin)
admin.site.register(IchpEvent, IchpEventAdmin)
admin.site.register(IchpCatch, IchpCatchAdmin)
admin.site.register(Huc12, Huc12Admin)

# admin.site = MyAdminSite()
# Adds an Admin Action that allows all selected records to be saved or downloaded as a CSV File
def export_as_csv(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta}.csv'
    writer = csv.writer(response, csv.excel)
    writer.writerow(field_names)
    for obj in queryset:
        row = writer.writerow([smart_str(getattr(obj, field)) for field in field_names])

    return response

# Adds an Admin Action that copies all selected records to be added to the clipboard in a tab-delimited format
def copy_to_clipboard(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]
    output = "\t".join(field_names) + "\n"
    for obj in queryset:
        row = "\t".join([smart_str(getattr(obj, field)) for field in field_names])
        output += row + "\n"
    # Copy the output to the windows clipboard using the pyperclip module
    pyperclip.copy(output)
    # return HttpResponse(output, content_type='text/plain')
    return None

export_as_csv.short_description = "Export Selected to CSV"
copy_to_clipboard.short_description = "Copy Selected to Clipboard"
admin.site.add_action(export_as_csv)
admin.site.add_action(copy_to_clipboard)