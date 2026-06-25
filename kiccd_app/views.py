from decimal import Decimal
import json
from math import sqrt
from datetime import datetime
from zoneinfo import ZoneInfo

from django.db import transaction
from django.db.models import Avg, Count, DecimalField, IntegerField, Sum, Value, F, ExpressionWrapper, Q, Max, Min, Case, When
from django.db.models.functions import Coalesce, ExtractYear
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.template import TemplateDoesNotExist
from django.views.generic import ListView
from django.forms import modelformset_factory
from django.contrib import messages
from django.utils import timezone

from .forms import *
from .models import *
 

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                default_group = Group.objects.get(name="Default Users")
                user.groups.add(default_group)
            except Group.DoesNotExist:
                pass
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return render(request, 'kiccd_app/home.html')
    else:
        form = CustomUserCreationForm()
    return render(request, 'kiccd_app/pages/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return render(request, 'kiccd_app/home.html')
    else:
        form = AuthenticationForm()
    return render(request, 'kiccd_app/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return render(request=request, template_name='kiccd_app/logged-out.html')


@login_required
def home_view(request):
    return render(request, 'kiccd_app/home.html')


@login_required
def site_map_view(request):
    return render(request, 'kiccd_app/pages/site-map.html')


def site_check_view(request):
    return render(request, 'kiccd_app/pages/site-check.html')


def index(request):
    if request.user.is_authenticated:
        return render(request, 'kiccd_app/home.html')
    
    registration_form = CustomUserCreationForm()
    login_form = AuthenticationForm()

    context = {
        'registration_form': registration_form,
        'login_form': login_form,
    }

    return render(request=request, template_name='kiccd_app/index.html', context=context)


def root_page_view(request):
    if request.user.is_authenticated:
        return render(request, 'kiccd_app/home.html')
    try:
        registration_form = CustomUserCreationForm()
        login_form = AuthenticationForm()
        return render(request, 'kiccd_app/index.html', {'registration_form': registration_form, 'login_form': login_form})
    except TemplateDoesNotExist:
        return render(request, 'kiccd_app/404.html')


@login_required
def dynamic_pages_view(request, template_name):
    try:
        return render(request, f'kiccd_app/pages/{template_name}.html')
    except TemplateDoesNotExist:
        return render(request, f'kiccd_app/404.html')


def sample_site_list(request):
    qs = SampleSite.objects.select_related('pool','type','basin','trib').all().order_by('pool__pool_id', 'river_mi')
    context = {
        'sites': qs,   # for template loop
    }
    return render(request, 'kiccd_app/pages/sample-site-list.html', context)


def recent_ic_events(request):
    # Create a queryset containing the last 200 records of the IcEvent model
    qs = IcEvent.objects.select_related('site', 'project', 'agency', 'crew_lead', 'gear', 'datez')
    qs = qs.all().order_by('-event_date', 'effort_num')[:200]

    events = list(qs)
    eastern_tz = ZoneInfo('America/New_York')
    for event in events:
        event.start_time_est = None
        if event.start_time:
            utc_dt = datetime.combine(event.event_date, event.start_time).replace(tzinfo=timezone.get_default_timezone())
            event.start_time_est = event.start_time.strftime('%H:%M')

    context = {
        'events': events,  # for template loop
    }
    return render(request, 'kiccd_app/pages/recent-ic-events.html', context)


def recent_cf_events(request):
    # Create a queryset containing the last 200 records of the IcEvent model
    qs = CfEvent.objects.select_related('observer', 'fisher', 'site', 'gear', 'datez')
    qs = qs.all().order_by('-cf_date', 'set_num')[:200]

    efforts = list(qs)

    for effort in efforts:
        effort.start_time_f = None
        effort.end_time_f = None
        effort.net_specs = None
        if effort.start_time:
            effort.start_time_f = effort.start_time.strftime('%H:%M')
        if effort.end_time:
            effort.end_time_f = effort.end_time.strftime('%H:%M')
        if effort.gear_length and effort.gear_depth:
            if effort.mesh_size:
                effort.net_specs = f"{effort.gear_length}' x {effort.gear_depth}' x {effort.mesh_size}\""
            else:
                effort.net_specs = f"{effort.gear_length}' x {effort.gear_depth}'"

    context = {
        'efforts': efforts,  # for template loop
    }
    return render(request, 'kiccd_app/pages/recent-cf-events.html', context)


def recent_ra_events(request):
    # Create a queryset containing the last 200 records of the RaEvent model
    qs = RaEvent.objects.select_related('observer', 'fisher', 'site', 'gear', 'datez')
    qs = qs.all().order_by('-ra_date', 'net_set', 'net_num')[:200]

    efforts = list(qs)

    for effort in efforts:
        effort.start_time_f = None
        effort.end_time_f = None
        effort.net_specs = None

        if effort.start_time:
            effort.start_time_f = effort.start_time.strftime('%Y-%m-%d %H:%M')
        if effort.end_time:
            effort.end_time_f = effort.end_time.strftime('%Y-%m-%d %H:%M')
        if effort.gear_length and effort.gear_depth:
            if effort.mesh_size:
                effort.net_specs = f"{effort.gear_length}' x {effort.gear_depth}' x {effort.mesh_size}\""
            else:
                effort.net_specs = f"{effort.gear_length}' x {effort.gear_depth}'"

    context = {
        'efforts': efforts,  # for template loop
    }
    return render(request, 'kiccd_app/pages/recent-ra-events.html', context)


def recent_ichp_events(request):
    # Create a queryset containing the last 200 records of the IchpEvent model
    qs = IchpEvent.objects.select_related('fisher', 'basin', 'site', 'gear', 'datez')
    qs = qs.all().order_by('-ichp_date', 'fisher', 'net_haul')[:3000]

    efforts = list(qs)

    for effort in efforts:
        effort.start_time_f = None
        effort.end_time_f = None
        effort.net_specs = None

        if effort.start_time:
            effort.start_time_f = effort.start_time.strftime('%H:%M')
        else:
            effort.start_time_f = "NA"
        if effort.end_time:
            effort.end_time_f = effort.end_time.strftime('%H:%M')
        else:
            effort.end_time_f = "NA"
        if effort.gear_length and effort.gear_depth:
            if effort.mesh_size:
                effort.net_specs = f"{effort.gear_length}' x {effort.gear_depth}' x {effort.mesh_size}\""
            else:
                effort.net_specs = f"{effort.gear_length}' x {effort.gear_depth}'"
        else:
            effort.net_specs = "NA"

    context = {
        'efforts': efforts,  # for template loop
    }
    return render(request, 'kiccd_app/pages/recent-ichp-events.html', context)


def cf_site_list(request):
    qs = FishingSite_CF.objects.select_related('type','pool','state','county','basin','trib').all().order_by('river_mi')
    context = {'sites': qs, }  # for template loop
    
    return render(request, 'kiccd_app/pages/fishing-sites-cf.html', context)


def hp_site_list(request):
    qs = FishingSite_HP.objects.select_related('type','pool','state','county','basin','trib').all().order_by('basin','river_mi')
    context = {'sites': qs, }  # for template loop
    
    return render(request, 'kiccd_app/pages/fishing-sites-hp.html', context)


def trib_list(request):
    qs = Trib.objects.select_related('basin','pool').all().order_by('basin','rm')
    context = {'tribs': qs, }  # for template loop
    
    return render(request, 'kiccd_app/pages/tributary-list.html', context)


def lookup_collections(request):
    """Render multiple small lookup tables on a single page: Basin, State, Partner, SiteType."""
    counties = County.objects.select_related('state').all().order_by('name')
    states = State.objects.all().order_by('abbrev')
    partners = Partner.objects.all().order_by('abbrev')
    site_types = SiteType.objects.all().order_by('abbrev')

    context = {
        'counties': counties,
        'states': states,
        'partners': partners,
        'site_types': site_types,
    }

    return render(request, 'kiccd_app/pages/lookup-collections.html', context)


@login_required
def fisher_create(request):
    """Create a new Fisher record. Requires add_fisher permission."""
    if not request.user.has_perm('kiccd_app.add_fisher'):
        return render(request, 'kiccd_app/403.html', status=403)

    if request.method == 'POST':
        form = FisherForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=True)
            messages.success(request, 'Added New Fisher.')
            return redirect('kiccd_app:fisher_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FisherForm()

    return render(request, 'kiccd_app/pages/fisher_form.html', {'form': form})


@login_required
def fisher_create_ajax(request):
    """AJAX endpoint: create a new Fisher and return JSON. Used by inline modals."""
    if not request.user.has_perm('kiccd_app.add_fisher'):
        return JsonResponse({'success': False, 'errors': {'__all__': ['You do not have permission to add fishers.']}}, status=403)
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)
    form = FisherForm(request.POST)
    if form.is_valid():
        instance = form.save(commit=True)
        return JsonResponse({'success': True, 'id': instance.pk, 'name': str(instance)})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
def ra_event_create(request):
    """Create a new RaEvent record. Requires add_raevent permission."""
    if not request.user.has_perm('kiccd_app.add_raevent'):
        return render(request, 'kiccd_app/403.html', status=403)

    if request.method == 'POST':
        form = RaEventForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save(user=request.user)
            messages.success(request, 'Recorded ride-along effort.')
            return redirect('kiccd_app:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RaEventForm()

    return render(request, 'kiccd_app/pages/ra-event-form.html', {
        'form': form,
        'site_types': SiteType.objects.order_by('name'),
        'pools': Pool.objects.order_by('pool_id'),
        'states': State.objects.order_by('name'),
        'counties': County.objects.order_by('name'),
        'basins': Basin.objects.order_by('name'),
        'tribs': Trib.objects.order_by('name'),
        'partners': Partner.objects.order_by('abbrev'),
    })


@login_required
def ra_event_set_create(request):
    """Batch-add RaEvent rows that share the same date/fisher/observer/site/gear."""
    if not request.user.has_perm('kiccd_app.add_raevent'):
        return render(request, 'kiccd_app/403.html', status=403)

    RaEventFormSet = modelformset_factory(RaEvent, form=RaEventRowForm, extra=20, can_delete=False)
    shared_form = RaEventBatchInfoForm(request.POST or None)
    formset = RaEventFormSet(request.POST or None, queryset=RaEvent.objects.none())

    if request.method == 'POST':
        print("POST data:", request.POST)  # Debugging line
        if shared_form.is_valid() and formset.is_valid():
            shared_data = shared_form.cleaned_data
            created = 0
            net_count = 0
            for form in formset:
                if not form.cleaned_data or not form.has_changed():
                    continue
                net_count += 1
                instance = form.save(commit=False)
                instance.net_num = net_count
                instance.ra_date = shared_data['ra_date']
                instance.fisher = shared_data['fisher']
                instance.observer = shared_data['observer']
                instance.site = shared_data['site']
                instance.gear = shared_data['gear']
                instance.net_set = shared_data['net_set']
                
                lat = shared_data.get('latitude')
                if lat is not None:
                    instance.latitude = float(lat)

                lon = shared_data.get('longitude')
                if lon is not None:
                    instance.longitude = float(lon)

                if shared_data['dead_set']:
                    prior_date = shared_data['ra_date'] - timezone.timedelta(days=1)
                    instance.start_time = datetime.combine(prior_date, shared_data['set_time'])
                else:                  
                    instance.start_time = datetime.combine(shared_data['ra_date'], shared_data['set_time'])
                instance.end_time = datetime.combine(shared_data['ra_date'], shared_data['pull_time'])
                
                wt = shared_data.get('water_temp_f')
                if wt is not None:
                    instance.water_temp_f = float(wt)

                wd = shared_data.get('water_depth_ft')
                if wd is not None:
                    instance.water_depth_ft = float(wd)
                
                instance.save(user=request.user)
                created += 1
            if created:
                messages.success(request, f'Added a Ride-Along set with {created} nets.')
                return redirect('kiccd_app:recent_ra_events')
            messages.info(request, 'Please fill in at least one row before submitting.')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'kiccd_app/pages/ra-event-batch-form.html', {
        'shared_form': shared_form,
        'formset': formset,
        'site_types': SiteType.objects.order_by('name'),
        'pools': Pool.objects.order_by('pool_id'),
        'states': State.objects.order_by('name'),
        'counties': County.objects.order_by('name'),
        'basins': Basin.objects.order_by('name'),
        'tribs': Trib.objects.order_by('name'),
        'partners': Partner.objects.order_by('abbrev'),
    })


def ichp_event_create(request):
    """Batch-add ICHP commercial fishing nets that share the same date/fisher/basin/gear."""
    if not request.user.has_perm('kiccd_app.add_ichpevent'):
        return render(request, 'kiccd_app/403.html', status=403)

    IchpEventFormSet = modelformset_factory(IchpEvent, form=IchpEventRowForm, extra=10, can_delete=False)
    shared_form = IchpEventBatchInfoForm(request.POST or None)
    formset = IchpEventFormSet(request.POST or None, queryset=IchpEvent.objects.none())
    
    if request.method == 'POST':
        print("POST data:", request.POST)  # Debugging line
        if shared_form.is_valid() and formset.is_valid():
            shared_data = shared_form.cleaned_data
            created = 0
            net_count = 0
            for form in formset:
                if not form.cleaned_data or not form.has_changed():
                    continue
                net_count += 1
                instance = form.save(commit=False)
                instance.net_haul = net_count
                instance.ichp_date = shared_data['ichp_date']
                instance.fisher = shared_data['fisher']
                instance.site = shared_data['site']
                instance.basin = shared_data['basin']
                instance.gear = shared_data['gear']
                lat = shared_data.get('latitude')
                lon = shared_data.get('longitude')
                stime = shared_data.get('start_time')
                etime = shared_data.get('end_time')

                if shared_data['agency_obs']:
                    instance.observed = True
                else:
                    instance.observed = False
                
                if lat is not None:
                    instance.latitude = float(lat)
                if lon is not None:
                    instance.longitude = float(lon)
                if stime is not None:
                    instance.start_time = stime
                if etime is not None:
                    instance.end_time = etime
                
                instance.save(user=request.user)
                created += 1
            if created:
                messages.success(request, f'Added {created} net haul{"s" if created > 1 else ""} reported by {shared_data["fisher"]}.')
                return redirect('kiccd_app:recent_ichp_events')
            messages.info(request, 'Please fill in at least one row before submitting.')
        else:
            messages.error(request, 'Please correct the errors below.')
            
    return render(request, 'kiccd_app/pages/ichp-event-batch-form.html', {
        'shared_form': shared_form,
        'formset': formset,
        'site_types': SiteType.objects.order_by('name'),
        'pools': Pool.objects.order_by('pool_id'),
        'states': State.objects.order_by('name'),
        'counties': County.objects.order_by('name'),
        'basins': Basin.objects.order_by('name'),
        'tribs': Trib.objects.order_by('name'),
    })


@login_required
def ichp_event_and_catch_create(request):
    """Create one ICHP effort (single net haul) and up to five associated harvest rows."""
    if not (request.user.has_perm('kiccd_app.add_ichpevent') and request.user.has_perm('kiccd_app.add_ichpcatch')):
        return render(request, 'kiccd_app/403.html', status=403)

    CatchFormSet = modelformset_factory(
        IchpCatch,
        form=IchpCatchRowForm,
        extra=10,
        can_delete=False,
        max_num=10,
        validate_max=True,
    )
    shared_form = IchpEventBatchInfoForm(request.POST or None, prefix='shared')
    event_form = IchpEventRowForm(request.POST or None, prefix='event')
    catch_formset = CatchFormSet(request.POST or None, queryset=IchpCatch.objects.none(), prefix='catch')

    if request.method == 'POST':
        if shared_form.is_valid() and event_form.is_valid() and catch_formset.is_valid():
            with transaction.atomic():
                shared_data = shared_form.cleaned_data

                event = event_form.save(commit=False)
                event.net_haul = event_form.cleaned_data.get('net_haul') or 1
                event.ichp_date = shared_data['ichp_date']
                event.fisher = shared_data['fisher']
                event.site = shared_data['site']
                event.basin = shared_data['basin']
                event.gear = shared_data['gear']
                event.observed = bool(shared_data.get('agency_obs'))

                lat = shared_data.get('latitude')
                lon = shared_data.get('longitude')
                stime = shared_data.get('start_time')
                etime = shared_data.get('end_time')

                if lat is not None:
                    event.latitude = float(lat)
                if lon is not None:
                    event.longitude = float(lon)
                if stime is not None:
                    event.start_time = stime
                if etime is not None:
                    event.end_time = etime

                event.save(user=request.user)

                created_catch = 0
                for form in catch_formset:
                    if not form.cleaned_data or not form.has_changed():
                        continue
                    catch = form.save(commit=False)
                    catch.event = event
                    if catch.total_cnt is None:
                        healthy = catch.rel_healthy_cnt or 0
                        moribund = catch.rel_moribund_cnt or 0
                        harvest = catch.harvest_cnt or 0
                        catch.total_cnt = healthy + moribund + harvest
                    catch.save(user=request.user)
                    created_catch += 1

            messages.success(
                request,
                (
                    f'Created ICHP effort #{event.event_id} (net {event.net_haul}) '
                    f'with {created_catch} harvest record{"s" if created_catch != 1 else ""}.'
                ),
            )
            return redirect('kiccd_app:ichp_event_and_catch_create')

        messages.error(request, 'Please correct the errors below.')

    return render(request, 'kiccd_app/pages/ichp-combined-form.html', {
        'shared_form': shared_form,
        'event_form': event_form,
        'catch_formset': catch_formset,
        'site_types': SiteType.objects.order_by('name'),
        'pools': Pool.objects.order_by('pool_id'),
        'states': State.objects.order_by('name'),
        'counties': County.objects.order_by('name'),
        'basins': Basin.objects.order_by('name'),
        'tribs': Trib.objects.order_by('name'),
    })


@login_required
def ra_catch_batch_create(request):
    """Add multiple RaCatch rows for a single ride-along event."""
    if not request.user.has_perm('kiccd_app.add_racatch'):
        return render(request, 'kiccd_app/403.html', status=403)

    CatchFormSet = modelformset_factory(RaCatch, form=RaCatchRowForm, extra=12, can_delete=False)
    shared_form = RaCatchEventForm(request.POST or None)
    formset = CatchFormSet(request.POST or None, queryset=RaCatch.objects.none())

    if request.method == 'POST':
        if shared_form.is_valid() and formset.is_valid():
            event = shared_form.cleaned_data['event']
            created = 0
            for form in formset:
                if not form.cleaned_data or not form.has_changed():
                    continue
                catch = form.save(commit=False)
                catch.event = event
                if catch.total_cnt is None:
                    healthy = catch.rel_healthy_cnt or 0
                    moribund = catch.rel_moribund_cnt or 0
                    harvest = catch.harvest_cnt or 0
                    catch.total_cnt = healthy + moribund + harvest
                catch.save(user=request.user)
                created += 1
            if created:
                messages.success(request, f'Submitted {created} catch records for {event}.')
                return redirect('kiccd_app:ra_catch_list')
            messages.info(request, 'Please add at least one catch row before submitting.')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'kiccd_app/pages/ra-catch-bulk-form.html', {
        'shared_form': shared_form,
        'formset': formset,
    })

 
