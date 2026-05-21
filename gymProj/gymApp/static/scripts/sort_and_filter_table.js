function sortTable(columnIndex, tableId) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.rows);

    // Determine sort direction (ascending or descending)
    const isAscending = table.dataset.sortDirection !== 'asc';
    table.dataset.sortDirection = isAscending ? 'asc' : 'desc';

    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();

        // Check if values are numbers
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        } else {
            return isAscending ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
        }
    });

    // Re-append sorted rows to tbody
    rows.forEach(row => tbody.appendChild(row));
    applyBootstrapStriping(tableId);
}

function setupSortableHeaders(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const sortableHeaders = table.querySelectorAll('thead th.sortable-th');
    sortableHeaders.forEach(th => {
        if (th.dataset.sortBound === '1') return;
        th.dataset.sortBound = '1';

        const columnIndex = th.cellIndex;
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => sortTable(columnIndex, tableId));
    });
}

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

function applyBootstrapStriping(tableId) {
    console.log('Applying bootstrap striping');
  const rows = document.querySelectorAll(`#${tableId} tbody tr`);

  let visibleIndex = 0;

  rows.forEach(row => {
    row.classList.remove('table-secondary');

    if (row.style.display === 'none') return;

    if (visibleIndex % 2 === 1) {
      row.classList.add('table-secondary');
    }

    visibleIndex++;
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

        let matchesFilters = true;

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
    applyBootstrapStriping(tableId);
    
}

const setupFiltersAndSearch = (tableId, filterIdToTd, searchableColumnClasses, searchInputId) => {
    const searchInput = document.getElementById(searchInputId);
    const filterIdToTdMap = new Map(filterIdToTd);

    setupSortableHeaders(tableId);

    const applyFinalFilters = () => {
        applyFilters(tableId, searchableColumnClasses, filterIdToTdMap);
    }

    for (const filterId of filterIdToTdMap.keys()) {
        values = Array.from(document.querySelectorAll('#' + tableId + ' .' + filterIdToTdMap.get(filterId))).map(td => td.textContent.trim());
        populateSelect(document.getElementById(filterId), values);
        document.getElementById(filterId).addEventListener('change', applyFinalFilters);
    };

    searchInput.addEventListener('input', applyFinalFilters);
    applyFinalFilters();
};

