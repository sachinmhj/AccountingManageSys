/**
 * BS Date Picker with AD<->BS two-way sync
 * Covers BS 2050-2090
 */
(function () {
    const BS_DATA = {
        2050:[30,32,31,32,31,30,30,30,29,30,29,31],2051:[31,31,32,31,31,31,30,29,30,29,30,30],
        2052:[31,31,32,32,31,30,30,29,30,29,30,30],2053:[31,32,31,32,31,30,30,30,29,29,30,31],
        2054:[30,32,31,32,31,30,30,30,29,30,29,31],2055:[31,31,32,31,31,32,30,29,30,29,30,30],
        2056:[31,32,31,32,31,30,30,29,30,29,30,30],2057:[31,32,31,32,31,30,30,30,29,29,30,31],
        2058:[30,32,31,32,31,30,30,30,29,30,29,31],2059:[31,31,32,31,31,31,30,29,30,29,30,30],
        2060:[31,31,32,32,31,30,30,29,30,29,30,30],2061:[31,32,31,32,31,30,30,30,29,29,30,31],
        2062:[30,32,31,32,31,30,30,30,29,30,29,31],2063:[31,31,32,31,31,32,30,29,30,29,30,30],
        2064:[31,32,31,32,31,30,30,29,30,29,30,30],2065:[31,32,31,32,31,30,30,30,29,29,30,31],
        2066:[31,31,31,32,31,31,30,29,30,29,30,30],2067:[31,31,32,31,31,31,30,29,30,29,30,30],
        2068:[31,31,32,32,31,30,30,29,30,29,30,30],2069:[31,32,31,32,31,30,30,30,29,29,30,31],
        2070:[30,32,31,32,31,30,30,30,29,30,29,31],2071:[31,31,32,31,31,31,30,29,30,29,30,30],
        2072:[31,31,32,32,31,30,30,29,30,29,30,30],2073:[31,32,31,32,31,30,30,30,29,29,30,31],
        2074:[30,32,31,32,31,30,30,30,29,30,29,31],2075:[31,31,32,31,31,31,30,29,30,29,30,30],
        2076:[31,31,32,32,31,30,30,29,30,29,30,30],2077:[31,32,31,32,31,30,30,30,29,29,30,31],
        2078:[31,31,31,32,31,31,29,30,30,29,29,31],2079:[31,31,32,31,31,31,30,29,30,29,30,30],
        2080:[31,31,32,32,31,30,30,29,30,29,30,30],2081:[31,32,31,32,31,30,30,30,29,29,30,31],
        2082:[30,32,31,32,31,30,30,30,29,30,29,31],2083:[31,31,32,31,31,31,30,29,30,29,30,30],
        2084:[31,31,32,32,31,30,30,29,30,29,30,30],2085:[31,32,31,32,31,30,30,30,29,29,30,31],
        2086:[30,32,31,32,31,30,30,30,29,30,29,31],2087:[31,31,32,31,31,31,30,29,30,29,30,30],
        2088:[31,31,32,32,31,30,30,29,30,29,30,30],2089:[31,32,31,32,31,30,30,30,29,29,30,31],
        2090:[30,32,31,32,31,30,30,30,29,30,29,31]
    };
    const BS_START = 2050;
    const AD_REF   = new Date(1993, 3, 14); // BS 2050/01/01 = AD 1993/04/14

    const MONTHS = ['Baisakh','Jestha','Ashadh','Shrawan','Bhadra','Ashwin',
                    'Kartik','Mangsir','Poush','Magh','Falgun','Chaitra'];
    const DAYS   = ['Su','Mo','Tu','We','Th','Fr','Sa'];

    function pad(n){ return String(n).padStart(2,'0'); }

    function adToBS(adDate) {
        let diff = Math.round((adDate - AD_REF) / 86400000);
        let y = BS_START, m = 1, d = 1;
        while (diff > 0 && BS_DATA[y]) {
            let dim = BS_DATA[y][m-1];
            if (diff < dim) { d += diff; diff = 0; }
            else { diff -= dim; if (++m > 12){ m=1; y++; } }
        }
        return {year:y, month:m, day:d};
    }

    function bsToAD(y, m, d) {
        let days = 0;
        for (let iy = BS_START; iy < y; iy++) {
            if (!BS_DATA[iy]) return null;
            BS_DATA[iy].forEach(x => days += x);
        }
        for (let im = 1; im < m; im++) days += (BS_DATA[y]||[])[im-1]||0;
        days += d - 1;
        let dt = new Date(AD_REF);
        dt.setDate(dt.getDate() + days);
        return dt;
    }

    function fmtAD(d){ return d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate()); }
    function fmtBS(bs){ return bs.year+'-'+pad(bs.month)+'-'+pad(bs.day); }

    /* ── Calendar popup ───────────────────────────────────────────── */
    function buildPopup(initYear, initMonth, initDay, onSelect) {
        let vy = initYear, vm = initMonth;

        const popup = document.createElement('div');
        popup.className = 'bs-datepicker-popup';
        popup.style.cssText = [
            'position:fixed',
            'z-index:999999',
            'width:260px',
            'background:#fff',
            'border:1px solid #cbd5e1',
            'border-radius:10px',
            'box-shadow:0 12px 36px rgba(0,0,0,.22)',
            'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif',
            'font-size:13px',
            'overflow:hidden'
        ].join(';');

        function render() {
            const dim = (BS_DATA[vy] || [])[vm - 1] || 30;
            const firstAD = bsToAD(vy, vm, 1);
            const dow = firstAD ? firstAD.getDay() : 0;

            let dayCells = '';
            for (let i = 0; i < dow; i++) dayCells += '<div></div>';
            for (let d = 1; d <= dim; d++) {
                const sel = (d === initDay && vm === initMonth && vy === initYear);
                dayCells += `<div class="bsd" data-d="${d}" style="padding:5px 2px;text-align:center;border-radius:5px;cursor:pointer;`
                    + (sel ? 'background:#2563eb;color:#fff;font-weight:700;' : 'color:#1e293b;')
                    + '">' + d + '</div>';
            }

            popup.innerHTML = `
<div style="background:#2563eb;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:10px 14px;">
  <button type="button" class="bsp" data-dir="-1" style="background:none;border:none;color:#fff;font-size:20px;cursor:pointer;line-height:1;">&#8249;</button>
  <div style="font-weight:600;font-size:14px;">${MONTHS[vm - 1]} ${vy}</div>
  <button type="button" class="bsp" data-dir="1"  style="background:none;border:none;color:#fff;font-size:20px;cursor:pointer;line-height:1;">&#8250;</button>
</div>
<div style="padding:8px 10px;">
  <div style="display:grid;grid-template-columns:repeat(7,1fr);margin-bottom:4px;">
    ${DAYS.map(d => `<div style="text-align:center;font-size:11px;color:#94a3b8;font-weight:600;padding:3px 0;">${d}</div>`).join('')}
  </div>
  <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:1px;">${dayCells}</div>
</div>
<div style="padding:6px 12px 8px;font-size:11px;color:#94a3b8;border-top:1px solid #f1f5f9;display:flex;justify-content:space-between;">
  <span>BS ${vy}-${pad(vm)}</span>
  <span>${firstAD ? firstAD.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : ''} (AD)</span>
</div>`;

            popup.querySelectorAll('.bsp').forEach(btn => {
                btn.addEventListener('click', e => {
                    e.stopPropagation();
                    vm += parseInt(btn.dataset.dir);
                    if (vm < 1) { vm = 12; vy--; }
                    if (vm > 12) { vm = 1; vy++; }
                    render();
                });
            });
            popup.querySelectorAll('.bsd').forEach(cell => {
                cell.addEventListener('mouseenter', () => { if (!cell.style.background) cell.style.background = '#eff6ff'; });
                cell.addEventListener('mouseleave', () => { if (cell.style.background === 'rgb(239, 246, 255)') cell.style.background = ''; });
                cell.addEventListener('click', e => {
                    e.stopPropagation();
                    onSelect(vy, vm, parseInt(cell.dataset.d));
                });
            });
        }

        render();

        popup.addEventListener('click', e => e.stopPropagation());
        return popup;
    }

    /* ── Public API ───────────────────────────────────────────────── */
    window.adToBS = adToBS;
    window.bsToAD = bsToAD;
    window.fmtBS = fmtBS;
    window.fmtAD = fmtAD;

    window.initBSPicker = function (bsId, onChangeCallback) {
        const bsInput = document.getElementById(bsId);
        if (!bsInput) return;

        bsInput.readOnly = true;
        bsInput.style.cssText += ';cursor:pointer;background:#fffbf0;border-color:#f59e0b;';
        if (!bsInput.getAttribute('placeholder')) {
            bsInput.setAttribute('placeholder', '📅 Pick BS date');
        }

        let picker = null;

        function closePicker() { if (picker) { picker.remove(); picker = null; } }

        function openPicker(e) {
            if (e) e.stopPropagation();
            if (picker) { closePicker(); return; }

            let selBS = null;
            if (bsInput.value) {
                const p = bsInput.value.split('-').map(Number);
                if (p.length === 3 && !isNaN(p[0])) {
                    selBS = { year: p[0], month: p[1], day: p[2] };
                }
            }
            let sbs = selBS || adToBS(new Date());

            picker = buildPopup(sbs.year, sbs.month, sbs.day, function (y, m, d) {
                bsInput.value = fmtBS({ year: y, month: m, day: d });
                if (typeof onChangeCallback === 'function') {
                    onChangeCallback(bsInput.value);
                } else {
                    bsInput.dispatchEvent(new Event('change'));
                }
                closePicker();
            });

            const rect = bsInput.getBoundingClientRect();
            picker.style.position = 'fixed';
            picker.style.top = (rect.bottom + 4) + 'px';
            picker.style.left = rect.left + 'px';
            picker.style.zIndex = '999999';

            document.body.appendChild(picker);
        }

        bsInput.addEventListener('click', openPicker);

        const parentRow = bsInput.closest('.date-row') || bsInput.parentElement;
        if (parentRow) {
            parentRow.addEventListener('click', openPicker);
            const labelSpan = parentRow.querySelector('.date-label, .bs-label');
            if (labelSpan) labelSpan.style.pointerEvents = 'none';
        }

        document.addEventListener('click', closePicker, false);
    };

    window.initDualDate = function (adId, bsId) {
        const adInput = document.getElementById(adId);
        const bsInput = document.getElementById(bsId);
        if (!adInput || !bsInput) return;

        bsInput.readOnly = true;
        bsInput.style.cssText += ';cursor:pointer;background:#fffbf0;border-color:#f59e0b;';
        if (!bsInput.getAttribute('placeholder')) {
            bsInput.setAttribute('placeholder', '📅 Click to pick BS date');
        }

        const parentRow = bsInput.closest('.date-row') || bsInput.parentElement;

        let picker = null;
        let selBS = null;

        if (adInput.value) {
            const p = adInput.value.split('-').map(Number);
            if (p.length === 3 && !isNaN(p[0]) && !isNaN(p[1]) && !isNaN(p[2])) {
                selBS = adToBS(new Date(p[0], p[1] - 1, p[2]));
                bsInput.value = fmtBS(selBS);
            }
        }

        function closePicker() { if (picker) { picker.remove(); picker = null; } }

        function openPicker(e) {
            if (e) e.stopPropagation();
            if (picker) { closePicker(); return; }

            let sbs = selBS || adToBS(new Date());
            if (adInput.value) {
                const p = adInput.value.split('-').map(Number);
                if (p.length === 3 && !isNaN(p[0]) && !isNaN(p[1]) && !isNaN(p[2])) {
                    sbs = adToBS(new Date(p[0], p[1] - 1, p[2]));
                }
            }

            picker = buildPopup(sbs.year, sbs.month, sbs.day, function (y, m, d) {
                selBS = { year: y, month: m, day: d };
                bsInput.value = fmtBS(selBS);
                const ad = bsToAD(y, m, d);
                if (ad) {
                    adInput.value = fmtAD(ad);
                    adInput.dispatchEvent(new Event('change'));
                    adInput.dispatchEvent(new Event('input'));
                }
                closePicker();
            });

            const rect = bsInput.getBoundingClientRect();
            picker.style.position = 'fixed';
            picker.style.top = (rect.bottom + 4) + 'px';
            picker.style.left = rect.left + 'px';
            picker.style.zIndex = '999999';

            document.body.appendChild(picker);
        }

        bsInput.addEventListener('click', openPicker);

        if (parentRow) {
            parentRow.addEventListener('click', openPicker);
            const labelSpan = parentRow.querySelector('.date-label, .bs-label');
            if (labelSpan) labelSpan.style.pointerEvents = 'none';
        }

        function syncAdToBs() {
            if (!adInput.value) { bsInput.value = ''; selBS = null; return; }
            const p = adInput.value.split('-').map(Number);
            if (p.length === 3 && !isNaN(p[0]) && !isNaN(p[1]) && !isNaN(p[2])) {
                selBS = adToBS(new Date(p[0], p[1] - 1, p[2]));
                bsInput.value = fmtBS(selBS);
            }
        }

        adInput.addEventListener('change', syncAdToBs);
        adInput.addEventListener('input', syncAdToBs);

        document.addEventListener('click', closePicker, false);
    };
})();