@login_required
def ichp_catch_batch_create(request):
    """Add multiple IchpCatch rows for a single ICHP event."""
    if not request.user.has_perm('kiccd_app.add_ichpcatch'):
        return render(request, 'kiccd_app/403.html', status=403)

    CatchFormSet = modelformset_factory(IchpCatch, form=IchpCatchRowForm, extra=10, can_delete=False)
    shared_form = IchpCatchEventForm(request.POST or None)
    formset = CatchFormSet(request.POST or None, queryset=IchpCatch.objects.none())

    if request.method == 'POST':
        if shared_form.is_valid() and formset.is_valid():
            event = shared_form.cleaned_data['event']
            created = 0
            for form in formset:
                if not form.cleaned_data or not form.has_changed():
                    continue
                catch = form.save(commit=False)
                catch.event = event
                if catch.total_cnt is None:
                    healthy = catch.rel_healthy_cnt or 0
                    moribund = catch.rel_moribund_cnt or 0
                    harvest = catch.harvest_cnt or 0
                    catch.total_cnt = healthy + moribund + harvest
                catch.save(user=request.user)
                created += 1
            if created:
                messages.success(request, f'Submitted {created} harvest record{"s" if created > 1 else ""} for {event}.')
                return redirect('kiccd_app:ichp_catch_batch_create')
            messages.info(request, 'Please add at least one catch row before submitting.')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'kiccd_app/pages/ichp-catch-bulk-form.html', {
        'shared_form': shared_form,
        'formset': formset,
    })


@login_required
def observer_create(request):
    """Create a new Observer. Requires add_observer permission."""
    if not request.user.has_perm('kiccd_app.add_observer'):
        return render(request, 'kiccd_app/403.html', status=403)

    if request.method == 'POST':
        form = ObserverForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=True)
            messages.success(request, 'Added New Observer.')
            return redirect('kiccd_app:observer_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ObserverForm()

    return render(request, 'kiccd_app/pages/observer_form.html', {'form': form})


@login_required
def observer_create_ajax(request):
    """AJAX endpoint: create a new Observer and return JSON. Used by inline modals."""
    if not request.user.has_perm('kiccd_app.add_observer'):
        return JsonResponse({'success': False, 'errors': {'__all__': ['You do not have permission to add observers.']}}, status=403)
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)
    form = ObserverForm(request.POST)
    if form.is_valid():
        instance = form.save(commit=True)
        return JsonResponse({'success': True, 'id': instance.pk, 'name': str(instance)})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
def trib_create(request):
    """Create a new Trib (tributary). Requires add_trib permission."""
    if not request.user.has_perm('kiccd_app.add_trib'):
        return render(request, 'kiccd_app/403.html', status=403)

    if request.method == 'POST':
        form = TribForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=True)
            messages.success(request, 'Added New Trib.')
            return redirect('kiccd_app:trib_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TribForm()

    return render(request, 'kiccd_app/pages/trib_form.html', {'form': form})


@login_required
def sample_site_create(request):
    """Create a new SampleSite. Requires add_samplesite permission."""
    if not request.user.has_perm('kiccd_app.add_samplesite'):
        return render(request, 'kiccd_app/403.html', status=403)

    if request.method == 'POST':
        form = SampleSiteForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=True)
            messages.success(request, 'Added New Sample Site.')
            return redirect('kiccd_app:sample_sites')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SampleSiteForm()

    return render(request, 'kiccd_app/pages/sample-site-form.html', {'form': form})


@login_required
def sample_site_create_ajax(request):
    """AJAX endpoint: create a new SampleSite and return JSON. Used by inline modals."""
    if not request.user.has_perm('kiccd_app.add_samplesite'):
        return JsonResponse({'success': False, 'errors': {'__all__': ['You do not have permission to add sample sites.']}}, status=403)
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)
    form = SampleSiteForm(request.POST)
    if form.is_valid():
        instance = form.save(commit=True)
        return JsonResponse({'success': True, 'id': instance.pk, 'name': str(instance)})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
def fishing_site_cf_create(request):
    """Create a new Contract Fishing Site (FishingSite_CF). Requires add_fishingsite_cf permission."""
    if not request.user.has_perm('kiccd_app.add_fishingsite_cf'):
        return render(request, 'kiccd_app/403.html', status=403)

    if request.method == 'POST':
        form = FishingSiteCFForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=True)
            messages.success(request, 'Added New CF Site.')
            return redirect('kiccd_app:cf_sites')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FishingSiteCFForm()

    return render(request, 'kiccd_app/pages/fishing-site-cf-form.html', {'form': form})


@login_required
def cf_site_create_ajax(request):
    """AJAX endpoint: create a new FishingSite_CF and return JSON. Used by inline modals."""
    if not request.user.has_perm('kiccd_app.add_fishingsite_cf'):
        return JsonResponse({'success': False, 'errors': {'__all__': ['You do not have permission to add sites.']}}, status=403)
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)
    form = FishingSiteCFForm(request.POST)
    if form.is_valid():
        instance = form.save(commit=True)
        return JsonResponse({'success': True, 'id': instance.pk, 'name': str(instance)})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
def hp_site_create_ajax(request):
    """AJAX endpoint: create a new FishingSite_HP and return JSON. Used by inline modals."""
    if not request.user.has_perm('kiccd_app.add_fishingsite_hp'):
        return JsonResponse({'success': False, 'errors': {'__all__': ['You do not have permission to add sites.']}}, status=403)
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)
    form = FishingSiteHPForm(request.POST)
    if form.is_valid():
        instance = form.save(commit=True)
        return JsonResponse({'success': True, 'id': instance.pk, 'name': str(instance)})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
def fishing_site_hp_create(request):
    """Create a new Commercial Fishing Site (FishingSite_HP). Requires add_fishingsite_hp permission."""
    if not request.user.has_perm('kiccd_app.add_fishingsite_hp'):
        return render(request, 'kiccd_app/403.html', status=403)

    if request.method == 'POST':
        form = FishingSiteHPForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=True)
            messages.success(request, 'Added a ICHP Site.')
            return redirect('kiccd_app:hp_sites')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FishingSiteHPForm()

    return render(request, 'kiccd_app/pages/fishing-site-hp-form.html', {'form': form})


@login_required
def crew_create(request):
    """Create a new Crew. Requires add_crew permission."""
    if not request.user.has_perm('kiccd_app.add_crew'):
        return render(request, 'kiccd_app/403.html', status=403)

    if request.method == 'POST':
        form = CrewCreateForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=True)
            messages.success(request, 'Added New Crew.')
            return redirect('kiccd_app:crew_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CrewCreateForm()

    return render(request, 'kiccd_app/pages/crew_form.html', {'form': form})


@login_required
def crew_create_ajax(request):
    """AJAX endpoint: create a new Crew and return JSON. Used by inline modals."""
    if not request.user.has_perm('kiccd_app.add_crew'):
        return JsonResponse({'success': False, 'errors': {'__all__': ['You do not have permission to add crew leaders.']}}, status=403)
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)
    form = CrewCreateForm(request.POST)
    if form.is_valid():
        instance = form.save(commit=True)
        return JsonResponse({'success': True, 'id': instance.pk, 'name': str(instance)})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
def ic_event_create(request):
    """Create a new IcEvent record. Requires add_icevent permission."""
    if not request.user.has_perm('kiccd_app.add_icevent'):
        return render(request, 'kiccd_app/403.html', status=403)

    if request.method == 'POST':
        form = IcEventForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save(user=request.user)
            messages.success(request, 'Recorded agency sampling event.')
            return redirect('kiccd_app:ic_catch_create')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = IcEventForm()

    return render(request, 'kiccd_app/pages/sample-event-form.html', {
        'form': form,
        'partners': Partner.objects.order_by('abbrev'),
        'site_types': SiteType.objects.order_by('name'),
        'pools': Pool.objects.order_by('pool_id'),
        'states': State.objects.order_by('name'),
        'basins': Basin.objects.order_by('name'),
    })


@login_required
def ic_catch_create(request):
    """Capture multiple IcCatch rows tied to a single IcEvent."""
    if not request.user.has_perm('kiccd_app.add_iccatch'):
        return render(request, 'kiccd_app/403.html', status=403)

    max_ic_catch_forms = 250
    exceeded_max_forms = False
    CatchFormSet = modelformset_factory(
        IcCatch,
        form=IcCatchForm,
        extra=25,
        can_delete=False,
        max_num=max_ic_catch_forms,
        validate_max=True,
    )
    post_data = request.POST or None
    catch_snapshot = []
    if request.method == 'POST' and post_data is not None:
        mutable_post = post_data.copy()
        snapshot_raw = mutable_post.get('catch_snapshot')
        if snapshot_raw:
            try:
                parsed_snapshot = json.loads(snapshot_raw)
                if isinstance(parsed_snapshot, list):
                    catch_snapshot = parsed_snapshot
            except (TypeError, ValueError, json.JSONDecodeError):
                catch_snapshot = []

        def _snapshot_row_has_data(row):
            if not isinstance(row, dict):
                return False
            scalar_keys = (
                'species',
                'length_mm',
                'weight_g',
                'fish_sex',
                'fish_count',
                'gonad_stage',
                'gonad_wt_g',
            )
            if any(str(row.get(key, '')).strip() != '' for key in scalar_keys):
                return True
            return bool(row.get('spawn_patch')) or bool(row.get('collected4ag'))

        def _apply_snapshot_rows(target_post, rows, max_rows):
            row_count = min(len(rows), max_rows)
            for index, row in enumerate(rows[:row_count]):
                prefix = f'form-{index}-'
                target_post[f'{prefix}species'] = str(row.get('species', '') or '')
                target_post[f'{prefix}length_mm'] = str(row.get('length_mm', '') or '')
                target_post[f'{prefix}weight_g'] = str(row.get('weight_g', '') or '')
                target_post[f'{prefix}fish_sex'] = str(row.get('fish_sex', '') or '')
                target_post[f'{prefix}fish_count'] = str(row.get('fish_count', '') or '')
                target_post[f'{prefix}gonad_stage'] = str(row.get('gonad_stage', '') or '')
                target_post[f'{prefix}gonad_wt_g'] = str(row.get('gonad_wt_g', '') or '')
                target_post[f'{prefix}spawn_patch'] = 'on' if row.get('spawn_patch') else ''
                target_post[f'{prefix}collected4ag'] = 'on' if row.get('collected4ag') else ''
            target_post['form-TOTAL_FORMS'] = str(row_count)
            return row_count

        snapshot_rows = [row for row in catch_snapshot if _snapshot_row_has_data(row)]
        if len(snapshot_rows) > max_ic_catch_forms:
            exceeded_max_forms = True
        posted_indexes = []
        for key in mutable_post.keys():
            if not key.startswith('form-'):
                continue
            parts = key.split('-')
            if len(parts) < 3:
                continue
            try:
                posted_indexes.append(int(parts[1]))
            except (TypeError, ValueError):
                continue

        posted_row_count = (max(posted_indexes) + 1) if posted_indexes else 0
        try:
            declared_total_forms = int(mutable_post.get('form-TOTAL_FORMS', 0))
        except (TypeError, ValueError):
            declared_total_forms = 0
        if declared_total_forms > max_ic_catch_forms:
            exceeded_max_forms = True

        normalized_declared_forms = min(max(declared_total_forms, 0), max_ic_catch_forms)
        normalized_posted_forms = min(max(posted_row_count, 0), max_ic_catch_forms)
        effective_posted_forms = max(normalized_declared_forms, normalized_posted_forms)
        if posted_row_count > max_ic_catch_forms:
            exceeded_max_forms = True
        mutable_post['form-TOTAL_FORMS'] = str(effective_posted_forms)

        # Canonical source: when snapshot exists, rebuild form rows from it to avoid
        # management-form drift causing truncated submissions.
        snapshot_count = min(len(snapshot_rows), max_ic_catch_forms)
        if snapshot_count:
            _apply_snapshot_rows(mutable_post, snapshot_rows, max_ic_catch_forms)
        post_data = mutable_post

    shared_form = EventSelectForm(post_data)
    formset = CatchFormSet(post_data, queryset=IcCatch.objects.none())

    if request.method == 'POST':
        if exceeded_max_forms:
            messages.warning(
                request,
                f'Only the first {max_ic_catch_forms} rows were processed. Additional rows were not submitted.',
            )
        if shared_form.is_valid() and formset.is_valid():
            event = shared_form.cleaned_data['event']
            created = 0

            with transaction.atomic():
                for form in formset:
                    if not form.cleaned_data or not form.has_changed():
                        continue
                    catch = form.save(commit=False)
                    catch.event = event
                    catch.save(user=request.user)
                    created += 1
            if created:
                messages.success(request, f'Saved {created} catch records for {event}.')
                return redirect('kiccd_app:home')
            else:
                messages.info(request, 'Add at least one catch row before submitting.')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'kiccd_app/pages/ic-catch-bulk-form.html', {
        'shared_form': shared_form,
        'formset': formset,
        'catch_snapshot': catch_snapshot,
        'event_has_errors': bool(shared_form.errors.get('event')),
    })


@login_required
def ic_catch_stats(request):
    """Return aggregated IcCatch statistics for dashboard widgets."""
    if not request.user.has_perm('kiccd_app.view_iccatch'):
        return JsonResponse({'detail': 'Permission denied.'}, status=403)

    requested_year = request.GET.get('year')
    try:
        year = int(requested_year) if requested_year else timezone.now().year
    except ValueError:
        year = timezone.now().year

    species_query = request.GET.get('species')
    species_id = request.GET.get('species_id')
    species_obj = None
    if species_id:
        try:
            species_obj = FishSpecies.objects.get(pk=int(species_id))
        except (FishSpecies.DoesNotExist, ValueError):
            species_obj = None

    species_lookup = species_query.strip() if species_query else None
    if not species_obj and species_lookup:
        species_obj = FishSpecies.objects.filter(name__iexact=species_lookup).first()
    if not species_obj and species_lookup:
        species_obj = FishSpecies.objects.filter(lookup__iexact=species_lookup).first()
    if not species_obj:
        species_obj = FishSpecies.objects.filter(name__iexact='Silver Carp').first()

    queryset = IcCatch.objects.filter(event__event_date__year=year)
    if species_obj:
        queryset = queryset.filter(species=species_obj)

    aggregates = queryset.aggregate(
        record_count=Coalesce(Count('pk'), Value(0), output_field=IntegerField()),
        total_fish=Coalesce(Sum('fish_count'), Value(0, output_field=IntegerField()), output_field=IntegerField()),
        total_weight=Coalesce(Sum('weight_g'), Value(0, output_field=DecimalField()), output_field=DecimalField()),
        average_length=Coalesce(Avg('length_mm'), Value(0, output_field=DecimalField()), output_field=DecimalField()),
        average_weight=Coalesce(Avg('weight_g'), Value(0, output_field=DecimalField()), output_field=DecimalField()),
    )

    def _serialize(value):
        return float(value) if isinstance(value, Decimal) else value

    stats = {key: _serialize(val) for key, val in aggregates.items()}
    payload = {
        'year': year,
        'species': species_obj.name if species_obj else species_lookup,
        'species_id': species_obj.pk if species_obj else None,
        'requested_species': species_lookup,
        'stats': stats,
    }
    return JsonResponse({'data': payload})

 
@login_required
def yearly_totals(request):
    """Return year-over-year totals for a species (default Silver Carp) across all catch sources."""
    required_perms = (
        'kiccd_app.view_cfcatch',
        'kiccd_app.view_racatch',
        'kiccd_app.view_iccatch',
        'kiccd_app.view_ichpcatch',
    )
    if not any(request.user.has_perm(perm) for perm in required_perms):
        return JsonResponse({'detail': 'Permission denied.'}, status=403)

    default_species = 'Silver Carp'
    species_param = request.GET.get('species')
    species_lookup = species_param.strip() if species_param else default_species
    species_id = request.GET.get('species_id')

    species_obj = None
    if species_id:
        try:
            species_obj = FishSpecies.objects.get(pk=int(species_id))
        except (ValueError, FishSpecies.DoesNotExist):
            species_obj = None
    if not species_obj and species_lookup:
        species_obj = FishSpecies.objects.filter(name__iexact=species_lookup).first()
    if not species_obj and species_lookup:
        species_obj = FishSpecies.objects.filter(lookup__iexact=species_lookup).first()
    if not species_obj and species_lookup != default_species:
        species_obj = FishSpecies.objects.filter(name__iexact=default_species).first()
        species_lookup = default_species
    if not species_obj:
        return JsonResponse({'detail': f'Species "{species_lookup}" not found.'}, status=404)

    def _parse_year(param):
        value = request.GET.get(param)
        if value in (None, ''):
            return None
        try:
            return int(value)
        except ValueError:
            return None

    start_year = _parse_year('start_year')
    end_year = _parse_year('end_year')
    if start_year is not None and end_year is not None and start_year > end_year:
        start_year, end_year = end_year, start_year

    def _yearly_totals(queryset, date_field, count_field):
        annotated = queryset.filter(species=species_obj).annotate(
            year=ExtractYear(F(date_field))
        )
        if start_year is not None:
            annotated = annotated.filter(year__gte=start_year)
        if end_year is not None:
            annotated = annotated.filter(year__lte=end_year)
        rows = annotated.values('year').annotate(
            total=Coalesce(Sum(count_field), Value(0), output_field=IntegerField())
        ).order_by('year')
        return {row['year']: int(row['total']) for row in rows if row['year'] is not None}

    cf_totals = _yearly_totals(CfCatch.objects.all(), 'event__cf_date', 'total_cnt')
    ra_totals = _yearly_totals(RaCatch.objects.all(), 'event__ra_date', 'total_cnt')
    ic_totals = _yearly_totals(IcCatch.objects.all(), 'event__event_date', 'fish_count')
    ichp_totals = _yearly_totals(IchpCatch.objects.all(), 'event__ichp_date', 'total_cnt')

    observed_years = sorted(set(cf_totals) | set(ra_totals) | set(ic_totals) | set(ichp_totals))
    if observed_years:
        range_start = start_year if start_year is not None else observed_years[0]
        range_end = end_year if end_year is not None else observed_years[-1]
    else:
        current_year = timezone.now().year
        range_start = start_year if start_year is not None else current_year
        range_end = end_year if end_year is not None else current_year
    if range_start > range_end:
        range_start, range_end = range_end, range_start

    year_sequence = list(range(range_start, range_end + 1))

    def _entry(year):
        cf_value = cf_totals.get(year, 0)
        ra_value = ra_totals.get(year, 0)
        ic_value = ic_totals.get(year, 0)
        ichp_value = ichp_totals.get(year, 0)
        total = cf_value + ra_value + ic_value + ichp_value
        return {
            'year': year,
            'contract_fishing': cf_value,
            'ride_along': ra_value,
            'agency_sampling': ic_value,
            'ichp_reports': ichp_value,
            'total': total,
        }

    series = [_entry(year) for year in year_sequence]
    summary = {
        'contract_fishing': sum(item['contract_fishing'] for item in series),
        'ride_along': sum(item['ride_along'] for item in series),
        'agency_sampling': sum(item['agency_sampling'] for item in series),
        'ichp_reports': sum(item['ichp_reports'] for item in series),
        'total': sum(item['total'] for item in series),
    }

    payload = {
        'species': species_obj.name,
        'species_id': species_obj.pk,
        'requested_species': species_lookup,
        'start_year': year_sequence[0] if year_sequence else None,
        'end_year': year_sequence[-1] if year_sequence else None,
        'series': series,
        'source_totals': summary,
    }
    return JsonResponse({'data': payload})
 

