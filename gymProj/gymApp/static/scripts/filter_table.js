function normalize(s) {
    return (s || '').toString().toLowerCase().trim();
}

function populateSelect(selectEl, values) {
    const uniq = Array.from(new Set(values.filter(Boolean))).sort();
    uniq.forEach(v => {
        const opt = document.createElement('option');
        opt.value = v;
        opt.textContent = v;
        selectEl.appendChild(opt);
    });
}


function applyFilters(tableId, searchableColumnClasses, filterIdToTd) {
    const searchVal = normalize(document.getElementById('searchInput').value);
    const filterIdToSelectedValue = new Map();
    filterIdToTd.forEach((tdClass, filterId) => {
        filterIdToSelectedValue.set(filterId, normalize(document.getElementById(filterId).value));
    });

    const rows = document.querySelectorAll(`#${tableId} tbody tr`);

    rows.forEach(row => {
        let matchesSearch = !searchVal;
        for (const colClass of searchableColumnClasses) {
            const cellText = normalize(row.querySelector(`.${colClass}`)?.textContent);
            if (cellText.includes(searchVal)) {
                matchesSearch = true;
                break;
            }
        }

        let matchesFilters  = true;

        filterIdToTd.forEach((tdClass, filterId) => {
            const selectedValue = filterIdToSelectedValue.get(filterId);
            const cellText = normalize(row.querySelector(`.${tdClass}`)?.textContent);
            if (selectedValue && cellText !== selectedValue) {
                matchesFilters = false;
            }
        });

        const show = matchesSearch && matchesFilters;
        row.style.display = show ? '' : 'none';

    })
}
