addEventListener("DOMContentLoaded", (event) => {
    const sidebar = document.getElementById('sidebar')
    const btn = document.getElementById('toggleBtn')

    btn.addEventListener('click', () => {
        if (sidebar.classList.contains('hidden')) {
            sidebar.classList.remove('hidden');
            sidebar.classList.add('shown');
        }
        else {
            sidebar.classList.remove('shown');
            sidebar.classList.add('hidden');
        }
    });
});