@login_required
def cf_fisher_day_count(request):
    """Return the contract fishing fisher-day count, filtered by date attributes."""
    if not (request.user.has_perm('kiccd_app.view_cfcatch') or request.user.has_perm('kiccd_app.view_cfevent')):
        return JsonResponse({'detail': 'Permission denied.'}, status=403)

    def _parse_int(param):
        raw = request.GET.get(param)
        if raw in (None, ''):
            return None
        try:
            return int(raw)
        except ValueError:
            return None

    year = _parse_int('year')
    month = _parse_int('month')
    week = _parse_int('week')
    peak_season = _parse_int('peak_season')
    pool_name = (request.GET.get('pool') or '').strip()
    fisher_name = (request.GET.get('fisher') or '').strip()
    season = (request.GET.get('season') or '').strip()

    queryset = CfEvent.objects.filter(cfcatch__isnull=False)

    if year is not None:
        queryset = queryset.filter(datez__cal_year=year)
    if month is not None:
        queryset = queryset.filter(datez__ic_month1=month)
    if week is not None:
        queryset = queryset.filter(datez__ic_weeknum=week)
    if peak_season is not None:
        queryset = queryset.filter(datez__cf_peak_season=peak_season)
    if pool_name:
        queryset = queryset.filter(
            Q(site__pool__name__iexact=pool_name) | Q(site__pool__abbrev__iexact=pool_name)
        )
    if fisher_name:
        queryset = queryset.filter(
            Q(fisher__name__icontains=fisher_name)
            | Q(fisher__first_name__icontains=fisher_name)
            | Q(fisher__last_name__icontains=fisher_name)
            | Q(fisher__lookup__icontains=fisher_name)
        )
    if season:
        queryset = queryset.filter(datez__cf_season__iexact=season)

    fisher_day_count = queryset.values('cf_date', 'fisher_id').distinct().count()

    payload = {
        'filters': {
            'year': year,
            'month': month,
            'week': week,
            'peak_season': peak_season,
            'pool': pool_name or None,
            'fisher': fisher_name or None,
            'season': season or None,
        },
        'fisher_day_count': fisher_day_count,
    }
    return JsonResponse({'data': payload})


@login_required
def cf_net_stats(request):
    """Return contract fishing net counts and total gear length with filters."""
    if not (request.user.has_perm('kiccd_app.view_cfcatch') or request.user.has_perm('kiccd_app.view_cfevent')):
        return JsonResponse({'detail': 'Permission denied.'}, status=403)

    def _parse_int(param):
        raw = request.GET.get(param)
        if raw in (None, ''):
            return None
        try:
            return int(raw)
        except ValueError:
            return None

    year = _parse_int('year')
    month = _parse_int('month')
    week = _parse_int('week')
    peak_season = _parse_int('peak_season')
    pool_name = (request.GET.get('pool') or '').strip()
    fisher_name = (request.GET.get('fisher') or '').strip()
    season = (request.GET.get('season') or '').strip()

    queryset = CfEvent.objects.filter(cfcatch__isnull=False)

    if year is not None:
        queryset = queryset.filter(datez__cal_year=year)
    if month is not None:
        queryset = queryset.filter(datez__ic_month1=month)
    if week is not None:
        queryset = queryset.filter(datez__ic_weeknum=week)
    if peak_season is not None:
        queryset = queryset.filter(datez__cf_peak_season=peak_season)
    if pool_name:
        queryset = queryset.filter(
            Q(site__pool__name__iexact=pool_name) | Q(site__pool__abbrev__iexact=pool_name)
        )
    if fisher_name:
        queryset = queryset.filter(
            Q(fisher__name__icontains=fisher_name)
            | Q(fisher__first_name__icontains=fisher_name)
            | Q(fisher__last_name__icontains=fisher_name)
            | Q(fisher__lookup__icontains=fisher_name)
        )
    if season:
        queryset = queryset.filter(datez__cf_season__iexact=season)

    distinct_sets = queryset.values('cf_date', 'fisher_id', 'site_id', 'set_num').annotate(
        set_gear_length=Coalesce(Max('gear_length'), Value(0), output_field=IntegerField())
    )
    total_gear_length = distinct_sets.aggregate(
        total=Coalesce(Sum('set_gear_length'), Value(0), output_field=IntegerField())
    )['total']

    payload = {
        'filters': {
            'year': year,
            'month': month,
            'week': week,
            'peak_season': peak_season,
            'pool': pool_name or None,
            'fisher': fisher_name or None,
            'season': season or None,
        },
        'stats': {
            'net_count': int(distinct_sets.count() or 0),
            'total_gear_length': int(total_gear_length or 0),
        },
    }
    return JsonResponse({'data': payload})


@login_required
def cf_effort_stats(request):
    """Return combined CF effort stats: fisher-day, fisher count, net count, and total gear length."""
    if not (request.user.has_perm('kiccd_app.view_cfcatch') or request.user.has_perm('kiccd_app.view_cfevent')):
        return JsonResponse({'detail': 'Permission denied.'}, status=403)

    def _parse_int(param):
        raw = request.GET.get(param)
        if raw in (None, ''):
            return None
        try:
            return int(raw)
        except ValueError:
            return None

    year = _parse_int('year')
    month = _parse_int('month')
    week = _parse_int('week')
    peak_season = _parse_int('peak_season')
    pool_name = (request.GET.get('pool') or '').strip()
    fisher_name = (request.GET.get('fisher') or '').strip()
    season = (request.GET.get('season') or '').strip()

    queryset = CfEvent.objects.filter(cfcatch__isnull=False)

    if year is not None:
        queryset = queryset.filter(datez__cal_year=year)
    if month is not None:
        queryset = queryset.filter(datez__ic_month1=month)
    if week is not None:
        queryset = queryset.filter(datez__ic_weeknum=week)
    if peak_season is not None:
        queryset = queryset.filter(datez__cf_peak_season=peak_season)
    if pool_name:
        queryset = queryset.filter(
            Q(site__pool__name__iexact=pool_name) | Q(site__pool__abbrev__iexact=pool_name)
        )
    if fisher_name:
        queryset = queryset.filter(
            Q(fisher__name__icontains=fisher_name)
            | Q(fisher__first_name__icontains=fisher_name)
            | Q(fisher__last_name__icontains=fisher_name)
            | Q(fisher__lookup__icontains=fisher_name)
        )
    if season:
        queryset = queryset.filter(datez__cf_season__iexact=season)

    fisher_day_count = queryset.values('cf_date', 'fisher_id').distinct().count()
    fisher_count = queryset.values('fisher_id').distinct().count()

    distinct_sets = queryset.values('cf_date', 'fisher_id', 'site_id', 'set_num').annotate(
        set_gear_length=Coalesce(Max('gear_length'), Value(0), output_field=IntegerField())
    )
    total_gear_length = distinct_sets.aggregate(
        total=Coalesce(Sum('set_gear_length'), Value(0), output_field=IntegerField())
    )['total']

    payload = {
        'filters': {
            'year': year,
            'month': month,
            'week': week,
            'peak_season': peak_season,
            'pool': pool_name or None,
            'fisher': fisher_name or None,
            'season': season or None,
        },
        'stats': {
            'fisher_day_count': int(fisher_day_count or 0),
            'fisher_count': int(fisher_count or 0),
            'net_count': int(distinct_sets.count() or 0),
            'total_gear_length': int(total_gear_length or 0),
        },
    }
    return JsonResponse({'data': payload})


@login_required
def cf_harvest_stats(request):
    """Return contract fishing harvest statistics with optional filters."""
    if not request.user.has_perm('kiccd_app.view_cfcatch'):
        return JsonResponse({'detail': 'Permission denied.'}, status=403)

    def _parse_int(param):
        raw = request.GET.get(param)
        if raw in (None, ''):
            return None
        try:
            return int(raw)
        except ValueError:
            return None

    species_param = request.GET.get('species')
    species_lookup = species_param.strip() if species_param else None
    pool_name = (request.GET.get('pool') or '').strip()
    fisher_name = (request.GET.get('fisher') or '').strip()
    year = _parse_int('year')
    month = _parse_int('month')
    week = _parse_int('week')
    peak_season = _parse_int('peak_season')
    season = (request.GET.get('season') or '').strip()

    queryset = CfCatch.objects.filter(species__targeted=True)

    species_obj = None
    if species_lookup:
        species_obj = FishSpecies.objects.filter(name__iexact=species_lookup, targeted=True).first()
        if not species_obj:
            species_obj = FishSpecies.objects.filter(lookup__iexact=species_lookup, targeted=True).first()
        if not species_obj:
            return JsonResponse({'detail': f'Species "{species_lookup}" not found.'}, status=404)
        queryset = queryset.filter(species=species_obj)

    if year is not None:
        queryset = queryset.filter(event__datez__cal_year=year)
    if month is not None:
        queryset = queryset.filter(event__datez__ic_month1=month)
    if week is not None:
        queryset = queryset.filter(event__datez__ic_weeknum=week)
    if peak_season is not None:
        queryset = queryset.filter(event__datez__cf_peak_season=peak_season)
    if pool_name:
        queryset = queryset.filter(
            Q(event__site__pool__name__iexact=pool_name) | Q(event__site__pool__abbrev__iexact=pool_name)
        )
    if fisher_name:
        queryset = queryset.filter(
            Q(event__fisher__name__icontains=fisher_name)
            | Q(event__fisher__first_name__icontains=fisher_name)
            | Q(event__fisher__last_name__icontains=fisher_name)
            | Q(event__fisher__lookup__icontains=fisher_name)
        )
    if season:
        queryset = queryset.filter(event__datez__cf_season__iexact=season)

    harvest_count_stats = queryset.aggregate(
        total=Coalesce(Sum('total_cnt'), Value(0), output_field=IntegerField()),
        row_count=Coalesce(Count('pk'), Value(0), output_field=IntegerField()),
        sum_x2=Coalesce(
            Sum(ExpressionWrapper(F('total_cnt') * F('total_cnt'), output_field=DecimalField())),
            Value(0, output_field=DecimalField()),
        ),
    )
    harvest_count = harvest_count_stats['total']
    harvest_count_std_dev = None
    harvest_count_std_err = None
    if harvest_count_stats['row_count']:
        mean_count = Decimal(harvest_count_stats['total']) / Decimal(harvest_count_stats['row_count'])
        variance_count = (harvest_count_stats['sum_x2'] / Decimal(harvest_count_stats['row_count'])) - (mean_count * mean_count)
        variance_count = max(variance_count, Decimal('0'))
        harvest_count_std_dev = Decimal(str(sqrt(float(variance_count))))
        harvest_count_std_err = harvest_count_std_dev / Decimal(str(sqrt(float(harvest_count_stats['row_count']))))

    length_stats = queryset.filter(mean_length_mm__isnull=False).aggregate(
        weighted_sum=Coalesce(
            Sum(ExpressionWrapper(F('mean_length_mm') * F('total_cnt'), output_field=DecimalField())),
            Value(0, output_field=DecimalField()),
        ),
        weighted_sum_sq=Coalesce(
            Sum(ExpressionWrapper(F('mean_length_mm') * F('mean_length_mm') * F('total_cnt'), output_field=DecimalField())),
            Value(0, output_field=DecimalField()),
        ),
        weight=Coalesce(Sum('total_cnt'), Value(0), output_field=IntegerField()),
    )
    mean_length = None
    mean_length_std_dev = None
    mean_length_std_err = None
    if length_stats['weight']:
        mean_length = length_stats['weighted_sum'] / length_stats['weight']
        variance_length = (length_stats['weighted_sum_sq'] / length_stats['weight']) - (mean_length * mean_length)
        variance_length = max(variance_length, Decimal('0'))
        mean_length_std_dev = Decimal(str(sqrt(float(variance_length))))
        mean_length_std_err = mean_length_std_dev / Decimal(str(sqrt(float(length_stats['weight']))))

    weight_value_expr = Coalesce(
        F('mean_weight_g'),
        F('predicted_weight_g'),
        output_field=DecimalField(),
    )
    weight_stats = queryset.filter(
        Q(mean_weight_g__isnull=False) | Q(predicted_weight_g__isnull=False)
    ).aggregate(
        weighted_sum=Coalesce(
            Sum(ExpressionWrapper(weight_value_expr * F('total_cnt'), output_field=DecimalField())),
            Value(0, output_field=DecimalField()),
        ),
        weighted_sum_sq=Coalesce(
            Sum(ExpressionWrapper(weight_value_expr * weight_value_expr * F('total_cnt'), output_field=DecimalField())),
            Value(0, output_field=DecimalField()),
        ),
        weight=Coalesce(Sum('total_cnt'), Value(0), output_field=IntegerField()),
    )
    mean_weight = None
    mean_weight_std_dev = None
    mean_weight_std_err = None
    if weight_stats['weight']:
        mean_weight = weight_stats['weighted_sum'] / weight_stats['weight']
        variance_weight = (weight_stats['weighted_sum_sq'] / weight_stats['weight']) - (mean_weight * mean_weight)
        variance_weight = max(variance_weight, Decimal('0'))
        mean_weight_std_dev = Decimal(str(sqrt(float(variance_weight))))
        mean_weight_std_err = mean_weight_std_dev / Decimal(str(sqrt(float(weight_stats['weight']))))

    total_weight_expr = ExpressionWrapper(weight_value_expr * F('total_cnt'), output_field=DecimalField())
    total_weight_stats = queryset.aggregate(
        total=Coalesce(Sum(total_weight_expr), Value(0, output_field=DecimalField())),
        row_count=Coalesce(Count('pk'), Value(0), output_field=IntegerField()),
        sum_x2=Coalesce(
            Sum(ExpressionWrapper(total_weight_expr * total_weight_expr, output_field=DecimalField())),
            Value(0, output_field=DecimalField()),
        ),
    )
    total_weight = total_weight_stats['total']
    total_weight_std_dev = None
    total_weight_std_err = None
    if total_weight_stats['row_count']:
        mean_total_weight = total_weight / Decimal(total_weight_stats['row_count'])
        variance_total_weight = (total_weight_stats['sum_x2'] / Decimal(total_weight_stats['row_count'])) - (mean_total_weight * mean_total_weight)
        variance_total_weight = max(variance_total_weight, Decimal('0'))
        total_weight_std_dev = Decimal(str(sqrt(float(variance_total_weight))))
        total_weight_std_err = total_weight_std_dev / Decimal(str(sqrt(float(total_weight_stats['row_count']))))
    total_weight_kg = None
    total_weight_lbs = None
    total_weight_kg_std_dev = None
    total_weight_kg_std_err = None
    total_weight_lbs_std_dev = None
    total_weight_lbs_std_err = None
    if total_weight is not None:
        total_weight_kg = total_weight / Decimal('1000')
        total_weight_lbs = total_weight * Decimal('0.0022046226218')
    if total_weight_std_dev is not None:
        total_weight_kg_std_dev = total_weight_std_dev / Decimal('1000')
        total_weight_lbs_std_dev = total_weight_std_dev * Decimal('0.0022046226218')
    if total_weight_std_err is not None:
        total_weight_kg_std_err = total_weight_std_err / Decimal('1000')
        total_weight_lbs_std_err = total_weight_std_err * Decimal('0.0022046226218')

    def _serialize(value):
        return float(value) if isinstance(value, Decimal) else value

    payload = {
        'filters': {
            'species': species_obj.name if species_obj else species_lookup,
            'pool': pool_name or None,
            'fisher': fisher_name or None,
            'year': year,
            'month': month,
            'week': week,
            'peak_season': peak_season,
            'season': season or None,
        },
        'stats': {
            'harvest_count': int(harvest_count or 0),
            'harvest_count_std_dev': _serialize(harvest_count_std_dev),
            'harvest_count_std_err': _serialize(harvest_count_std_err),
            'mean_length_mm': _serialize(mean_length),
            'mean_length_mm_std_dev': _serialize(mean_length_std_dev),
            'mean_length_mm_std_err': _serialize(mean_length_std_err),
            'mean_weight_g': _serialize(mean_weight),
            'mean_weight_g_std_dev': _serialize(mean_weight_std_dev),
            'mean_weight_g_std_err': _serialize(mean_weight_std_err),
            'total_weight_g': _serialize(total_weight),
            'total_weight_g_std_dev': _serialize(total_weight_std_dev),
            'total_weight_g_std_err': _serialize(total_weight_std_err),
            'total_weight_kg': _serialize(total_weight_kg),
            'total_weight_kg_std_dev': _serialize(total_weight_kg_std_dev),
            'total_weight_kg_std_err': _serialize(total_weight_kg_std_err),
            'total_weight_lbs': _serialize(total_weight_lbs),
            'total_weight_lbs_std_dev': _serialize(total_weight_lbs_std_dev),
            'total_weight_lbs_std_err': _serialize(total_weight_lbs_std_err),
        },
    }
    return JsonResponse({'data': payload})


@login_required
def cf_filtered_results(request):
    """Render the contract fishing filtered results page."""
    if not request.user.has_perm('kiccd_app.view_cfcatch'):
        return render(request, 'kiccd_app/403.html', status=403)

    targeted_species = FishSpecies.objects.filter(targeted=True).order_by('-ranked', 'name')
    pools = Pool.objects.all().order_by('pool_id')
    fishers = Fisher.objects.filter(contracted=True).order_by('last_name', 'first_name')

    current_year = timezone.now().year
    years = list(
        Dates.objects.filter(cal_year__gte=2019, cal_year__lte=current_year)
        .values_list('cal_year', flat=True)
        .distinct()
        .order_by('-cal_year')
    )
    months = list(
        Dates.objects.values('ic_month1', 'ic_month2', 'ic_mon')
        .distinct()
        .order_by('ic_month1')
    )
    weeks = list(
        Dates.objects.values_list('ic_weeknum', flat=True).distinct().order_by('ic_weeknum')
    )
    peak_seasons = list(
        Dates.objects.filter(cal_year__gte=2019, cal_year__lte=current_year)
        .values_list('cf_peak_season', flat=True)
        .distinct()
        .order_by('-cf_peak_season')
    )
    seasons = ('Spring', 'Summer', 'Fall', 'Winter')

    context = {
        'targeted_species': targeted_species,
        'pool_options': pools,
        'year_options': years,
        'month_options': months,
        'week_options': weeks,
        'peak_season_options': peak_seasons,
        'season_options': seasons,
        'fisher_options': fishers,
    }
    return render(request, 'kiccd_app/pages/cf-results-filtered.html', context)


