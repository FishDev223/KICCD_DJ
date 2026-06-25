/**
 * Module: Scripts for Crew Form
 */

document.addEventListener('DOMContentLoaded', function(){
    const agencySelect = document.getElementById('id_agency');
    const officeSelect = document.getElementById('id_office');
    if (!agencySelect || !officeSelect) return;

    // URL with placeholder 0; we'll replace the '0' segment with the selected id
    const baseUrl = "{% url 'kiccd_app:api_offices_by_agency' 0 %}";
    function buildUrl(id){
        return baseUrl.replace('/0/','/'+id+'/');
    }

    function clearOptions(){
        officeSelect.innerHTML = '';
        const opt = document.createElement('option');
        opt.value = '';
        opt.text = '--- Select Office ---';
        officeSelect.appendChild(opt);
        officeSelect.disabled = true;
    }

    agencySelect.addEventListener('change', function(){
        const agencyId = this.value;
        if (!agencyId){
            clearOptions();
            return;
        }
        fetch(buildUrl(agencyId))
            .then(r => r.json())
            .then(data => {
                officeSelect.innerHTML = '';
                const placeholder = document.createElement('option');
                placeholder.value = '';
                placeholder.text = '--- Select Office ---';
                officeSelect.appendChild(placeholder);
                (data.offices || []).forEach(o => {
                    const opt = document.createElement('option');
                    opt.value = o.id;
                    opt.text = o.name;
                    officeSelect.appendChild(opt);
                });
                officeSelect.disabled = false;
            })
            .catch(() => clearOptions());
    });

    // populate on load if an agency is pre-selected
    if (agencySelect.value) {
        agencySelect.dispatchEvent(new Event('change'));
    }
});