@login_required
def ichp_filtered_results(request):
    """Render the ICHP filtered results page."""
    if not (request.user.has_perm('kiccd_app.view_ichpcatch') or request.user.has_perm('kiccd_app.view_ichpevent')):
        return render(request, 'kiccd_app/403.html', status=403)

    basins = Basin.objects.filter(ichpevent__isnull=False, ichpevent__observed=False).distinct().order_by('abbrev', 'name')
    pools = Pool.objects.filter(fishingsite_hp__ichpevent__isnull=False, fishingsite_hp__ichpevent__observed=False).distinct().order_by('pool_id')
    sites = FishingSite_HP.objects.filter(ichpevent__isnull=False, ichpevent__observed=False).select_related('pool', 'basin').distinct().order_by('name')
    fishers = Fisher.objects.filter(ichpevent__isnull=False, ichpevent__observed=False).distinct().order_by('last_name', 'first_name')
    species_options = (
        FishSpecies.objects
        .filter(ichpcatch__isnull=False, ichpcatch__event__observed=False)
        .exclude(spp_id=0)
        .exclude(name__iexact='No Fish')
        .distinct()
        .order_by('-ranked', 'name')
    )

    years = list(
        Dates.objects.filter(ichpevent__isnull=False, ichpevent__observed=False)
        .values_list('cal_year', flat=True)
        .distinct()
        .order_by('-cal_year')
    )
    months = list(
        Dates.objects.filter(ichpevent__isnull=False, ichpevent__observed=False)
        .values('ic_month1', 'ic_mon')
        .distinct()
        .order_by('ic_month1')
    )
    seasons = list(
        Dates.objects.filter(ichpevent__isnull=False, ichpevent__observed=False)
        .values_list('ic_season', flat=True)
        .distinct()
        .order_by('ic_season')
    )

    context = {
        'basin_options': basins,
        'pool_options': pools,
        'site_options': sites,
        'year_options': years,
        'month_options': months,
        'season_options': seasons,
        'fisher_options': fishers,
        'species_options': species_options,
    }
    return render(request, 'kiccd_app/pages/ichp-results-filtered.html', context)


@login_required
def ic_filtered_view(request):
    """Render a filterable Agency Invasive Carp Sampling effort/catch results table."""
    if not (request.user.has_perm('kiccd_app.view_iccatch') or request.user.has_perm('kiccd_app.view_icevent')):
        return render(request, 'kiccd_app/403.html', status=403)

    # Restrict option lists to events that have at least one catch row.
    base_events = IcEvent.objects.filter(iccatch__isnull=False)

    years = list(
        Dates.objects.filter(icevent__iccatch__isnull=False)
        .values_list('cal_year', flat=True)
        .distinct()
        .order_by('-cal_year')
    )
    projects = Project.objects.filter(icevent__iccatch__isnull=False).distinct().order_by('project_id')
    agencies = Partner.objects.filter(icevent__iccatch__isnull=False).distinct().order_by('abbrev', 'name')
    basins = Basin.objects.filter(samplesite__icevent__iccatch__isnull=False).distinct().order_by('abbrev', 'name')
    pools = Pool.objects.filter(samplesite__icevent__iccatch__isnull=False).distinct().order_by('pool_id')
    sites = (
        SampleSite.objects.filter(icevent__iccatch__isnull=False)
        .select_related('pool', 'basin')
        .distinct()
        .order_by('name')
    )
    months = list(
        Dates.objects.filter(icevent__iccatch__isnull=False)
        .values('ic_month1', 'ic_mon')
        .distinct()
        .order_by('ic_month1')
    )
    seasons = list(
        Dates.objects.filter(icevent__iccatch__isnull=False)
        .values_list('ic_season', flat=True)
        .distinct()
        .order_by('ic_season')
    )

    def _parse_int(param):
        raw = (request.GET.get(param) or '').strip()
        if raw == '':
            return None
        try:
            return int(raw)
        except ValueError:
            return None

    selected_year = _parse_int('year')
    selected_project = _parse_int('project')
    selected_agency = _parse_int('agency')
    selected_basin = _parse_int('basin')
    selected_pool = _parse_int('pool')
    selected_site = _parse_int('site')
    selected_month = _parse_int('month')
    selected_season = (request.GET.get('season') or '').strip()

    catches = IcCatch.objects.none()
    filters_applied = request.GET.get('apply') == '1'

    if filters_applied:
        catches = IcCatch.objects.select_related(
            'event__project',
            'event__agency',
            'event__site',
            'event__site__basin',
            'event__site__pool',
            'event__gear',
            'event__datez',
            'species',
        ).filter(event__in=base_events)

        if selected_year is not None:
            catches = catches.filter(event__datez__cal_year=selected_year)
        if selected_project is not None:
            catches = catches.filter(event__project_id=selected_project)
        if selected_agency is not None:
            catches = catches.filter(event__agency_id=selected_agency)
        if selected_basin is not None:
            catches = catches.filter(event__site__basin_id=selected_basin)
        if selected_pool is not None:
            catches = catches.filter(event__site__pool_id=selected_pool)
        if selected_site is not None:
            catches = catches.filter(event__site_id=selected_site)
        if selected_month is not None:
            catches = catches.filter(event__datez__ic_month1=selected_month)
        if selected_season:
            catches = catches.filter(event__datez__ic_season__iexact=selected_season)

        catches = catches.order_by('-event__event_date', 'event__effort_num', 'species__name')

    context = {
        'year_options': years,
        'project_options': projects,
        'agency_options': agencies,
        'basin_options': basins,
        'pool_options': pools,
        'site_options': sites,
        'month_options': months,
        'season_options': seasons,
        'selected_year': selected_year,
        'selected_project': selected_project,
        'selected_agency': selected_agency,
        'selected_basin': selected_basin,
        'selected_pool': selected_pool,
        'selected_site': selected_site,
        'selected_month': selected_month,
        'selected_season': selected_season,
        'filters_applied': filters_applied,
        'catches': catches,
    }
    return render(request, 'kiccd_app/pages/ic-filtered.html', context)


@login_required
def subsample_filtered_view(request):
    """Render a filterable Subsample length/weight results table."""
    if not request.user.has_perm('kiccd_app.view_subsample'):
        return render(request, 'kiccd_app/403.html', status=403)

    base_qs = Subsample.objects.select_related(
        'datez',
        'fisher',
        'basin',
        'pool',
        'spp',
        'sex',
        'observer',
    )

    years = list(
        Dates.objects.filter(subsample__isnull=False)
        .values_list('cal_year', flat=True)
        .distinct()
        .order_by('-cal_year')
    )
    seasons = list(
        Dates.objects.filter(subsample__isnull=False)
        .exclude(cf_season__isnull=True)
        .exclude(cf_season='')
        .values_list('cf_season', flat=True)
        .distinct()
        .order_by('cf_season')
    )
    months = list(
        Dates.objects.filter(subsample__isnull=False)
        .values('ic_month1', 'ic_mon')
        .distinct()
        .order_by('ic_month1')
    )
    basins = Basin.objects.filter(subsample__isnull=False).distinct().order_by('name')
    pools = Pool.objects.filter(subsample__isnull=False).distinct().order_by('pool_id')
    species = FishSpecies.objects.filter(subsample__isnull=False).distinct().order_by('-ranked', 'name')
    sexes = FishSex.objects.filter(subsample__isnull=False).distinct().order_by('sx_id')
    fishers = Fisher.objects.filter(subsample__isnull=False).distinct().order_by('last_name', 'first_name')

    def _parse_int(param):
        raw = (request.GET.get(param) or '').strip()
        if raw == '':
            return None
        try:
            return int(raw)
        except ValueError:
            return None

    selected_year = _parse_int('year')
    selected_month = _parse_int('month')
    selected_basin = _parse_int('basin')
    selected_pool = _parse_int('pool')
    selected_species = _parse_int('species')
    selected_sex = _parse_int('sex')
    selected_fisher = _parse_int('fisher')
    selected_season = (request.GET.get('season') or '').strip()

    subsamples = Subsample.objects.none()
    filters_applied = request.GET.get('apply') == '1'

    if filters_applied:
        subsamples = base_qs

        if selected_year is not None:
            subsamples = subsamples.filter(datez__cal_year=selected_year)
        if selected_season:
            subsamples = subsamples.filter(datez__cf_season__iexact=selected_season)
        if selected_month is not None:
            subsamples = subsamples.filter(datez__ic_month1=selected_month)
        if selected_basin is not None:
            subsamples = subsamples.filter(basin_id=selected_basin)
        if selected_pool is not None:
            subsamples = subsamples.filter(pool_id=selected_pool)
        if selected_species is not None:
            subsamples = subsamples.filter(spp_id=selected_species)
        if selected_sex is not None:
            subsamples = subsamples.filter(sex_id=selected_sex)
        if selected_fisher is not None:
            subsamples = subsamples.filter(fisher_id=selected_fisher)

        subsamples = subsamples.order_by('-cf_date', 'fisher__last_name', 'fisher__first_name', 'spp__name')
        subsamples = list(subsamples)

        for sub in subsamples:
            sub.length_in = None
            sub.weight_kg = None
            sub.weight_lb = None

            if sub.length_mm is not None:
                length_in = (Decimal(sub.length_mm) / Decimal('25.4')).quantize(Decimal('0.01'))
                sub.length_in = f"{length_in:.2f}"

            if sub.weight_g is not None:
                weight_kg = (Decimal(sub.weight_g) / Decimal('1000')).quantize(Decimal('0.01'))
                weight_lb = (Decimal(sub.weight_g) / Decimal('453.59237')).quantize(Decimal('0.01'))
                sub.weight_kg = f"{weight_kg:.2f}"
                sub.weight_lb = f"{weight_lb:.2f}"

    context = {
        'year_options': years,
        'season_options': seasons,
        'month_options': months,
        'basin_options': basins,
        'pool_options': pools,
        'species_options': species,
        'sex_options': sexes,
        'fisher_options': fishers,
        'selected_year': selected_year,
        'selected_season': selected_season,
        'selected_month': selected_month,
        'selected_basin': selected_basin,
        'selected_pool': selected_pool,
        'selected_species': selected_species,
        'selected_sex': selected_sex,
        'selected_fisher': selected_fisher,
        'filters_applied': filters_applied,
        'subsamples': subsamples,
    }
    return render(request, 'kiccd_app/pages/subsample-filtered.html', context)


@login_required
def ichp_report_filtered_view(request):
    """Render a filterable ICHP effort/catch table for reports."""
    if not (request.user.has_perm('kiccd_app.view_ichpcatch') or request.user.has_perm('kiccd_app.view_ichpevent')):
        return render(request, 'kiccd_app/403.html', status=403)

    def _parse_int(param):
        raw = (request.GET.get(param) or '').strip()
        if raw == '':
            return None
        try:
            return int(raw)
        except ValueError:
            return None

    selected_year = _parse_int('year')
    selected_month = _parse_int('month')
    selected_basin = _parse_int('basin')
    selected_species = _parse_int('species')
    selected_fisher = _parse_int('fisher')
    selected_season = (request.GET.get('season') or '').strip()
    selected_observed = (request.GET.get('observed') or '').strip()

    if selected_observed == 'only':
        observed_q = {'event__observed': True}
        event_observed_q = {'ichpevent__observed': True}
        catch_event_observed_q = {'ichpcatch__event__observed': True}
    elif selected_observed == 'all':
        observed_q = {}
        event_observed_q = {}
        catch_event_observed_q = {}
    else:
        selected_observed = 'exclude'
        observed_q = {'event__observed': False}
        event_observed_q = {'ichpevent__observed': False}
        catch_event_observed_q = {'ichpcatch__event__observed': False}

    base_catches = IchpCatch.objects.select_related(
        'event',
        'event__datez',
        'event__fisher',
        'event__basin',
        'event__site',
        'event__gear',
        'species',
    ).filter(**observed_q)

    years = list(
        Dates.objects.filter(ichpevent__ichpcatch__isnull=False, **event_observed_q)
        .values_list('cal_year', flat=True)
        .distinct()
        .order_by('-cal_year')
    )
    months = list(
        Dates.objects.filter(ichpevent__ichpcatch__isnull=False, **event_observed_q)
        .values('ic_month1', 'ic_mon')
        .distinct()
        .order_by('ic_month1')
    )
    seasons = list(
        Dates.objects.filter(ichpevent__ichpcatch__isnull=False, **event_observed_q)
        .values_list('ic_season', flat=True)
        .distinct()
        .order_by('ic_season')
    )
    basins = Basin.objects.filter(ichpevent__ichpcatch__isnull=False, **event_observed_q).distinct().order_by('abbrev', 'name')
    species_options = (
        FishSpecies.objects
        .filter(**catch_event_observed_q)
        .exclude(spp_id=0)
        .exclude(name__iexact='No Fish')
        .distinct()
        .order_by('-ranked', 'name')
    )
    fishers = Fisher.objects.filter(ichpevent__ichpcatch__isnull=False, **event_observed_q).distinct().order_by('last_name', 'first_name')

    catches = IchpCatch.objects.none()
    filters_applied = request.GET.get('apply') == '1'

    if filters_applied:
        catches = base_catches

        if selected_year is not None:
            catches = catches.filter(event__datez__cal_year=selected_year)
        if selected_month is not None:
            catches = catches.filter(event__datez__ic_month1=selected_month)
        if selected_season:
            catches = catches.filter(event__datez__ic_season__iexact=selected_season)
        if selected_basin is not None:
            catches = catches.filter(event__basin_id=selected_basin)
        if selected_species is not None:
            catches = catches.filter(species_id=selected_species)
        if selected_fisher is not None:
            catches = catches.filter(event__fisher_id=selected_fisher)

        catches = catches.order_by('-event__ichp_date', 'event__fisher__last_name', 'event__net_haul', 'species__name')

    context = {
        'year_options': years,
        'month_options': months,
        'season_options': seasons,
        'basin_options': basins,
        'species_options': species_options,
        'fisher_options': fishers,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_season': selected_season,
        'selected_basin': selected_basin,
        'selected_species': selected_species,
        'selected_fisher': selected_fisher,
        'selected_observed': selected_observed,
        'filters_applied': filters_applied,
        'catches': catches,
    }
    return render(request, 'kiccd_app/pages/ichp-report-filtered.html', context)


@login_required
def cf_report_filtered_view(request):
    """Render a filterable CF effort/catch table for reports."""
    if not (request.user.has_perm('kiccd_app.view_cfcatch') or request.user.has_perm('kiccd_app.view_cfevent')):
        return render(request, 'kiccd_app/403.html', status=403)

    base_catches = CfCatch.objects.select_related(
        'event',
        'event__datez',
        'event__fisher',
        'event__observer',
        'event__site',
        'event__site__basin',
        'event__site__pool',
        'event__gear',
        'species',
    )

    years = list(
        Dates.objects.filter(cfevent__cfcatch__isnull=False)
        .values_list('cal_year', flat=True)
        .distinct()
        .order_by('-cal_year')
    )
    months = list(
        Dates.objects.filter(cfevent__cfcatch__isnull=False)
        .values('ic_month1', 'ic_mon')
        .distinct()
        .order_by('ic_month1')
    )
    seasons = list(
        Dates.objects.filter(cfevent__cfcatch__isnull=False)
        .exclude(cf_season__isnull=True)
        .exclude(cf_season='')
        .values_list('cf_season', flat=True)
        .distinct()
        .order_by('cf_season')
    )
    basins = Basin.objects.filter(fishingsite_cf__cfevent__cfcatch__isnull=False).distinct().order_by('abbrev', 'name')
    pools = Pool.objects.filter(fishingsite_cf__cfevent__cfcatch__isnull=False).distinct().order_by('pool_id')
    sites = (
        FishingSite_CF.objects
        .filter(cfevent__cfcatch__isnull=False)
        .select_related('pool', 'basin')
        .distinct()
        .order_by('name')
    )
    gears = Gear.objects.filter(cfevent__cfcatch__isnull=False).distinct().order_by('name')
    fishers = Fisher.objects.filter(cfevent__cfcatch__isnull=False).distinct().order_by('last_name', 'first_name')

    def _parse_int(param):
        raw = (request.GET.get(param) or '').strip()
        if raw == '':
            return None
        try:
            return int(raw)
        except ValueError:
            return None

    selected_year = _parse_int('year')
    selected_month = _parse_int('month')
    selected_basin = _parse_int('basin')
    selected_pool = _parse_int('pool')
    selected_site = _parse_int('site')
    selected_gear = _parse_int('gear')
    selected_fisher = _parse_int('fisher')
    selected_season = (request.GET.get('season') or '').strip()

    catches = CfCatch.objects.none()
    filters_applied = request.GET.get('apply') == '1'

    if filters_applied:
        catches = base_catches

        if selected_year is not None:
            catches = catches.filter(event__datez__cal_year=selected_year)
        if selected_month is not None:
            catches = catches.filter(event__datez__ic_month1=selected_month)
        if selected_season:
            catches = catches.filter(event__datez__cf_season__iexact=selected_season)
        if selected_basin is not None:
            catches = catches.filter(event__site__basin_id=selected_basin)
        if selected_pool is not None:
            catches = catches.filter(event__site__pool_id=selected_pool)
        if selected_site is not None:
            catches = catches.filter(event__site_id=selected_site)
        if selected_gear is not None:
            catches = catches.filter(event__gear_id=selected_gear)
        if selected_fisher is not None:
            catches = catches.filter(event__fisher_id=selected_fisher)

        catches = catches.order_by('-event__cf_date', 'event__fisher__last_name', 'event__set_num', 'species__name')
        catches = list(catches)

        for catch in catches:
            catch.gear_spec = None
            catch.total_weight_kg = None

            if (
                catch.event.gear_length is not None
                and catch.event.gear_depth is not None
                and catch.event.mesh_size is not None
            ):
                mesh_size = Decimal(catch.event.mesh_size).quantize(Decimal('0.01'))
                catch.gear_spec = f"{catch.event.gear_length} x {catch.event.gear_depth} x {mesh_size:.2f}"

            if catch.total_cnt is None:
                continue

            mean_weight_source_g = catch.mean_weight_g if catch.mean_weight_g is not None else catch.predicted_weight_g
            if mean_weight_source_g is None:
                continue

            total_weight_g = Decimal(catch.total_cnt) * Decimal(mean_weight_source_g)
            total_weight_kg = (total_weight_g / Decimal('1000')).quantize(Decimal('0.01'))
            if total_weight_kg == Decimal('0.00'):
                continue
            catch.total_weight_kg = f"{total_weight_kg:.2f}"

    context = {
        'year_options': years,
        'month_options': months,
        'season_options': seasons,
        'basin_options': basins,
        'pool_options': pools,
        'site_options': sites,
        'gear_options': gears,
        'fisher_options': fishers,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_season': selected_season,
        'selected_basin': selected_basin,
        'selected_pool': selected_pool,
        'selected_site': selected_site,
        'selected_gear': selected_gear,
        'selected_fisher': selected_fisher,
        'filters_applied': filters_applied,
        'catches': catches,
    }
    return render(request, 'kiccd_app/pages/cf-report-filtered.html', context)

 
@login_required
def ra_report_filtered_view(request):
    """Render a filterable ICHP Ride-Along effort/catch table for reports."""
    if not (request.user.has_perm('kiccd_app.view_racatch') or request.user.has_perm('kiccd_app.view_raevent')):
        return render(request, 'kiccd_app/403.html', status=403)

    base_catches = RaCatch.objects.select_related(
        'event',
        'event__datez',
        'event__fisher',
        'event__observer',
        'event__site',
        'event__site__basin',
        'event__site__pool',
        'event__gear',
        'species',
    )

    years = list(
        Dates.objects.filter(raevent__racatch__isnull=False)
        .values_list('cal_year', flat=True)
        .distinct()
        .order_by('-cal_year')
    )
    months = list(
        Dates.objects.filter(raevent__racatch__isnull=False)
        .values('ic_month1', 'ic_mon')
        .distinct()
        .order_by('ic_month1')
    )
    seasons = list(
        Dates.objects.filter(raevent__racatch__isnull=False)
        .exclude(ic_season__isnull=True)
        .exclude(ic_season='')
        .values_list('ic_season', flat=True)
        .distinct()
        .order_by('ic_season')
    )
    basins = Basin.objects.filter(fishingsite_hp__raevent__racatch__isnull=False).distinct().order_by('abbrev', 'name')
    sites = (
        FishingSite_HP.objects
        .filter(raevent__racatch__isnull=False)
        .select_related('pool', 'basin')
        .distinct()
        .order_by('name')
    )
    fishers = Fisher.objects.filter(raevent__racatch__isnull=False).distinct().order_by('last_name', 'first_name')
    species_options = (
        FishSpecies.objects
        .filter(racatch__isnull=False)
        .exclude(spp_id=0)
        .exclude(name__iexact='No Fish')
        .distinct()
        .order_by('-ranked', 'name')
    )

    def _parse_int(param):
        raw = (request.GET.get(param) or '').strip()
        if raw == '':
            return None
        try:
            return int(raw)
        except ValueError:
            return None

    selected_year = _parse_int('year')
    selected_month = _parse_int('month')
    selected_basin = _parse_int('basin')
    selected_site = _parse_int('site')
    selected_fisher = _parse_int('fisher')
    selected_species = _parse_int('species')
    selected_season = (request.GET.get('season') or '').strip()

    catches = RaCatch.objects.none()
    filters_applied = request.GET.get('apply') == '1'

    if filters_applied:
        catches = base_catches

        if selected_year is not None:
            catches = catches.filter(event__datez__cal_year=selected_year)
        if selected_month is not None:
            catches = catches.filter(event__datez__ic_month1=selected_month)
        if selected_season:
            catches = catches.filter(event__datez__ic_season__iexact=selected_season)
        if selected_basin is not None:
            catches = catches.filter(event__site__basin_id=selected_basin)
        if selected_site is not None:
            catches = catches.filter(event__site_id=selected_site)
        if selected_fisher is not None:
            catches = catches.filter(event__fisher_id=selected_fisher)
        if selected_species is not None:
            catches = catches.filter(species_id=selected_species)

        catches = catches.order_by('-event__ra_date', 'event__fisher__last_name', 'event__net_set', 'event__net_num', 'species__name')
        catches = list(catches)

        for catch in catches:
            catch.gear_spec = None
            catch.total_weight_kg = None
            if (
                catch.event.gear_length is not None
                and catch.event.gear_depth is not None
                and catch.event.mesh_size is not None
            ):
                mesh_size = Decimal(catch.event.mesh_size).quantize(Decimal('0.01'))
                catch.gear_spec = f"{catch.event.gear_length} x {catch.event.gear_depth} x {mesh_size:.2f}"

            if catch.total_cnt is None:
                continue

            mean_weight_source_g = catch.mean_weight_g if catch.mean_weight_g is not None else catch.predicted_weight_g
            if mean_weight_source_g is None:
                continue

            total_weight_g = Decimal(catch.total_cnt) * Decimal(mean_weight_source_g)
            total_weight_kg = (total_weight_g / Decimal('1000')).quantize(Decimal('0.01'))
            if total_weight_kg == Decimal('0.00'):
                continue
            catch.total_weight_kg = f"{total_weight_kg:.2f}"

    context = {
        'year_options': years,
        'month_options': months,
        'season_options': seasons,
        'basin_options': basins,
        'site_options': sites,
        'fisher_options': fishers,
        'species_options': species_options,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_season': selected_season,
        'selected_basin': selected_basin,
        'selected_site': selected_site,
        'selected_fisher': selected_fisher,
        'selected_species': selected_species,
        'filters_applied': filters_applied,
        'catches': catches,
    }
    return render(request, 'kiccd_app/pages/ra-report-filtered.html', context)


@login_required
def ichp_effort_stats(request):
    """Return combined ICHP effort stats with optional filters."""
    if not (request.user.has_perm('kiccd_app.view_ichpcatch') or request.user.has_perm('kiccd_app.view_ichpevent')):
        return JsonResponse({'detail': 'Permission denied.'}, status=403)

    def _parse_int(param):
        raw = request.GET.get(param)
        if raw in (None, ''):
            return None
        try:
            return int(raw)
        except ValueError:
            return None

    year = _parse_int('year')
    basin_id = _parse_int('basin')
    pool_id = _parse_int('pool')
    site_id = _parse_int('site')
    month = _parse_int('month')
    fisher_id = _parse_int('fisher')
    season = (request.GET.get('season') or '').strip()
    observed_filter = (request.GET.get('observed') or '').strip()

    queryset = IchpEvent.objects.all()
    if observed_filter == 'only':
        queryset = queryset.filter(observed=True)
    elif observed_filter == 'all':
        pass
    else:
        queryset = queryset.filter(observed=False)

    if year is not None:
        queryset = queryset.filter(datez__cal_year=year)
    if basin_id is not None:
        queryset = queryset.filter(basin_id=basin_id)
    if pool_id is not None:
        queryset = queryset.filter(site__pool_id=pool_id)
    if site_id is not None:
        queryset = queryset.filter(site_id=site_id)
    if month is not None:
        queryset = queryset.filter(datez__ic_month1=month)
    if season:
        queryset = queryset.filter(datez__ic_season__iexact=season)
    if fisher_id is not None:
        queryset = queryset.filter(fisher_id=fisher_id)

    fisher_day_count = queryset.values('ichp_date', 'fisher_id').distinct().count()
    fisher_count = queryset.values('fisher_id').distinct().count()
    total_net_count = queryset.values('event_id').count()
    total_net_length = queryset.aggregate(
        total=Coalesce(Sum('gear_length'), Value(0), output_field=IntegerField())
    )['total']

    payload = {
        'filters': {
            'year': year,
            'basin': basin_id,
            'pool': pool_id,
            'site': site_id,
            'month': month,
            'season': season or None,
            'fisher': fisher_id,
        },
        'stats': {
            'fisher_count': int(fisher_count or 0),
            'fisher_day_count': int(fisher_day_count or 0),
            'net_count': int(total_net_count or 0),
            'total_net_length': int(total_net_length or 0),
        },
    }
    return JsonResponse({'data': payload})


@login_required
def ichp_harvest_stats(request):
    """Return ICHP harvest statistics with optional filters and species selection."""
    if not request.user.has_perm('kiccd_app.view_ichpcatch'):
        return JsonResponse({'detail': 'Permission denied.'}, status=403)

    def _parse_int(param):
        raw = request.GET.get(param)
        if raw in (None, ''):
            return None
        try:
            return int(raw)
        except ValueError:
            return None

    year = _parse_int('year')
    basin_id = _parse_int('basin')
    pool_id = _parse_int('pool')
    site_id = _parse_int('site')
    month = _parse_int('month')
    fisher_id = _parse_int('fisher')
    season = (request.GET.get('season') or '').strip()
    species_id = _parse_int('species')
    targeted_only = (request.GET.get('targeted_only') or '').strip() in ('1', 'true', 'True', 'yes')
    observed_filter = (request.GET.get('observed') or '').strip()

    queryset = IchpCatch.objects.all()
    if observed_filter == 'only':
        queryset = queryset.filter(event__observed=True)
    elif observed_filter == 'all':
        pass
    else:
        queryset = queryset.filter(event__observed=False)

    if year is not None:
        queryset = queryset.filter(event__datez__cal_year=year)
    if basin_id is not None:
        queryset = queryset.filter(event__basin_id=basin_id)
    if pool_id is not None:
        queryset = queryset.filter(event__site__pool_id=pool_id)
    if site_id is not None:
        queryset = queryset.filter(event__site_id=site_id)
    if month is not None:
        queryset = queryset.filter(event__datez__ic_month1=month)
    if season:
        queryset = queryset.filter(event__datez__ic_season__iexact=season)
    if fisher_id is not None:
        queryset = queryset.filter(event__fisher_id=fisher_id)
    if targeted_only:
        queryset = queryset.filter(species__targeted=True)

    species_obj = None
    if species_id is not None:
        species_obj = FishSpecies.objects.filter(pk=species_id).first()
        if not species_obj:
            return JsonResponse({'detail': f'Species id "{species_id}" not found.'}, status=404)
        queryset = queryset.filter(species_id=species_id)

    totals = queryset.aggregate(
        total_harvest=Coalesce(Sum('harvest_cnt'), Value(0), output_field=IntegerField()),
        total_rel_healthy=Coalesce(Sum('rel_healthy_cnt'), Value(0), output_field=IntegerField()),
        total_rel_moribund=Coalesce(Sum('rel_moribund_cnt'), Value(0), output_field=IntegerField()),
        total_weight_lb=Coalesce(Sum('reported_weight_lb'), Value(0, output_field=DecimalField())),
    )
    total_weight_lb = totals['total_weight_lb'] or Decimal('0')
    total_weight_kg = total_weight_lb * Decimal('0.45359237')

    def _serialize(value):
        return float(value) if isinstance(value, Decimal) else value

    payload = {
        'filters': {
            'year': year,
            'basin': basin_id,
            'pool': pool_id,
            'site': site_id,
            'month': month,
            'season': season or None,
            'fisher': fisher_id,
            'species': species_obj.name if species_obj else None,
            'targeted_only': targeted_only,
        },
        'stats': {
            'harvest_count': int(totals['total_harvest'] or 0),
            'rel_healthy_count': int(totals['total_rel_healthy'] or 0),
            'rel_moribund_count': int(totals['total_rel_moribund'] or 0),
            'total_weight_lb': _serialize(total_weight_lb),
            'total_weight_kg': _serialize(total_weight_kg),
        },
    }
    return JsonResponse({'data': payload})


@login_required
def ic_age_growth_length_at_age(request):
    """Render filterable Length-at-Age summary results for IcAgeGrowth data."""
    if not request.user.has_perm('kiccd_app.view_icagegrowth'):
        return render(request, 'kiccd_app/403.html', status=403)

    base_qs = IcAgeGrowth.objects.select_related('agency', 'basin', 'pool', 'site__trib', 'spp', 'sex', 'datez')

    year_options = (
        base_qs.exclude(datez__cal_year__isnull=True)
        .values_list('datez__cal_year', flat=True)
        .distinct()
        .order_by('-datez__cal_year')
    )
    agency_options = Partner.objects.filter(icagegrowth__isnull=False).distinct().order_by('abbrev', 'name')
    basin_options = Basin.objects.filter(icagegrowth__isnull=False).distinct().order_by('abbrev', 'name')
    pool_options = Pool.objects.filter(icagegrowth__isnull=False).distinct().order_by('pool_id')
    trib_options = Trib.objects.filter(samplesite__icagegrowth__isnull=False).distinct().order_by('name')
    site_options = SampleSite.objects.filter(icagegrowth__isnull=False).select_related('pool').distinct().order_by('name')
    species_options = FishSpecies.objects.filter(icagegrowth__isnull=False).distinct().order_by('-ranked', 'name')
    sex_options = FishSex.objects.filter(icagegrowth__isnull=False).distinct().order_by('sx_id')

    selected_year = (request.GET.get('year') or '').strip()
    selected_agency = (request.GET.get('agency') or '').strip()
    selected_basin = (request.GET.get('basin') or '').strip()
    selected_pool = (request.GET.get('pool') or '').strip()
    selected_trib = (request.GET.get('trib') or '').strip()
    selected_site = (request.GET.get('site') or '').strip()
    selected_species = (request.GET.get('species') or '').strip()
    selected_sex = (request.GET.get('sex') or '').strip()

    filtered_qs = base_qs

    if selected_year:
        filtered_qs = filtered_qs.filter(datez__cal_year=selected_year)
    if selected_agency:
        filtered_qs = filtered_qs.filter(agency_id=selected_agency)
    if selected_basin:
        filtered_qs = filtered_qs.filter(basin_id=selected_basin)
    if selected_pool:
        filtered_qs = filtered_qs.filter(pool_id=selected_pool)
    if selected_trib:
        filtered_qs = filtered_qs.filter(site__trib_id=selected_trib)
    if selected_site:
        filtered_qs = filtered_qs.filter(site_id=selected_site)
    if selected_species:
        filtered_qs = filtered_qs.filter(spp_id=selected_species)
    if selected_sex:
        filtered_qs = filtered_qs.filter(sex_id=selected_sex)

    filters_applied = request.GET.get('apply') == '1'
    results = []
    total_filtered_records = 0

    if filters_applied:
        analysis_qs = filtered_qs.filter(ic_age__gte=1, ic_age__lte=25)
        total_filtered_records = analysis_qs.count()

        grouped_rows = (
            analysis_qs.values('ic_age')
            .annotate(
                fish_count=Coalesce(Count('pk'), Value(0), output_field=IntegerField()),
                length_count=Coalesce(Count('length_mm'), Value(0), output_field=IntegerField()),
                mean_length_mm=Avg('length_mm'),
                max_length_mm=Max('length_mm'),
                min_length_mm=Min('length_mm'),
                sum_length_sq=Coalesce(
                    Sum(
                        ExpressionWrapper(
                            F('length_mm') * F('length_mm'),
                            output_field=DecimalField(max_digits=24, decimal_places=4),
                        )
                    ),
                    Value(0, output_field=DecimalField(max_digits=24, decimal_places=4)),
                ),
                mean_weight_g=Avg('weight_g'),
            )
            .order_by('ic_age')
        )

        grouped_by_age = {row['ic_age']: row for row in grouped_rows}

        for age in range(1, 26):
            row = grouped_by_age.get(age, {})
            fish_count = int(row.get('fish_count') or 0)
            length_count = int(row.get('length_count') or 0)
            mean_length = row.get('mean_length_mm')
            sum_length_sq = row.get('sum_length_sq')

            std_dev_length_mm = None
            std_err_length_mm = None

            if length_count > 0 and mean_length is not None and sum_length_sq is not None:
                variance = (float(sum_length_sq) / float(length_count)) - (float(mean_length) ** 2)
                variance = max(variance, 0.0)
                std_dev_length_mm = sqrt(variance)
                std_err_length_mm = std_dev_length_mm / sqrt(float(length_count)) if length_count > 0 else None

            mean_weight_g = row.get('mean_weight_g')
            mean_weight_kg = (float(mean_weight_g) / 1000.0) if mean_weight_g is not None else None
            mean_weight_lb = (float(mean_weight_g) * 0.0022046226218) if mean_weight_g is not None else None

            results.append({
                'age': age,
                'count': fish_count,
                'age_frequency': ((fish_count / total_filtered_records) * 100.0) if total_filtered_records else None,
                'mean_length_mm': mean_length,
                'max_length_mm': row.get('max_length_mm'),
                'min_length_mm': row.get('min_length_mm'),
                'std_dev_length_mm': std_dev_length_mm,
                'std_err_length_mm': std_err_length_mm,
                'mean_weight_kg': mean_weight_kg,
                'mean_weight_lb': mean_weight_lb,
            })

    context = {
        'year_options': year_options,
        'agency_options': agency_options,
        'basin_options': basin_options,
        'pool_options': pool_options,
        'trib_options': trib_options,
        'site_options': site_options,
        'species_options': species_options,
        'sex_options': sex_options,
        'selected_year': selected_year,
        'selected_agency': selected_agency,
        'selected_basin': selected_basin,
        'selected_pool': selected_pool,
        'selected_trib': selected_trib,
        'selected_site': selected_site,
        'selected_species': selected_species,
        'selected_sex': selected_sex,
        'filters_applied': filters_applied,
        'results': results,
        'total_filtered_records': total_filtered_records,
    }

    return render(request, 'kiccd_app/pages/ic-age-growth-filtered.html', context)


@login_required
def cf_charted_results(request):
    """Render targeted CF harvest totals by month (Oct-May) grouped by season year."""
    if not request.user.has_perm('kiccd_app.view_cfcatch'):
        return render(request, 'kiccd_app/403.html', status=403)

    month_sequence = [10, 11, 12, 1, 2, 3, 4, 5, 6]
    month_labels = {
        10: 'Oct',
        11: 'Nov',
        12: 'Dec',
        1: 'Jan',
        2: 'Feb',
        3: 'Mar',
        4: 'Apr',
        5: 'May',
        6: 'Jun',
    }

    season_year_expr = Case(
        When(event__datez__ic_month1__gte=10, then=F('event__datez__cal_year')),
        default=ExpressionWrapper(F('event__datez__cal_year') - Value(1), output_field=IntegerField()),
        output_field=IntegerField(),
    )

    rows = (
        CfCatch.objects.filter(species__targeted=True, event__datez__ic_month1__in=month_sequence)
        .annotate(season_year=season_year_expr, month=F('event__datez__ic_month1'))
        .values('season_year', 'month')
        .annotate(
            total=Coalesce(Sum('total_cnt'), Value(0), output_field=IntegerField()),
            row_count=Coalesce(Count('pk'), Value(0), output_field=IntegerField()),
            sum_x2=Coalesce(
                Sum(ExpressionWrapper(F('total_cnt') * F('total_cnt'), output_field=DecimalField())),
                Value(0, output_field=DecimalField()),
            ),
        )
        .order_by('season_year', 'month')
    )

    totals_by_year = {}
    errors_by_year = {}
    for row in rows:
        season_year = row['season_year']
        month = row['month']
        totals_by_year.setdefault(season_year, {})[month] = int(row['total'] or 0)
        row_count = int(row['row_count'] or 0)
        if row_count:
            mean = float(row['total'] or 0) / row_count
            variance = (float(row['sum_x2'] or 0) / row_count) - (mean * mean)
            variance = max(variance, 0.0)
            std_dev = sqrt(variance)
            errors_by_year.setdefault(season_year, {})[month] = std_dev

    categories = [month_labels[m] for m in month_sequence]
    series = []
    for season_year in sorted(totals_by_year):
        data = []
        for month in month_sequence:
            total = totals_by_year[season_year].get(month, 0)
            std_dev = errors_by_year.get(season_year, {}).get(month)
            data.append({
                'x': month_labels[month],
                'y': total,
                'sd': float(std_dev) if std_dev is not None else None,
            })
        series.append({
            'name': f"{season_year}-{season_year + 1}",
            'data': data,
        })

    context = {
        'chart_data': {
            'categories': categories,
            'series': series,
        }
    }
    return render(request, 'kiccd_app/pages/cf-monthly-charts.html', context)


@login_required
def cf_daily_catch_rate(request):
    """Render the mean daily targeted CF catch rate (count per fisher-day) by month."""
    if not request.user.has_perm('kiccd_app.view_cfcatch'):
        return render(request, 'kiccd_app/403.html', status=403)

    year_options = list(
        CfEvent.objects.filter(cf_date__isnull=False)
        .values_list('cf_date__year', flat=True)
        .distinct()
        .order_by('-cf_date__year')
    )
    current_year = timezone.now().year
    requested_year = request.GET.get('year')
    try:
        requested_year = int(requested_year) if requested_year else None
    except (TypeError, ValueError):
        requested_year = None

    if year_options:
        selected_year = requested_year if requested_year in year_options else year_options[0]
    else:
        selected_year = current_year

    month_sequence = list(range(1, 13))
    month_labels = {
        1: 'Jan',
        2: 'Feb',
        3: 'Mar',
        4: 'Apr',
        5: 'May',
        6: 'Jun',
        7: 'Jul',
        8: 'Aug',
        9: 'Sep',
        10: 'Oct',
        11: 'Nov',
        12: 'Dec',
    }

    species_targets = ['Silver Carp', 'Grass Carp', 'Bighead Carp']
    species_objs = FishSpecies.objects.filter(name__in=species_targets, targeted=True)
    species_lookup = {species.name: species for species in species_objs}
    ordered_species = [name for name in species_targets if name in species_lookup]

    month_stats = {
        month: {
            'count': 0,
            'species': {name: {'sum': 0, 'sum_sq': 0} for name in ordered_species},
        }
        for month in month_sequence
    }

    fisher_days = []
    if year_options:
        fisher_days = list(
            CfEvent.objects.filter(cf_date__year=selected_year)
            .values('fisher_id', 'cf_date')
            .distinct()
        )

    species_totals_by_species = {name: {} for name in ordered_species}
    if ordered_species and fisher_days:
        species_totals_qs = (
            CfCatch.objects.filter(
                event__cf_date__year=selected_year,
                species__name__in=ordered_species,
            )
            .values('species__name', 'event__fisher_id', 'event__cf_date')
            .annotate(
                total=Coalesce(
                    Sum('total_cnt'),
                    Value(0),
                    output_field=IntegerField(),
                )
            )
        )
        for row in species_totals_qs:
            key = (row['event__fisher_id'], row['event__cf_date'])
            species_totals_by_species[row['species__name']][key] = int(row['total'] or 0)

    for entry in fisher_days:
        key = (entry['fisher_id'], entry['cf_date'])
        stats = month_stats[entry['cf_date'].month]
        stats['count'] += 1
        for species_name in ordered_species:
            species_stats = stats['species'][species_name]
            total = species_totals_by_species[species_name].get(key, 0)
            species_stats['sum'] += total
            species_stats['sum_sq'] += total * total

    has_data = bool(ordered_species) and any(stats['count'] > 0 for stats in month_stats.values())
    categories = [month_labels[m] for m in month_sequence]
    series = []
    if has_data:
        for species_name in ordered_species:
            month_series = []
            for month in month_sequence:
                stats = month_stats[month]
                count = stats['count']
                species_stats = stats['species'][species_name]
                if count:
                    raw_mean = species_stats['sum'] / count
                    variance = (species_stats['sum_sq'] / count) - (raw_mean * raw_mean)
                    variance = max(variance, 0.0)
                    std_err = sqrt(variance) / sqrt(count) if count else None
                else:
                    raw_mean = 0.0
                    std_err = None
                displayed_mean = round(raw_mean, 2)
                month_series.append({
                    'x': month_labels[month],
                    'y': float(f"{displayed_mean:.2f}"),
                    'se': float(std_err) if std_err is not None else None,
                })
            series.append({'name': species_name, 'data': month_series})

    context = {
        'year_options': year_options,
        'selected_year': selected_year,
        'chart_data': {
            'categories': categories,
            'series': series,
        },
    }
    return render(request, 'kiccd_app/pages/cf-daily-catch-rate.html', context)


@login_required
def subsample_length_distribution(request):
    """Render a filtered subsample length histogram with binned counts and table output."""
    if not request.user.has_perm('kiccd_app.view_subsample'):
        return render(request, 'kiccd_app/403.html', status=403)

    bin_size_lookup = {
        '10mm': {'mm': 10.0, 'label': '10 mm', 'unit': 'mm', 'to_display': 1.0, 'precision': 0},
        '25mm': {'mm': 25.0, 'label': '25 mm', 'unit': 'mm', 'to_display': 1.0, 'precision': 0},
        '50mm': {'mm': 50.0, 'label': '50 mm', 'unit': 'mm', 'to_display': 1.0, 'precision': 0},
        '100mm': {'mm': 100.0, 'label': '100 mm', 'unit': 'mm', 'to_display': 1.0, 'precision': 0},
        '1in': {'mm': 25.4, 'label': '1 inch', 'unit': 'in', 'to_display': 25.4, 'precision': 0},
        '2in': {'mm': 50.8, 'label': '2 inch', 'unit': 'in', 'to_display': 25.4, 'precision': 0},
    }

    selected_bin_size = (request.GET.get('bin_size') or '').strip()
    selected_year = (request.GET.get('year') or '').strip()
    selected_season = (request.GET.get('season') or '').strip()
    selected_basin = (request.GET.get('basin') or '').strip()
    selected_pool = (request.GET.get('pool') or '').strip()
    selected_species = (request.GET.get('species') or '').strip()
    selected_sex = (request.GET.get('sex') or '').strip()

    has_requested_filters = any([
        selected_bin_size,
        selected_year,
        selected_season,
        selected_basin,
        selected_pool,
        selected_species,
        selected_sex,
    ])

    subsample_qs = Subsample.objects.filter(length_mm__isnull=False)
    year_options = list(
        subsample_qs
        .annotate(year=ExtractYear('cf_date'))
        .values_list('year', flat=True)
        .distinct()
        .order_by('-year')
    )
    season_options = list(
        subsample_qs
        .values_list('datez__cf_season', flat=True)
        .distinct()
        .order_by('datez__cf_season')
    )
    basin_options = Basin.objects.all().order_by('name')
    pool_options = Pool.objects.all().order_by('pool_id')
    species_options = FishSpecies.objects.filter(targeted=True).order_by('-ranked', 'name')
    sex_options = FishSex.objects.all().order_by('sx_id')

    chart_data = {'categories': [], 'series': []}
    distribution_rows = []
    validation_message = ''
    selected_unit = 'mm'

    if has_requested_filters:
        filtered_qs = subsample_qs

        if selected_year:
            try:
                filtered_qs = filtered_qs.filter(cf_date__year=int(selected_year))
            except (TypeError, ValueError):
                selected_year = ''

        if selected_season:
            filtered_qs = filtered_qs.filter(datez__cf_season=selected_season)

        if selected_basin:
            try:
                filtered_qs = filtered_qs.filter(basin_id=int(selected_basin))
            except (TypeError, ValueError):
                selected_basin = ''

        if selected_pool:
            try:
                filtered_qs = filtered_qs.filter(pool_id=int(selected_pool))
            except (TypeError, ValueError):
                selected_pool = ''

        if selected_species:
            try:
                filtered_qs = filtered_qs.filter(spp_id=int(selected_species))
            except (TypeError, ValueError):
                selected_species = ''

        if selected_sex:
            try:
                filtered_qs = filtered_qs.filter(sex_id=int(selected_sex))
            except (TypeError, ValueError):
                selected_sex = ''

        if selected_bin_size in bin_size_lookup:
            selected_bin_details = bin_size_lookup[selected_bin_size]
            bin_size_mm = float(selected_bin_details['mm'])
            selected_unit = selected_bin_details['unit']
            display_divisor = float(selected_bin_details['to_display'])
            display_precision = int(selected_bin_details['precision'])
            lengths = [float(length) for length in filtered_qs.values_list('length_mm', flat=True)]

            if lengths:
                min_length = min(lengths)
                start_edge = int(min_length // bin_size_mm) * bin_size_mm

                counts_by_bin = {}
                for length in lengths:
                    bin_index = int((length - start_edge) // bin_size_mm)
                    counts_by_bin[bin_index] = counts_by_bin.get(bin_index, 0) + 1

                total_length_count = len(lengths)

                max_bin_index = max(counts_by_bin)
                categories = []
                counts = []

                for idx in range(0, max_bin_index + 1):
                    bin_min_mm = start_edge + (idx * bin_size_mm)
                    bin_max_mm = bin_min_mm + bin_size_mm
                    bin_min_display = bin_min_mm / display_divisor
                    bin_max_display = bin_max_mm / display_divisor
                    bin_count = counts_by_bin.get(idx, 0)
                    table_label = f"{bin_min_display:.{display_precision}f}"
                    label = table_label
                    categories.append(label)
                    counts.append(bin_count)
                    distribution_rows.append({
                        'bin_label': table_label,
                        'bin_min': round(bin_min_display, display_precision),
                        'bin_max': round(bin_max_display, display_precision),
                        'count': bin_count,
                        'length_frequency': ((bin_count / total_length_count) * 100.0) if total_length_count else 0.0,
                    })

                chart_data = {
                    'categories': categories,
                    'series': [{'name': 'Fish Count', 'data': counts}],
                }
        else:
            validation_message = 'Select a bin size to generate the histogram.'

    context = {
        'bin_size_options': [
            {'value': '10mm', 'label': '10 mm'},
            {'value': '25mm', 'label': '25 mm'},
            {'value': '50mm', 'label': '50 mm'},
            {'value': '100mm', 'label': '100 mm'},
            {'value': '1in', 'label': '1 inch'},
            {'value': '2in', 'label': '2 inch'},
        ],
        'selected_bin_size': selected_bin_size,
        'year_options': year_options,
        'season_options': season_options,
        'basin_options': basin_options,
        'pool_options': pool_options,
        'species_options': species_options,
        'sex_options': sex_options,
        'selected_year': selected_year,
        'selected_season': selected_season,
        'selected_basin': selected_basin,
        'selected_pool': selected_pool,
        'selected_species': selected_species,
        'selected_sex': selected_sex,
        'has_requested_filters': has_requested_filters,
        'validation_message': validation_message,
        'length_unit': selected_unit,
        'distribution_rows': distribution_rows,
        'chart_data': chart_data,
    }
    return render(request, 'kiccd_app/pages/subsample-length-distribution.html', context)


@login_required
def ic_length_distribution(request):
    """Render a filtered IC catch length distribution with count and frequency histograms."""
    if not request.user.has_perm('kiccd_app.view_iccatch'):
        return render(request, 'kiccd_app/403.html', status=403)

    bin_size_lookup = {
        '10mm': {'mm': 10.0, 'label': '10 mm', 'unit': 'mm', 'to_display': 1.0, 'precision': 0},
        '25mm': {'mm': 25.0, 'label': '25 mm', 'unit': 'mm', 'to_display': 1.0, 'precision': 0},
        '50mm': {'mm': 50.0, 'label': '50 mm', 'unit': 'mm', 'to_display': 1.0, 'precision': 0},
        '100mm': {'mm': 100.0, 'label': '100 mm', 'unit': 'mm', 'to_display': 1.0, 'precision': 0},
        '1in': {'mm': 25.4, 'label': '1 inch', 'unit': 'in', 'to_display': 25.4, 'precision': 0},
        '2in': {'mm': 50.8, 'label': '2 inch', 'unit': 'in', 'to_display': 25.4, 'precision': 0},
    }

    selected_bin_size = (request.GET.get('bin_size') or '').strip()
    selected_year = (request.GET.get('year') or '').strip()
    selected_season = (request.GET.get('season') or '').strip()
    selected_basin = (request.GET.get('basin') or '').strip()
    selected_pool = (request.GET.get('pool') or '').strip()
    selected_site = (request.GET.get('site') or '').strip()
    selected_month = (request.GET.get('month') or '').strip()
    selected_species = (request.GET.get('species') or '').strip()
    selected_sex = (request.GET.get('sex') or '').strip()

    has_requested_filters = any([
        selected_bin_size,
        selected_year,
        selected_season,
        selected_basin,
        selected_pool,
        selected_site,
        selected_month,
        selected_species,
        selected_sex,
    ])

    ic_catch_qs = IcCatch.objects.filter(length_mm__isnull=False).exclude(species__spp_id=0)
    year_options = list(
        ic_catch_qs
        .annotate(year=ExtractYear('event__event_date'))
        .values_list('year', flat=True)
        .distinct()
        .order_by('-year')
    )
    season_options = list(
        ic_catch_qs
        .values_list('event__datez__ic_season', flat=True)
        .distinct()
        .order_by('event__datez__ic_season')
    )
    basin_options = Basin.objects.filter(samplesite__icevent__iccatch__isnull=False).distinct().order_by('name')
    pool_options = Pool.objects.filter(samplesite__icevent__iccatch__isnull=False).distinct().order_by('pool_id')
    site_options = SampleSite.objects.filter(icevent__iccatch__isnull=False).distinct().order_by('name')
    month_options = list(
        Dates.objects.filter(icevent__iccatch__isnull=False)
        .values('ic_month1', 'ic_mon')
        .distinct()
        .order_by('ic_month1')
    )
    species_options = FishSpecies.objects.filter(iccatch__isnull=False).exclude(spp_id=0).distinct().order_by('-ranked', 'name')
    sex_options = FishSex.objects.filter(iccatch__isnull=False).distinct().order_by('abbrev')

    count_chart_data = {'categories': [], 'series': []}
    frequency_chart_data = {'categories': [], 'series': []}
    distribution_rows = []
    validation_message = ''
    selected_unit = 'mm'

    if has_requested_filters:
        filtered_qs = ic_catch_qs

        if selected_year:
            try:
                filtered_qs = filtered_qs.filter(event__event_date__year=int(selected_year))
            except (TypeError, ValueError):
                selected_year = ''

        if selected_season:
            filtered_qs = filtered_qs.filter(event__datez__ic_season=selected_season)

        if selected_basin:
            try:
                filtered_qs = filtered_qs.filter(event__site__basin_id=int(selected_basin))
            except (TypeError, ValueError):
                selected_basin = ''

        if selected_pool:
            try:
                filtered_qs = filtered_qs.filter(event__site__pool_id=int(selected_pool))
            except (TypeError, ValueError):
                selected_pool = ''

        if selected_site:
            try:
                filtered_qs = filtered_qs.filter(event__site_id=int(selected_site))
            except (TypeError, ValueError):
                selected_site = ''

        if selected_month:
            try:
                filtered_qs = filtered_qs.filter(event__datez__ic_month1=int(selected_month))
            except (TypeError, ValueError):
                selected_month = ''

        if selected_species:
            try:
                filtered_qs = filtered_qs.filter(species_id=int(selected_species))
            except (TypeError, ValueError):
                selected_species = ''

        if selected_sex:
            try:
                filtered_qs = filtered_qs.filter(fish_sex_id=int(selected_sex))
            except (TypeError, ValueError):
                selected_sex = ''

        if selected_bin_size in bin_size_lookup:
            selected_bin_details = bin_size_lookup[selected_bin_size]
            bin_size_mm = float(selected_bin_details['mm'])
            selected_unit = selected_bin_details['unit']
            display_divisor = float(selected_bin_details['to_display'])
            display_precision = int(selected_bin_details['precision'])
            length_rows = list(filtered_qs.values_list('length_mm', 'fish_count'))

            if length_rows:
                min_length = min(float(length_mm) for length_mm, _ in length_rows if length_mm is not None)
                start_edge = int(min_length // bin_size_mm) * bin_size_mm

                counts_by_bin = {}
                total_fish_count = 0
                for length_mm, fish_count in length_rows:
                    if length_mm is None:
                        continue
                    count_value = int(fish_count) if fish_count is not None else 1
                    if count_value < 1:
                        continue
                    bin_index = int((float(length_mm) - start_edge) // bin_size_mm)
                    counts_by_bin[bin_index] = counts_by_bin.get(bin_index, 0) + count_value
                    total_fish_count += count_value

                if counts_by_bin and total_fish_count > 0:
                    max_bin_index = max(counts_by_bin)
                    categories = []
                    counts = []
                    frequencies = []

                    for idx in range(0, max_bin_index + 1):
                        bin_min_mm = start_edge + (idx * bin_size_mm)
                        bin_max_mm = bin_min_mm + bin_size_mm
                        bin_min_display = bin_min_mm / display_divisor
                        bin_max_display = bin_max_mm / display_divisor
                        bin_count = counts_by_bin.get(idx, 0)
                        bin_frequency = (bin_count / total_fish_count) * 100.0
                        label = f"{bin_min_display:.{display_precision}f}"
                        table_label = f"{bin_min_display:.{display_precision}f}"
                        categories.append(label)
                        counts.append(bin_count)
                        frequencies.append(round(bin_frequency, 2))
                        distribution_rows.append({
                            'bin_label': table_label,
                            'bin_min': round(bin_min_display, display_precision),
                            'bin_max': round(bin_max_display, display_precision),
                            'count': bin_count,
                            'length_frequency': bin_frequency,
                        })

                    count_chart_data = {
                        'categories': categories,
                        'series': [{'name': 'Fish Count', 'data': counts}],
                    }
                    frequency_chart_data = {
                        'categories': categories,
                        'series': [{'name': 'Frequency (%)', 'data': frequencies}],
                    }
        else:
            validation_message = 'Select a bin size to generate the histogram.'

    context = {
        'bin_size_options': [
            {'value': '10mm', 'label': '10 mm'},
            {'value': '25mm', 'label': '25 mm'},
            {'value': '50mm', 'label': '50 mm'},
            {'value': '100mm', 'label': '100 mm'},
            {'value': '1in', 'label': '1 inch'},
            {'value': '2in', 'label': '2 inch'},
        ],
        'selected_bin_size': selected_bin_size,
        'year_options': year_options,
        'season_options': season_options,
        'basin_options': basin_options,
        'pool_options': pool_options,
        'site_options': site_options,
        'month_options': month_options,
        'species_options': species_options,
        'sex_options': sex_options,
        'selected_year': selected_year,
        'selected_season': selected_season,
        'selected_basin': selected_basin,
        'selected_pool': selected_pool,
        'selected_site': selected_site,
        'selected_month': selected_month,
        'selected_species': selected_species,
        'selected_sex': selected_sex,
        'has_requested_filters': has_requested_filters,
        'validation_message': validation_message,
        'length_unit': selected_unit,
        'distribution_rows': distribution_rows,
        'count_chart_data': count_chart_data,
        'frequency_chart_data': frequency_chart_data,
    }
    return render(request, 'kiccd_app/pages/ic-length-distribution.html', context)


@login_required
def cf_event_batch_create(request):
    """Batch-add CfEvent rows that share the same date/fisher/observer/site."""
    if not request.user.has_perm('kiccd_app.add_cfevent'):
        return render(request, 'kiccd_app/403.html', status=403)

    CfEventFormSet = modelformset_factory(CfEvent, form=CfEventRowForm, extra=12, can_delete=False)
    shared_form = CfEventBatchInfoForm(request.POST or None)
    formset = CfEventFormSet(request.POST or None, queryset=CfEvent.objects.none())

    if request.method == 'POST':
        if shared_form.is_valid() and formset.is_valid():
            shared_data = shared_form.cleaned_data
            created = 0
            net_count = 0
            for form in formset:
                if not form.cleaned_data or not form.has_changed():
                    continue
                instance = form.save(commit=False)
                instance.cf_date = shared_data['cf_date']
                instance.fisher = shared_data['fisher']
                instance.observer = shared_data['observer']
                instance.site = shared_data['site']
                net_count += 1
                instance.set_num = net_count
                instance.save(user=request.user)
                created += 1
            if created:
                messages.success(request, f'Added {created} net sets related to the contract fishing efforts on {shared_data["cf_date"]}.')
                return redirect('kiccd_app:recent_cf_events')
            messages.info(request, 'Please fill in at least one row before submitting.')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'kiccd_app/pages/cf-event-bulk-form.html', {
        'shared_form': shared_form,
        'formset': formset,
        'partners': Partner.objects.order_by('abbrev'),
        'site_types': SiteType.objects.order_by('name'),
        'pools': Pool.objects.order_by('pool_id'),
        'states': State.objects.order_by('name'),
        'counties': County.objects.order_by('name'),
        'basins': Basin.objects.order_by('name'),
        'tribs': Trib.objects.order_by('name'),
    })


@login_required
def cf_event_create(request):
    """Create a new CfEvent record. Requires add_cfevent permission."""
    if not request.user.has_perm('kiccd_app.add_cfevent'):
        return render(request, 'kiccd_app/403.html', status=403)

    if request.method == 'POST':
        form = CfEventForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save(user=request.user)
            messages.success(request, 'Recorded contract fishing effort.')
            return redirect('kiccd_app:recent_cf_events')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CfEventForm()

    return render(request, 'kiccd_app/pages/cf-event-form.html', {'form': form})


@login_required
def cf_catch_batch_create(request):
    """Add multiple CfCatch rows for the same CfEvent."""
    if not request.user.has_perm('kiccd_app.add_cfcatch'):
        return render(request, 'kiccd_app/403.html', status=403)

    CatchFormSet = modelformset_factory(CfCatch, form=CfCatchRowForm, extra=15, can_delete=False)
    shared_form = CfCatchEventForm(request.POST or None)

    # Initialize shared_form with POST data and pass it as initial for dynamic queryset handling
    # post_data = request.POST or None
    # initial_data = {'event': post_data.get('event')} if post_data else {}
    # shared_form = CfCatchEventForm(data=post_data, initial=initial_data)

    formset = CatchFormSet(request.POST or None, queryset=CfCatch.objects.none())

    if request.method == 'POST':
        print("POST data:", request.POST)  # Check the 'event' value
        if shared_form.is_valid() and formset.is_valid():
            event = shared_form.cleaned_data['event']
            created = 0
            for form in formset:
                if not form.cleaned_data or not form.has_changed():
                    continue
                catch = form.save(commit=False)
                catch.event = event
                if catch.total_cnt is None:
                    healthy = catch.healthy_cnt or 0
                    moribund = catch.moribund_cnt or 0
                    catch.total_cnt = healthy + moribund
                catch.save(user=request.user)
                created += 1
            if created:
                messages.success(request, f'Created {created} catch records for {event}.')
                return redirect('kiccd_app:cf_catch_list')
            messages.info(request, 'Please add at least one catch row before submitting.')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'kiccd_app/pages/cf-catch-bulk-form.html', {
        'shared_form': shared_form,
        'formset': formset,
    })


class CfCatchListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = CfCatch
    template_name = 'kiccd_app/pages/cf-catch-list.html'
    context_object_name = 'catches'
    # paginate_by = 50
    permission_required = 'kiccd_app.view_cfcatch'

    def get_queryset(self):
        gram_value = Decimal('0.001')
        weight_expr = Coalesce(
            F('mean_weight_g'),
            F('predicted_weight_g'),
            output_field=DecimalField(max_digits=18, decimal_places=6),
        )
        cnt = F('moribund_cnt')

        return (
            CfCatch.objects.select_related('event__fisher', 'species', 'event__site', 'event__site__pool', 'event__datez')
            .annotate(
                display_weight=weight_expr,
                total_weight_kg=ExpressionWrapper(
                    weight_expr * Value(gram_value) * cnt,
                    output_field=DecimalField(max_digits=18, decimal_places=6),
                ),
            )
            .order_by('-event__cf_date', 'event__fisher', 'event__set_num', 'species__name')
        )


@login_required
def cf_refresh_subsample_means(request):
    if not request.user.has_perm('kiccd_app.change_cfcatch'):
        return render(request, 'kiccd_app/403.html', status=403)
    if request.method != 'POST':
        return redirect('kiccd_app:cf_catch_list')

    updated = 0
    skipped = 0
    recent_catches = CfCatch.objects.order_by('-event__event_id')[:500]

    for catch in recent_catches:
        if not catch.ss_code:
            skipped += 1
            continue

        updates = {}
        ss_len = Subsample.mean_length_by_ss_code(catch.ss_code)
        ss_wt = Subsample.mean_weight_by_ss_code(catch.ss_code)

        if ss_len is not None:
            new_len = Decimal(ss_len)
            if catch.mean_length_mm != new_len:
                updates['mean_length_mm'] = new_len
            if catch.mean_length != new_len:
                updates['mean_length'] = new_len

        if ss_wt is not None:
            new_wt = Decimal(ss_wt)
            if catch.mean_weight_g != new_wt:
                updates['mean_weight_g'] = new_wt

        if updates:
            CfCatch.objects.filter(pk=catch.pk).update(**updates)
            updated += 1

    if updated:
        messages.success(request, f'Updated length/weight values for {updated} Contract Fishing records.')
    else:
        messages.info(request, 'Contract Fishing records were already synced to the subsample data.')
    if skipped:
        messages.info(request, f'Skipped {skipped} Contract Fishing records that lacked SS_Codes.')

    return redirect('kiccd_app:cf_catch_list')


class RaCatchListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = RaCatch
    template_name = 'kiccd_app/pages/ra-catch-list.html'
    context_object_name = 'catches'
    # paginate_by = 50
    permission_required = 'kiccd_app.view_racatch'
    def get_queryset(self):
        return (
            RaCatch.objects.select_related('event__fisher', 'species', 'event__site', 'event__site__basin', 'event__datez')
            .order_by('-event__ra_date', 'event__fisher', 'event__net_set', 'event__net_num', 'species__name')
        )


@login_required
def ra_catch_refresh_subsample_means(request):
    if not request.user.has_perm('kiccd_app.change_racatch'):
        return render(request, 'kiccd_app/403.html', status=403)
    if request.method != 'POST':
        return redirect('kiccd_app:ra_catch_list')

    updated = 0
    skipped = 0
    recent_catches = RaCatch.objects.order_by('-event__event_id')[:1000]
    for catch in recent_catches:
        if not catch.ss_code:
            skipped += 1
            continue

        updates = {}
        ss_len = Subsample.mean_length_by_ss_code(catch.ss_code)
        ss_wt = Subsample.mean_weight_by_ss_code(catch.ss_code)

        if ss_len is not None:
            new_len = Decimal(ss_len)
            if catch.mean_length_mm != new_len:
                updates['mean_length_mm'] = new_len

        if ss_wt is not None:
            new_wt = Decimal(ss_wt)
            if catch.mean_weight_g != new_wt:
                updates['mean_weight_g'] = new_wt

        if updates:
            RaCatch.objects.filter(pk=catch.pk).update(**updates)
            updated += 1

    if updated:
        messages.success(request, f'Updated the length & weight of {"a single Ride-Along" if updated == 1 else f"{updated} Ride-Alongs"}.')
    else:
        messages.info(request, 'All Ride-Alongs were already synced to the subsample data.')
    if skipped:
        messages.info(request, f'Skipped {skipped} {"Ride-Along" if skipped == 1 else "Ride-Alongs"} without defined SS_Codes.')

    return redirect('kiccd_app:ra_catch_list')


class IchpHarvestListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = IchpCatch
    template_name = 'kiccd_app/pages/ichp-harvest-list.html'
    context_object_name = 'catches'
    permission_required = 'kiccd_app.view_IchpCatch'
    def get_queryset(self):
        return (
            IchpCatch.objects.select_related('event__fisher', 'species', 'event__basin', 'event__site', 'event__datez')
            .order_by('-event__ichp_date', 'event__fisher', 'event__net_haul', 'species__name')
        )


@login_required
def ichp_refresh_subsample_means(request):
    if not request.user.has_perm('kiccd_app.change_ichpcatch'):
        return render(request, 'kiccd_app/403.html', status=403)
    if request.method != 'POST':
        return redirect('kiccd_app:ichp_harvest_list')

    updated = 0
    skipped = 0
    recent_catches = IchpCatch.objects.order_by('-event__event_id')[:1000]
    for catch in recent_catches:
        if not catch.ss_code:
            skipped += 1
            continue

        updates = {}
        ss_len = Subsample.mean_length_by_ss_code(catch.ss_code)
        ss_wt = Subsample.mean_weight_by_ss_code(catch.ss_code)

        if ss_len is not None:
            new_len = Decimal(ss_len)
            if catch.ss_mean_length_mm != new_len:
                updates['ss_mean_length_mm'] = new_len

        if ss_wt is not None:
            new_wt = Decimal(ss_wt)
            if catch.ss_mean_weight_g != new_wt:
                updates['ss_mean_weight_g'] = new_wt

        if updates:
            IchpCatch.objects.filter(pk=catch.pk).update(**updates)
            updated += 1

    if updated:
        messages.success(request, f'Updated length/weight values for {updated} IC Harvest Program records.')
    else:
        messages.info(request, 'IC Harvest Program records were already synced to the subsample data.')
    if skipped:
        messages.info(request, f'Skipped {skipped} IC Harvest Program records that lacked SS_Codes.')

    return redirect('kiccd_app:ichp_harvest_list')


class IcCatchListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = IcCatch
    template_name = 'kiccd_app/pages/ic-catch-list.html'
    context_object_name = 'catches'
    # paginate_by = 50
    permission_required = 'kiccd_app.view_iccatch'

    def get_queryset(self):
        return (
            IcCatch.objects.select_related('event__site', 'species', 'event__site__pool', 'event__site__basin', 'fish_sex', 'event__datez')
            .order_by('-event__event_date', 'event__site', 'event__effort_num', 'species__name')[:25000]
        )

class RecentIcCatchView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = IcCatch
    template_name = 'kiccd_app/pages/recent-ic-catch.html'
    context_object_name = 'catches'
    permission_required = 'kiccd_app.view_iccatch'

    def get_queryset(self):
        return (
            IcCatch.objects.select_related('event__site', 'species', 'event__site__pool', 'event__site__basin', 'fish_sex', 'event__datez')
            .order_by('-catch_id')[:2500]
        )

class IcAgeGrowthListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = IcAgeGrowth
    template_name = 'kiccd_app/pages/ic-age-growth-list.html'
    context_object_name = 'records'
    permission_required = 'kiccd_app.view_icagegrowth'

    def get_queryset(self):
        return (
            IcAgeGrowth.objects.select_related('agency', 'basin', 'pool', 'site', 'spp', 'sex', 'datez')
            .order_by('-catch_date', 'site__name', 'spp__name')
        )

class SubsampleListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Subsample
    template_name = 'kiccd_app/pages/ss-data-list.html'
    context_object_name = 'subs'
    permission_required = 'kiccd_app.view_Subsample'

    def get_queryset(self):
        return (
            Subsample.objects.select_related('fisher', 'observer', 'basin', 'pool', 'spp','sex', 'datez')
            .order_by('-cf_date', 'fisher', 'spp')[:2000]
        )

class SampleSiteListView(ListView):
    model = SampleSite
    template_name = 'kiccd_app/pages/lookup-sample-sites.html'
    context_object_name = 'sites'
    paginate_by = 50

    def get_queryset(self):
        return SampleSite.objects.select_related('pool','state','county','trib').order_by('name')

class PoolListView(ListView):
    model = Pool
    template_name = 'kiccd_app/pages/lookup-pools.html'
    context_object_name = 'pools'
    # paginate_by = 20

    def get_queryset(self):
        return Pool.objects.all().order_by('pool_id')

class SpeciesListView(ListView):
    model = FishSpecies
    template_name = 'kiccd_app/pages/lookup-species.html'
    context_object_name = 'fishes'
    # paginate_by = 20

    def get_queryset(self):
        return FishSpecies.objects.all().order_by('name')

class BasinListView(ListView):
    model = Basin
    template_name = 'kiccd_app/pages/lookup-basins.html'
    context_object_name = 'basins'
    # paginate_by = 20

    def get_queryset(self):
        return Basin.objects.all().order_by('name')

class CrewListView(ListView):
    model = Crew
    template_name = 'kiccd_app/pages/lookup-crews.html'
    context_object_name = 'crews'
    # paginate_by = 20

    def get_queryset(self):
        return Crew.objects.select_related('agency','office').all().order_by('crew_id')

class ProjectListView(ListView):
    model = Project
    template_name = 'kiccd_app/pages/lookup-projects.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.exclude(project_id=60).exclude(project_id=70).order_by('project_id')

class GearListView(ListView):
    model = Gear
    template_name = 'kiccd_app/pages/lookup-gear.html'
    context_object_name = 'gears'
    # paginate_by = 20

    def get_queryset(self):
        return Gear.objects.all().order_by('name')

class FisherListView(ListView):
    model = Fisher
    template_name = 'kiccd_app/pages/lookup-fishers.html'
    context_object_name = 'fishers'
    # paginate_by = 20

    def get_queryset(self):
        return Fisher.objects.all().order_by('last_name', 'first_name')

class ObserverListView(ListView):
    model = Observer
    template_name = 'kiccd_app/pages/lookup-observers.html'
    context_object_name = 'observers'
    # paginate_by = 20

    def get_queryset(self):
        return Observer.objects.all().order_by('observer_id')


@login_required
def subsample_bulk_create(request):
    """Add up to 20 Subsample rows that share the same CF date/fisher info."""
    if not request.user.has_perm('kiccd_app.add_subsample'):
        return render(request, 'kiccd_app/403.html', status=403)

    SubsampleFormSet = modelformset_factory(Subsample, form=SubsampleForm, extra=25, can_delete=False)
    shared_form = SubsampleBatchInfoForm(request.POST or None)
    formset = SubsampleFormSet(request.POST or None, queryset=Subsample.objects.none())

    if request.method == 'POST':
        if shared_form.is_valid() and formset.is_valid():
            shared_data = shared_form.cleaned_data
            created = 0
            for form in formset:
                if not form.cleaned_data or not form.has_changed():
                    continue
                subsample = form.save(commit=False)
                subsample.cf_date = shared_data['cf_date']
                subsample.fisher = shared_data['fisher']
                subsample.observer = shared_data['observer']
                subsample.basin = shared_data['basin']
                subsample.pool = shared_data['pool']
                subsample.spp = shared_data['spp']
                subsample.save()
                created += 1

            if created:
                messages.success(request, f'Added {created} new {shared_data["spp"]} to the subsample table.')
                return redirect('kiccd_app:subsample_bulk_create')

            messages.info(request, 'Add at least one subsample row before submitting.')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'kiccd_app/pages/subsample-bulk-form.html', {
        'shared_form': shared_form,
        'formset': formset,
        'partners': Partner.objects.order_by('abbrev'),
    })

@login_required
def ic_age_growth_bulk_create(request):
    """Capture multiple IcAgeGrowth rows that share the same collection metadata."""
    if not request.user.has_perm('kiccd_app.add_icagegrowth'):
        return render(request, 'kiccd_app/403.html', status=403)

    IcAgeGrowthFormSet = modelformset_factory(IcAgeGrowth, form=IcAgeGrowthRowForm, extra=25, can_delete=False)
    shared_form = IcAgeGrowthBatchInfoForm(request.POST or None)
    formset = IcAgeGrowthFormSet(request.POST or None, queryset=IcAgeGrowth.objects.none())

    if request.method == 'POST':
        if shared_form.is_valid() and formset.is_valid():
            shared_data = shared_form.cleaned_data
            created = 0
            default_sex = FishSex.objects.filter(sx_id=0).first()
            default_project = Project.objects.filter(project_id=80).first()
            default_agency = Partner.objects.filter(partner_id=6).first()

            for form in formset:
                if not form.cleaned_data or not form.has_changed():
                    continue

                record = form.save(commit=False)
                record.catch_date = shared_data['catch_date']
                record.project = shared_data['project']
                record.agency = shared_data['agency']
                record.basin = shared_data['basin']
                record.pool = shared_data['pool']
                record.site = shared_data['site']
                record.latitude = shared_data.get('latitude')
                record.longitude = shared_data.get('longitude')
                record.spp = shared_data['spp']

                if record.project is None and default_project is not None:
                    record.project = default_project
                
                if record.agency is None and default_agency is not None:
                    record.agency = default_agency

                if record.sex is None and default_sex is not None:
                    record.sex = default_sex

                record.save(user=request.user)
                created += 1

            if created:
                messages.success(request, f'Saved {created} age & growth record{"s" if created != 1 else ""}.')
                return redirect('kiccd_app:ic_age_growth_bulk_create')

            messages.info(request, 'Add at least one fish row before submitting.')
        else:
            messages.error(request, 'Please correct the errors below and resubmit.')

    return render(request, 'kiccd_app/pages/ic-age-growth-bulk-form.html', {
        'shared_form': shared_form,
        'formset': formset,
        'site_types': SiteType.objects.order_by('name'),
        'pools': Pool.objects.order_by('pool_id'),
        'states': State.objects.order_by('name'),
        'basins': Basin.objects.order_by('name'),
    })

@login_required
def pools_by_basin(request, basin_id):
    """AJAX endpoint: return pools related to a basin.

    Since Pool does not have a direct FK to Basin, we look for Pools
    that are referenced by Trib records in the given basin. If none
    are found, return all pools as a fallback.
    """
    try:
        # Pools referenced by tribs in this basin
        pools_qs = Pool.objects.filter(trib__basin_id=basin_id).distinct().order_by('pool_id')
        if not pools_qs.exists():
            pools_qs = Pool.objects.all().order_by('pool_id')
        pools = [{'id': p.pool_id, 'name': p.name} for p in pools_qs]
        return JsonResponse({'pools': pools})
    except Exception:
        return JsonResponse({'pools': []})

@login_required
def counties_by_state(request, state_id):
    """AJAX endpoint: return counties for a given state."""
    try:
        counties_qs = County.objects.filter(state_id=state_id).order_by('name')
        counties = [{'id': c.county_id, 'name': c.name} for c in counties_qs]
        return JsonResponse({'counties': counties})
    except Exception:
        return JsonResponse({'counties': []})

@login_required
def tribs_by_basin(request, basin_id):
    """AJAX endpoint: return tribs for a given basin."""
    try:
        tribs_qs = Trib.objects.filter(basin_id=basin_id).order_by('name')
        tribs = [{'id': t.trib_id, 'name': t.name} for t in tribs_qs]
        return JsonResponse({'tribs': tribs})
    except Exception:
        return JsonResponse({'tribs': []})


def tribs_by_basin_and_pool(request, basin_id, pool_id):
    """AJAX endpoint: return tribs filtered by both basin and pool."""
    try:
        tribs_qs = Trib.objects.filter(basin_id=basin_id, pool_id=pool_id).order_by('name')
        tribs = [{'id': t.trib_id, 'name': t.name} for t in tribs_qs]
        return JsonResponse({'tribs': tribs})
    except Exception:
        return JsonResponse({'tribs': []})

def pool_boundaries(request):
    """Return all pools with their boundary as a GeoJSON FeatureCollection for client-side spatial lookup."""
    features = []
    for p in Pool.objects.exclude(boundary__isnull=True).values('pool_id', 'name', 'abbrev', 'boundary'):
        features.append({
            'type': 'Feature',
            'geometry': p['boundary'],
            'properties': {'pool_id': p['pool_id'], 'name': p['name'], 'abbrev': p['abbrev']}
        })
    return JsonResponse({'type': 'FeatureCollection', 'features': features})

def basin_boundaries(request):
    """Return all basins with their boundary as a GeoJSON FeatureCollection for client-side spatial lookup."""
    features = []
    for b in Basin.objects.exclude(boundary__isnull=True).values('basin_id', 'name', 'abbrev', 'boundary'):
        features.append({
            'type': 'Feature',
            'geometry': b['boundary'],
            'properties': {'basin_id': b['basin_id'], 'name': b['name'], 'abbrev': b['abbrev']}
        })
    return JsonResponse({'type': 'FeatureCollection', 'features': features})

def trib_boundaries(request):
    """Return tribs with their boundary as a GeoJSON FeatureCollection.

    Accepts optional query parameters to filter server-side before returning:
      basin_id — return only tribs belonging to this basin
      pool_id  — return only tribs belonging to this pool
    Both may be combined. With no parameters the full set is returned (for
    backward-compatibility with other callers such as sample-site-form.html).
    """
    qs = Trib.objects.exclude(boundary__isnull=True)
    basin_id = request.GET.get('basin_id')
    pool_id  = request.GET.get('pool_id')
    if basin_id:
        qs = qs.filter(basin_id=basin_id)
    if pool_id:
        qs = qs.filter(pool_id=pool_id)
    features = []
    for t in qs.values('trib_id', 'name', 'basin_id', 'pool_id', 'boundary'):
        features.append({
            'type': 'Feature',
            'geometry': t['boundary'],
            'properties': {
                'trib_id': t['trib_id'],
                'name': t['name'],
                'basin_id': t['basin_id'],
                'pool_id': t['pool_id'],
            }
        })
    return JsonResponse({'type': 'FeatureCollection', 'features': features})


def huc12_boundaries(request):
    """Return all HUC12 records with their boundary as a GeoJSON FeatureCollection for client-side spatial lookup."""
    features = []
    for h in Huc12.objects.exclude(boundary__isnull=True).values(
        'huc_id', 'huc12', 'huc12_name', 'huc10', 'huc10_name', 'huc8', 'huc8_name', 'boundary'
    ):
        features.append({
            'type': 'Feature',
            'geometry': h['boundary'],
            'properties': {
                'huc_id':     h['huc_id'],
                'huc12':      h['huc12'],
                'huc12_name': h['huc12_name'],
                'huc10':      h['huc10'],
                'huc10_name': h['huc10_name'],
                'huc8':       h['huc8'],
                'huc8_name':  h['huc8_name'],
            }
        })
    return JsonResponse({'type': 'FeatureCollection', 'features': features})

@login_required
def offices_by_agency(request, agency_id):
    """AJAX endpoint: return office list for a given agency."""
    try:
        offices_qs = Office.objects.filter(agency_id=agency_id).order_by('name')
        offices = [{'id': o.office_id, 'name': o.name} for o in offices_qs]
        return JsonResponse({'offices': offices})
    except Exception:
        return JsonResponse({'offices': []})

@login_required
def crews_by_agency(request, agency_id):
    """AJAX endpoint: return crew list for a given agency."""
    try:
        crews_qs = Crew.objects.filter(agency_id=agency_id).order_by('leader')
        crews = [{'id': c.crew_id, 'name': c.leader} for c in crews_qs]
        return JsonResponse({'crews': crews})
    except Exception:
        return JsonResponse({'crews': []})

@login_required
def FishingSites_HP_by_basin(request, basin_id):
    """AJAX endpoint: return fishing sites for a given basin."""
    try:
        fishing_sites_qs = FishingSite_HP.objects.filter(basin_id=basin_id).order_by('name')
        fishing_sites = [{'id': fs.site_id, 'name': fs.name} for fs in fishing_sites_qs]
        return JsonResponse({'fishing_sites': fishing_sites})
    except Exception:
        return JsonResponse({'fishing_sites': []})

@login_required
def SampleSite_by_basin(request, basin_id):
    """AJAX endpoint: return sample sites for a given basin."""
    try:
        sample_sites_qs = SampleSite.objects.filter(basin_id=basin_id).order_by('river_mi')
        sample_sites = [{'id': ss.site_id, 'name': ss.name} for ss in sample_sites_qs]
        return JsonResponse({'sample_sites': sample_sites})
    except Exception:
        return JsonResponse({'sample_sites': []})

@login_required
def SampleSite_by_pool(request, pool_id):
    """AJAX endpoint: return sample sites for a given pool."""
    try:
        sample_sites_qs = SampleSite.objects.filter(pool_id=pool_id).order_by('river_mi')
        sample_sites = [{'id': ss.site_id, 'name': ss.name} for ss in sample_sites_qs]
        return JsonResponse({'sample_sites': sample_sites})
    except Exception:
        return JsonResponse({'sample_sites': []})

@login_required
def SampleSite_by_basin_and_pool(request, basin_id, pool_id):
    """AJAX endpoint: return sample sites for a given basin and pool."""
    try:
        sample_sites_qs = SampleSite.objects.filter(basin_id=basin_id, pool_id=pool_id).order_by('river_mi')
        sample_sites = [{'id': ss.site_id, 'name': ss.name} for ss in sample_sites_qs]
        return JsonResponse({'sample_sites': sample_sites})
    except Exception:
        return JsonResponse({'sample_sites': []})

@login_required
def sample_sites_lookup(request):
    """AJAX endpoint: Select2 lookup for sample sites by name or code."""
    term = (request.GET.get('q') or '').strip()
    qs = SampleSite.objects.all()
    if term:
        qs = qs.filter(Q(name__icontains=term))
    qs = qs.order_by('name')[:25]
    results = []
    for site in qs:
        label = site.name
        if getattr(site, 'pool', None):
            label = f"{site.name} [{site.pool.abbrev}]"
        results.append({'id': site.site_id, 'text': label})
    return JsonResponse({'results': results})


@login_required
def sample_sites_geojson(request):
    """GeoJSON FeatureCollection of all SampleSite records that have coordinates."""
    qs = (
        SampleSite.objects
        .select_related('pool', 'basin')
        .exclude(latitude__isnull=True)
        .exclude(longitude__isnull=True)
        .order_by('pool__pool_id', 'river_mi')
    )
    features = []
    for site in qs:
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [float(site.longitude), float(site.latitude)],
            },
            'properties': {
                'id': site.site_id,
                'name': site.name,
                'river_mi': float(site.river_mi) if site.river_mi is not None else None,
                'pool': site.pool.name if site.pool else '',
                'pool_abbrev': site.pool.abbrev if site.pool else '',
                'basin': site.basin.name if site.basin else '',
            },
        })
    return JsonResponse({'type': 'FeatureCollection', 'features': features})


@login_required
def cf_sites_geojson(request):
    """GeoJSON FeatureCollection of all FishingSite_CF records."""
    qs = (
        FishingSite_CF.objects
        .select_related('pool', 'basin')
        .order_by('pool__pool_id', 'river_mi')
    )
    features = []
    for site in qs:
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [float(site.longitude), float(site.latitude)],
            },
            'properties': {
                'id': site.site_id,
                'name': site.name,
                'site_code': site.site_code or '',
                'river_mi': float(site.river_mi) if site.river_mi is not None else None,
                'pool': site.pool.name if site.pool else '',
                'pool_abbrev': site.pool.abbrev if site.pool else '',
                'basin': site.basin.name if site.basin else '',
            },
        })
    return JsonResponse({'type': 'FeatureCollection', 'features': features})


@login_required
def hp_sites_geojson(request):
    """GeoJSON FeatureCollection of all FishingSite_HP records."""
    qs = (
        FishingSite_HP.objects
        .select_related('pool', 'basin')
        .order_by('basin__name', 'river_mi')
    )
    features = []
    for site in qs:
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [float(site.longitude), float(site.latitude)],
            },
            'properties': {
                'id': site.site_id,
                'name': site.name,
                'river_mi': float(site.river_mi) if site.river_mi is not None else None,
                'pool': site.pool.name if site.pool else '',
                'pool_abbrev': site.pool.abbrev if site.pool else '',
                'basin': site.basin.name if site.basin else '',
            },
        })
    return JsonResponse({'type': 'FeatureCollection', 'features': features})


@login_required
def ic_catch_count_by_event(request, event_id=None):
    """AJAX endpoint: return existing IcCatch record count for a given IcEvent."""
    if not request.user.has_perm('kiccd_app.add_iccatch'):
        return JsonResponse({'detail': 'Permission denied.'}, status=403)

    requested_event_id = event_id if event_id is not None else request.GET.get('event_id')
    try:
        resolved_event_id = int(requested_event_id)
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'Invalid event_id.'}, status=400)

    record_count = IcCatch.objects.filter(event_id=resolved_event_id).count()
    return JsonResponse({'event_id': resolved_event_id, 'record_count': record_count})


@login_required
def ichp_event_search(request):
    """AJAX endpoint: search IchpEvent records for Select2 autocomplete."""
    if not request.user.has_perm('kiccd_app.add_ichpcatch'):
        return JsonResponse({'results': []}, status=403)

    term = request.GET.get('term', '').strip()

    qs = IchpEvent.objects.select_related('fisher').order_by('-ichp_date', 'fisher__lookup', 'net_haul')
    if term:
        qs = qs.filter(
            Q(ichp_date__icontains=term) |
            Q(fisher__lookup__icontains=term) |
            Q(fisher__last_name__icontains=term) |
            Q(fisher__first_name__icontains=term)
        )

    results = [
        {'id': e.event_id, 'text': str(e)}
        for e in qs[:50]
    ]
    return JsonResponse({'results': results, 'pagination': {'more': False}})


@login_required
def ichp_catch_count_by_event(request, event_id=None):
    """AJAX endpoint: return existing IchpCatch record count for a given IchpEvent."""
    if not request.user.has_perm('kiccd_app.add_ichpcatch'):
        return JsonResponse({'detail': 'Permission denied.'}, status=403)

    requested_event_id = event_id if event_id is not None else request.GET.get('event_id')
    try:
        resolved_event_id = int(requested_event_id)
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'Invalid event_id.'}, status=400)

    record_count = IchpCatch.objects.filter(event_id=resolved_event_id).count()
    return JsonResponse({'event_id': resolved_event_id, 'record_count': record_count})


@login_required
def ra_catch_count_by_event(request, event_id=None):
    """AJAX endpoint: return existing RaCatch record count for a given RaEvent."""
    if not request.user.has_perm('kiccd_app.add_racatch'):
        return JsonResponse({'detail': 'Permission denied.'}, status=403)

    requested_event_id = event_id if event_id is not None else request.GET.get('event_id')
    try:
        resolved_event_id = int(requested_event_id)
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'Invalid event_id.'}, status=400)

    record_count = RaCatch.objects.filter(event_id=resolved_event_id).count()
    return JsonResponse({'event_id': resolved_event_id, 'record_count': record_count})


@login_required
def cf_catch_count_by_event(request, event_id=None):
    """AJAX endpoint: return existing CfCatch record count for a given CfEvent."""
    if not request.user.has_perm('kiccd_app.add_cfcatch'):
        return JsonResponse({'detail': 'Permission denied.'}, status=403)

    requested_event_id = event_id if event_id is not None else request.GET.get('event_id')
    try:
        resolved_event_id = int(requested_event_id)
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'Invalid event_id.'}, status=400)

    record_count = CfCatch.objects.filter(event_id=resolved_event_id).count()
    return JsonResponse({'event_id': resolved_event_id, 'record_count': record_count})


@login_required
def ichp_monthly_weight_chart(request):
    """Render a filtered ICHP monthly total reported weight (lb) column chart grouped by year."""
    if not request.user.has_perm('kiccd_app.view_ichpcatch'):
        return render(request, 'kiccd_app/403.html', status=403)

    month_sequence = list(range(1, 13))
    month_labels = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec',
    }

    def _parse_int(param):
        raw = (request.GET.get(param) or '').strip()
        try:
            return int(raw) if raw else None
        except ValueError:
            return None

    selected_year = _parse_int('year')
    selected_basin = _parse_int('basin')
    selected_pool = _parse_int('pool')
    selected_site = _parse_int('site')
    selected_fisher = _parse_int('fisher')
    # 'targeted' is a sentinel meaning "all targeted IC species combined"
    _raw_species = (request.GET.get('species') or '').strip()
    selected_species_targeted = (_raw_species == 'targeted')
    selected_species = None if selected_species_targeted else _parse_int('species')
    selected_observed = (request.GET.get('observed') or '').strip()

    if selected_observed == 'only':
        _observed_q = {'event__observed': True}
        _event_observed_q = {'ichpevent__observed': True}
        _catch_event_observed_q = {'ichpcatch__event__observed': True}
    elif selected_observed == 'all':
        _observed_q = {}
        _event_observed_q = {}
        _catch_event_observed_q = {}
    else:
        selected_observed = 'exclude'
        _observed_q = {'event__observed': False}
        _event_observed_q = {'ichpevent__observed': False}
        _catch_event_observed_q = {'ichpcatch__event__observed': False}

    base_qs = IchpCatch.objects.filter(
        reported_weight_lb__isnull=False,
        **_observed_q,
    ).select_related('event__datez', 'event__basin', 'event__site', 'event__fisher')

    # Populate filter dropdowns from the unrestricted base set
    year_options = list(
        base_qs
        .values_list('event__datez__cal_year', flat=True)
        .distinct()
        .order_by('-event__datez__cal_year')
    )
    basin_options = (
        Basin.objects
        .filter(ichpevent__ichpcatch__reported_weight_lb__isnull=False, **_event_observed_q)
        .distinct()
        .order_by('name')
    )
    pool_options = (
        Pool.objects
        .filter(fishingsite_hp__ichpevent__ichpcatch__reported_weight_lb__isnull=False,
                **{'fishingsite_hp__' + k: v for k, v in _event_observed_q.items()})
        .distinct()
        .order_by('pool_id')
    )
    site_options = (
        FishingSite_HP.objects
        .filter(ichpevent__ichpcatch__reported_weight_lb__isnull=False, **_event_observed_q)
        .select_related('pool', 'basin')
        .distinct()
        .order_by('name')
    )
    fisher_options = (
        Fisher.objects
        .filter(ichpevent__ichpcatch__reported_weight_lb__isnull=False, **_event_observed_q)
        .distinct()
        .order_by('last_name', 'first_name')
    )
    species_options = (
        FishSpecies.objects
        .filter(ichpcatch__reported_weight_lb__isnull=False, **_catch_event_observed_q)
        .exclude(spp_id=0)
        .exclude(name__iexact='No Fish')
        .distinct()
        .order_by('-ranked', 'name')
    )

    form_submitted = bool(request.GET)

    categories = [month_labels[m] for m in month_sequence]
    series = []
    table_rows = []

    if form_submitted:
        # Apply filters
        filtered_qs = base_qs
        if selected_year:
            filtered_qs = filtered_qs.filter(event__datez__cal_year=selected_year)
        if selected_basin:
            filtered_qs = filtered_qs.filter(event__basin_id=selected_basin)
        if selected_pool:
            filtered_qs = filtered_qs.filter(event__site__pool_id=selected_pool)
        if selected_site:
            filtered_qs = filtered_qs.filter(event__site_id=selected_site)
        if selected_fisher:
            filtered_qs = filtered_qs.filter(event__fisher_id=selected_fisher)
        if selected_species_targeted:
            filtered_qs = filtered_qs.filter(species__targeted=True)
        elif selected_species:
            filtered_qs = filtered_qs.filter(species_id=selected_species)

        rows = (
            filtered_qs
            .values('event__datez__cal_year', 'event__datez__ic_month1')
            .annotate(total_weight=Coalesce(
                Sum('reported_weight_lb'),
                Value(Decimal('0.0')),
                output_field=DecimalField(),
            ))
            .order_by('event__datez__cal_year', 'event__datez__ic_month1')
        )

        totals_by_year = {}
        for row in rows:
            year = row['event__datez__cal_year']
            month = row['event__datez__ic_month1']
            weight = float(row['total_weight'] or 0)
            totals_by_year.setdefault(year, {})[month] = weight

        for year in sorted(totals_by_year):
            data = []
            for month in month_sequence:
                data.append(round(totals_by_year[year].get(month, 0), 1))
            series.append({'name': str(year), 'data': data})

        # Build table rows: one row per (year, month) that has data
        for year in sorted(totals_by_year):
            for month in month_sequence:
                weight = totals_by_year[year].get(month)
                if weight is not None and weight > 0:
                    table_rows.append({
                        'year': year,
                        'month': month_labels[month],
                        'total_weight_lb': round(weight, 1),
                    })

    has_data = bool(series)

    context = {
        'year_options': year_options,
        'basin_options': basin_options,
        'pool_options': pool_options,
        'site_options': site_options,
        'fisher_options': fisher_options,
        'species_options': species_options,
        'selected_year': selected_year,
        'selected_basin': selected_basin,
        'selected_pool': selected_pool,
        'selected_site': selected_site,
        'selected_fisher': selected_fisher,
        'selected_species': 'targeted' if selected_species_targeted else selected_species,
        'selected_observed': selected_observed,
        'chart_data': {'categories': categories, 'series': series},
        'table_rows': table_rows,
        'has_data': has_data,
        'form_submitted': form_submitted,
    }
    return render(request, 'kiccd_app/pages/ichp-monthly-weight.html', context)


def trib_sites_geojson(request):
    """GeoJSON FeatureCollection of all Trib records that have coordinates."""
    qs = (
        Trib.objects
        .select_related('pool', 'basin')
        .exclude(lat__isnull=True)
        .exclude(lon__isnull=True)
        .order_by('pool__pool_id', 'name')
    )
    features = []
    for trib in qs:
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [float(trib.lon), float(trib.lat)],
            },
            'properties': {
                'id': trib.trib_id,
                'name': trib.name,
                'river_mi': float(trib.rm) if trib.rm is not None else None,
                'pool': trib.pool.name if trib.pool else '',
                'pool_abbrev': trib.pool.abbrev if trib.pool else '',
                'basin': trib.basin.name if trib.basin else '',
            },
        })
    return JsonResponse({'type': 'FeatureCollection', 'features': features})
